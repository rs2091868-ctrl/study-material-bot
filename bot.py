import os, asyncio, threading, http.server, socketserver, gspread, json
from oauth2client.service_account import ServiceAccountCredentials
from pyrogram import Client, filters, enums
from pyrogram.errors import UserNotParticipant

# --- CONFIG ---
CHANNEL_ID = "@hd_cinema_hub_og"  # Aapka channel username
CHANNEL_LINK = "https://t.me/hd_cinema_hub_og"

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
        return True # Error aane par process hone dega takki bot na ruke
    return False

@app.on_message(filters.command("start"))
async def start(c, m):
    await m.reply("😎🔥 **Bot Online!**\n\nMovie ka naam bhejein. ✨\n\n⚠️ File na milne par spelling check Karen!", parse_mode=enums.ParseMode.MARKDOWN)

@app.on_message(filters.text & ~filters.command("start") & filters.private)
async def handle_request(c, m):
    # 1. Join Check
    if not await is_subscribed(c, m):
        await m.reply(
            f"❌ **Access Denied!**\n\nPehle hamara channel join karein tabhi aap link dekh payenge.\n\n🔗 **Join Here:** {CHANNEL_LINK}\n\nJoin karne ke baad fir se message bhejein.",
            disable_web_page_preview=True
        )
        return

    # 2. Process Request
    query = m.text.lower().strip()
    data = get_data_from_sheet()
    
    if query in data:
        mat_name, link = data[query]
        sent = await m.reply(
            f"✅ **Material Found!**\n\n🎬 **Name:** {mat_name}\n🔗 **Link:** {link}\n\n⚠️ Note: 4 min mein link delete ho jayega!",
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        
        # Auto-delete
        await asyncio.sleep(240)
        try: 
            await sent.delete()
            await m.delete()
        except: 
            pass

if __name__ == "__main__":
    app.run()
