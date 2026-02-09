import os, asyncio, threading, http.server, socketserver, gspread, json
from oauth2client.service_account import ServiceAccountCredentials
from pyrogram import Client, filters, enums

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
        
        # FIX: Hum yahan index 0 use karenge taki tab ka naam jo bhi ho, pehli tab utha le
        sheet = client.open("StudyBotProject").get_worksheet(0)
        
        records = sheet.get_all_records()
        # Debugging ke liye: print(records) Render logs mein dikhega
        return {str(row['Material']).lower().strip(): row['Link'] for row in records}
    except Exception as e:
        print(f"Sheet Error: {e}")
        return {}

# --- BOT SETUP ---
app = Client("factio_bot", api_id=int(os.getenv("API_ID")), api_hash=os.getenv("API_HASH"), bot_token=os.getenv("BOT_TOKEN"))

@app.on_message(filters.command("start"))
async def start(c, m):
    await m.reply("📚 **Bot Online!**\n\nMaterial ka naam bhejein.", parse_mode=enums.ParseMode.MARKDOWN)

@app.on_message(filters.text & ~filters.command("start"))
async def handle_request(c, m):
    query = m.text.lower().strip()
    data = get_data_from_sheet()
    
    if query in data:
        link = data[query]
        sent = await m.reply(
            f"✅ **Material Found!**\n\n🔗 **Link:** {link}\n\n⚠️ Note: 5 min mein delete ho jayega!",
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        await asyncio.sleep(300)
        try: await sent.delete(); await m.delete()
        except: pass
    else:
        # Taki humein pata chale bot kya dhoond raha hai
        await m.reply(f"❌ '{query}' nahi mila. Sheet check karein!", parse_mode=enums.ParseMode.MARKDOWN)

if __name__ == "__main__":
    app.run()
