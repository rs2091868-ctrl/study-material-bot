from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import os

# ===== ENVIRONMENT VARIABLES =====
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ===== FORCE JOIN CHANNEL (without @) =====
FORCE_CHANNEL = "hd_cinema_zx"

# ===== BOT INIT =====
app = Client(
    "hd_cinema_zx",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ===== MATERIAL DATABASE (LINKS ONLY) =====
DATA = {
    "physics notes": "https://yourshortlink.com/physics",
    "math pdf": "https://yourshortlink.com/math"
}

# ===== /start COMMAND =====
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "🔥 **Welcome to prime Bot**\n\n"
        "✍️ Movie ka naam search karo\n"
        "🔗 Link sirf 5 min ke liye milega\n\n"
        "👇 Pehle channel join karo",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{FORCE_CHANNEL}")]]
        )
    )

# ===== SEARCH HANDLER =====
@app.on_message(filters.text & ~filters.command)
async def search_material(client, message):

    # ---- FORCE JOIN CHECK ----
    try:
        await client.get_chat_member(FORCE_CHANNEL, message.from_user.id)
    except:
        await message.reply_text(
            "❌ Pehle channel join karo",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{FORCE_CHANNEL}")]]
            )
        )
        return

    # ---- SEARCH ----
    query = message.text.lower().strip()

    if query in DATA:
        msg = await message.reply_text(
            f"✅ **Material Found**\n\n🔗 {DATA[query]}"
        )

        # ---- AUTO DELETE AFTER 5 MIN ----
        await asyncio.sleep(300)
        await msg.delete()

    else:
        await message.reply_text("❌ Material nahi mila, naam sahi likho")

# ===== RUN BOT =====
app.run()
