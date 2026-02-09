import os, asyncio, threading, http.server, socketserver, gspread, json
from oauth2client.service_account import ServiceAccountCredentials
from pyrogram import Client, filters, enums

# --- RENDER FREE TIER PORT BINDING ---
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
        if not creds_json:
            print("Error: GSPREAD_JSON nahi mila!")
            return {}
            
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # IMPORTANT: Yahan apni sheet ka exact naam likhein (Double quotes ke andar)
        sheet = client.open("Aapki_Sheet_Ka_Naam_Yahan_Likho").sheet1 
        
        records = sheet.get_all_records()
        # {Material: Link} format
        return {str(row['Material']).lower().strip(): row['Link'] for row in records}
    except Exception as e:
        print(f"Sheet Error: {e}")
        return {}

# --- BOT SETUP ---
app = Client(
    "factio_bot",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

@app.on_message(filters.command("start"))
async def start(c, m):
    welcome = (
        "🔥 **Welcome to Og Prime Movie Bot!**\n\n"
        "Movie ka naam likh kar bhejein aur link paayein.\n\n"
        "📢 **Note:** Links 5 minute mein delete ho jayenge!"
    )
    await m.reply(welcome, parse_mode=enums.ParseMode.MARKDOWN)

@app.on_message(filters.text & ~filters.command("start"))
async def handle_request(c, m):
    query = m.text.lower().strip()
    data = get_data_from_sheet()
    
    if query in data:
        response = (
            f"✅ **Material Mil Gaya!**\n\n"
            f"🔗 **Link:** {data[query]}\n\n"
            f"⚠️ **Note:** Ye message 5 minute mein delete ho jayega!"
        )
        
        sent = await m.reply(
            response, 
            disable_web_page_preview=True, 
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_to_message_id=m.id
        )
        
        # 5 Minute baad delete
        await asyncio.sleep(300)
        try:
            await sent.delete()
            await m.delete()
        except:
            pass
            
    elif m.chat.type == enums.ChatType.PRIVATE:
        await m.reply("❌ **Maaf kijiyega, ye material nahi mila.**\nSpelling check karein ya Sheet mein add karein.", parse_mode=enums.ParseMode.MARKDOWN)

if __name__ == "__main__":
    app.run()
