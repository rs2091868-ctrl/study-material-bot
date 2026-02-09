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
        # Render ke Environment Variables se JSON data lena
        creds_json = os.environ.get("GSPREAD_JSON")
        if not creds_json:
            print("Error: GSPREAD_JSON environment variable nahi mila!")
            return {}
            
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Yahan apni Google Sheet ka sahi naam likhein
        sheet = client.open("StudyBotProject").sheet1 
        records = sheet.get_all_records()
        # {Material Name: Link} format mein data convert karna
        return {str(row['Material']).lower().strip(): row['Link'] for row in records}
    except Exception as e:
        print(f"Sheet Error: {e}")
        return {}

# --- BOT INITIALIZATION ---
app = Client(
    "factio_study_bot",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

@app.on_message(filters.command("start"))
async def start(c, m):
    welcome_text = (
        "📚 **Welcome to Study Material Bot!**\n\n"
        "Aap kisi bhi material ka naam likh kar bhejein, main aapko uska link de dunga.\n\n"
        "📢 **Note:** Privacy ke liye links 5 minute baad delete ho jayenge."
    )
    await m.reply(welcome_text, parse_mode=enums.ParseMode.MARKDOWN)

@app.on_message(filters.text & ~filters.command("start"))
async def handle_material_request(c, m):
    query = m.text.lower().strip()
    data = get_data_from_sheet()
    
    if query in data:
        response_text = (
            f"✅ **Material Found!**\n\n"
            f"🔗 **Link:** {data[query]}\n\n"
            f"⚠️ **DHYAN DEIN:** Ye link 5 minute mein delete ho jayegi. Isse pehle save kar lein!"
        )
        
        # Reply to user message
        sent = await m.reply(
            response_text, 
            disable_web_page_preview=True, 
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_to_message_id=m.id
        )
        
        # 5 Minute wait karke delete karna
        await asyncio.sleep(300)
        try:
            await sent.delete()
            await m.delete() # Bot agar admin hai toh user ka message bhi delete karega
        except:
            pass
            
    elif m.chat.type == enums.ChatType.PRIVATE:
        # Groups mein faltu replies se bachne ke liye sirf Private chat mein 'Not Found' dikhayega
        await m.reply("❌ **Maaf kijiyega, ye material nahi mila.**\nSpelling check karein ya Sheet mein add karein.", parse_mode=enums.ParseMode.MARKDOWN)

if __name__ == "__main__":
    app.run()
