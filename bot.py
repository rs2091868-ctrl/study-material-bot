import os, asyncio, threading, http.server, socketserver, gspread, json
import difflib
from oauth2client.service_account import ServiceAccountCredentials
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import UserNotParticipant

# --- CONFIG ---
CHANNEL_ID = "@hd_cinema_hub_og"
CHANNEL_LINK = "https://t.me/hd_cinema_hub_og"
BOT_USERNAME = "og_prime_zx_bot"

# --- RENDER PORT BINDING ---
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- GOOGLE SHEETS CONNECTION ---
def get_data_from_sheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_json = os.environ.get("GSPREAD_JSON")
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("StudyBotProject").get_worksheet(0)
        records = sheet.get_all_records()
        return {str(row['Material']).lower().strip(): (row['Material'], row['Link']) for row in records}
    except Exception as e:
        print(f"Sheet Error: {e}")
        return {}

# --- BOT SETUP ---
app = Client("factio_bot", api_id=int(os.getenv("API_ID")), api_hash=os.getenv("API_HASH"), bot_token=os.getenv("BOT_TOKEN"))

async def is_subscribed(c, m):
    try:
        user = await c.get_chat_member(CHANNEL_ID, m.from_user.id)
        if user.status in [enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            return True
    except UserNotParticipant:
        return False
    except Exception as e:
        print(f"Join Check Error: {e}")
        return True 
    return False

@app.on_message(filters.command("start"))
async def start(c, m):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me To Your Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")]
    ])
    await m.reply("😎🔥 **Bot Online!**\n\nMovie ka naam bhejein. ✨\n\n⚠️ File na milne par spelling check Karen!", parse_mode=enums.ParseMode.MARKDOWN, reply_markup=buttons)

# --- CALLBACK HANDLER (Buttons Click) ---
@app.on_callback_query()
async def callback_handler(c, cb: CallbackQuery):
    query = cb.data.lower().strip()
    data = get_data_from_sheet()
    
    if query in data:
        mat_name, link = data[query]
        sent = await cb.message.reply(
            f"✅ **Material Found!**\n\n🎬 **Name:** {mat_name}\n🔗 **Link:** {link}\n\n⚠️ Note: 4 min mein link delete ho jayega!",
            disable_web_page_preview=True
        )
        await cb.answer("Material Sent!") # Notification on top
        
        await asyncio.sleep(240)
        try: 
            await sent.delete()
        except: pass
    else:
        await cb.answer("❌ Error: Material not found in sheet!", show_alert=True)

# --- TEXT MESSAGE HANDLER ---
@app.on_message(filters.text & ~filters.command("start"))
async def handle_request(c, m):
    if m.chat.type == enums.ChatType.PRIVATE:
        if not await is_subscribed(c, m):
            join_button = InlineKeyboardMarkup([[InlineKeyboardButton("📢 Join Channel First", url=CHANNEL_LINK)]])
            await m.reply(f"❌ **Access Denied!**\n\nPehle hamara channel join karein tabhi aap link dekh payenge.", reply_markup=join_button)
            return

    query = m.text.lower().strip()
    data = get_data_from_sheet()
    
    if query in data:
        mat_name, link = data[query]
        sent = await m.reply(
            f"✅ **Material Found!**\n\n🎬 **Name:** {mat_name}\n🔗 **Link:** {link}\n\n⚠️ Note: 4 min mein link delete ho jayega!",
            disable_web_page_preview=True,
            reply_to_message_id=m.id
        )
        await asyncio.sleep(240)
        try: 
            await sent.delete()
            await m.delete()
        except: pass

    else:
        all_materials = list(data.keys())
        matches = difflib.get_close_matches(query, all_materials, n=5, cutoff=0.3)
        
        if matches:
            buttons = []
            for match in matches:
                display_name = data[match][0]
                # Yahan humne callback_data use kiya hai taaki username na aaye
                buttons.append([InlineKeyboardButton(display_name, callback_data=match)])
            
            suggestion_msg = await m.reply(
                "🤔 **Aap ye toh nahi dhoond rahe?**\nNiche diye gaye options mein se select karein:",
                reply_markup=InlineKeyboardMarkup(buttons),
                reply_to_message_id=m.id
            )
            await asyncio.sleep(120)
            try: await suggestion_msg.delete()
            except: pass

if __name__ == "__main__":
    app.run()
