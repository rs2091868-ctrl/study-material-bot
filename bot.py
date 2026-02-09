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
        sheet = client.open("StudyBotProject").get_worksheet(0)
        records = sheet.get_all_records()
        # Material name aur link dono return kar raha hai
        return {str(row['Material']).lower().strip(): (row['Material'], row['Link']) for row in records}
    except Exception as e:
        print(f"Sheet Error: {e}")
        return {}

# --- BOT SETUP ---
app = Client("factio_bot", api_id=int(os.getenv("API_ID")), api_hash=os.getenv("API_HASH"), bot_token=os.getenv("BOT_TOKEN"))

@app.on_message(filters.command("start"))
async def start(c, m):
    # Aapka OG Prime wala welcome message
    await m.reply("😎🔥 **Bot Online!**\n\nMy name is OG Prime. Movie ka naam bhejein. ✨ example border❌ Border ✅ pahla akshar capital me hona chahiye file na milne par spelling check Karen ✍️\n\n#factio", parse_mode=enums.ParseMode.MARKDOWN)

@app.on_message(filters.text & ~filters.command("start"))
async def handle_request(c, m):
    query = m.text.lower().strip()
    data = get_data_from_sheet()
    
    # Check karega ki kya material sheet mein hai
    if query in data:
        mat_name, link = data[query]
        # Material ka name aur link saath mein
        sent = await m.reply(
            f"✅ **Material Found!**\n\n🎬 **Name:** {mat_name}\n🔗 **Link:** {link}\n\n⚠️ Note: 4 min mein link delete ho jayega!\n\nlink par click karke download karlein 🍿",
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        
        # 4 minute (240s) baad dono message delete honge
        await asyncio.sleep(240)
        try: 
            await sent.delete()
            await m.delete()
        except: 
            pass
    # ELSE part hata diya hai taki faltu message par bot reply na kare (Group spam control)

if __name__ == "__main__":
    app.run()
