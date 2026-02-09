import os
import asyncio
import threading
import http.server
import socketserver
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ===== RENDER PORT BINDING (MISTAKE FIX) =====
# Ye section Render ke "Port scan timeout" error ko solve karega
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Dummy server running on port {port}")
        httpd.serve_forever()

# Server ko background mein start karein
threading.Thread(target=run_dummy_server, daemon=True).start()

# ===== ENVIRONMENT VARIABLES =====
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ===== BOT INIT =====
app = Client(
    "og_prime_zx_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ===== SETTINGS =====
CHANNEL_USERNAME = "hd_cinema_zx"
AUTO_DELETE_TIME = 300  # 5 minutes

# ===== DATA =====
DATA = {
    "physics notes": "https://unlocktoearn.com/kAvOH",
    "chemistry notes": "https://unlocktoearn.com/G72j8",
    "math pdf": "https://unlocktoearn.com/syQJq"
}

# ===== START COMMAND =====
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply(
        "📚 **Study Material Bot**\n\nMaterial ka naam bhejo aur link pao.\n\n👇 Pehle channel join karo",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")]]
        ),
        parse_mode="markdown"
    )

# ===== TEXT HANDLER =====
@app.on_message(filters.text & ~filters.command("start"))
async def send_material(client, message):
    query = message.text.lower().strip()
    if query in DATA:
        sent = await message.reply(
            f"✅ **Your Material Link:**\n{DATA[query]}",
            disable_web_page_preview=True,
            parse_mode="markdown"
        )
        # Auto-delete logic
        await asyncio.sleep(AUTO_DELETE_TIME)
        try:
            await sent.delete()
            await message.delete()
        except Exception as e:
            print(f"Error deleting message: {e}")
    else:
        await message.reply(
            "❌ **Material nahi mila**\n\n📌 Is tarah likho:\n`physics notes`\n`chemistry notes`\n`math pdf`",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")]]
            ),
            parse_mode="markdown"
        )

# ===== RUN BOT =====
if __name__ == "__main__":
    app.run()
