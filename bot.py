from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

API_ID = 37479567
API_HASH = "89fe17e8b2660a56833727a4a0cf3f6e"
BOT_TOKEN = "7994147127:AAFabxygfDzJaCHeu2CHjvAe9y_fTweTogg"
FORCE_CHANNEL = "StudyMaterial079"

app = Client(
    "studybot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Dummy database (baad me expand kar sakta hai)
DATA = {
    "physics notes": "https://yourshortlink.com/physics",
    "math pdf": "https://yourshortlink.com/math"
}

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "👋 **Hello! Welcome to Study Material Bot**\n\n"
        "📝 *Note:*\n"
        "Material ka naam search karo,\n"
        "main tumhe material ka link de dunga.\n\n"
        "⚠️ Name bilkul correct hona chahiye.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_CHANNEL}")]
        ])
    )

@app.on_message(filters.text & ~filters.command)
async def search_material(client, message):

    try:
        member = await client.get_chat_member(FORCE_CHANNEL, message.from_user.id)
    except:
        await message.reply_text(
            "🚫 Pehle channel join karo",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_CHANNEL}")]
            ])
        )
        return

    query = message.text.lower()

    if query in DATA:
        msg = await message.reply_text(
            f"✅ **Material Found**\n\n🔗 {DATA[query]}"
        )
        await asyncio.sleep(300)  # 5 minutes
        await msg.delete()
    else:
        await message.reply_text("❌ Material nahi mila, naam sahi likho")

app.run()
