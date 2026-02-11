import os, asyncio, threading, http.server, socketserver, gspread, json, re
from oauth2client.service_account import ServiceAccountCredentials
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

# --- CONFIG ---
CHANNEL_ID = "@hd_cinema_hub_og"
CHANNEL_LINK = "https://t.me/hd_cinema_hub_og"
BOT_USERNAME = "og_prime_zx_bot"

# --- ADULT & BAD WORDS LIST ---
# Yahan aap aur bhi words add kar sakte hain
BAD_WORDS = ["mc", "bc", "sex", "porn", "xnx", "gaali", "chu"] 

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

# Helper function for auto-delete
async def auto_delete(chat_id, message_id, delay=300):
    await asyncio.sleep(delay)
    try:
        await app.delete_messages(chat_id, message_id)
    except:
        pass

# Helper function to check join status
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

# --- NEW FEATURE: MONITOR GROUP MESSAGES ---
@app.on_message(filters.group & filters.text & ~filters.me)
async def group_monitor(c, m):
    # Admin immunity: Admin ke messages check nahi honge
    try:
        member = await c.get_chat_member(m.chat.id, m.from_user.id)
        if member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            return
    except:
        pass

    # 1. Link & Adult Word Filter (Immediate Delete)
    text = m.text.lower()
    has_link = re.search(r'http[s]?://|t\.me|www\.', text)
    has_bad_word = any(word in text for word in BAD_WORDS)

    if has_link or has_bad_word:
        await m.delete()
        return

    # 2. 5 Minute Auto-Delete for Normal Messages
    asyncio.create_task(auto_delete(m.chat.id, m.id, 300))

# --- UPDATED HANDLE REQUEST (Group + Private) ---
@app.on_message(filters.text & ~filters.command("start"))
async def handle_request(c, m):
    if m.chat.type == enums.ChatType.PRIVATE:
        if not await is_subscribed(c, m):
            join_button = InlineKeyboardMarkup([[InlineKeyboardButton("📢 Join Channel First", url=CHANNEL_LINK)]])
            await m.reply(f"❌ **Access Denied!**\n\nPehle hamara channel join karein.", reply_markup=join_button)
            return

    query = m.text.lower().strip()
    data = get_data_from_sheet()
    
    if query in data:
        mat_name, link = data[query]
        sent = await m.reply(
            f"✅ **Material Found!**\n\n🎬 **Name:** {mat_name}\n🔗 **Link:** {link}\n\n⚠️ Note: 5 min mein link delete ho jayega!",
            disable_web_page_preview=True,
            reply_to_message_id=m.id
        )
        
        # 5 minute auto-delete for bot reply
        asyncio.create_task(auto_delete(m.chat.id, sent.id, 300))
        # Message mangne wale ka message bhi delete (agar group hai)
        if m.chat.type != enums.ChatType.PRIVATE:
            asyncio.create_task(auto_delete(m.chat.id, m.id, 300))

if __name__ == "__main__":
    app.run()
