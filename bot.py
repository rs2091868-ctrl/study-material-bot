import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURATION ---
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
# Aapka channel username yahan set hai
CHANNEL_USERNAME = "hd_cinema_zx" 

app = Client("study_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)
sheet = client.open("StudyBotProject").sheet1 

# --- FORCE JOIN CHECK FUNCTION ---
async def is_user_member(user_id):
    try:
        member = await app.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
    except Exception:
        return False
    return False

@app.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    
    # Check if user joined channel
    if not await is_user_member(user_id):
        await message.reply_text(
            f"👋 Namaste {message.from_user.mention}!\n\n"
            "Bot use karne ke liye aapko hamara channel join karna hoga. 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Join Channel 📢", url=f"https://t.me/{CHANNEL_USERNAME}")],
                [InlineKeyboardButton("Check Again ✅", callback_data="check_join")]
            ])
        )
        return

    await message.reply_text("Swagat hai! Ab aap koi bhi material ka naam bhej kar link le sakte hain. #factio")

@app.on_message(filters.text & filters.private)
async def search_link(client, message):
    user_id = message.from_user.id
    
    # Yahan bhi check karega ki user abhi member hai ya nahi
    if not await is_user_member(user_id):
        await message.reply_text("Pehle channel join karein! @hd_cinema_zx")
        return

    query = message.text.lower()
    data = sheet.get_all_records()
    
    for row in data:
        if query in row['Material'].lower():
            await message.reply_text(f"✅ Mil gaya!\n\n📦 **{row['Material']}**\n🔗 Link: {row['Link']}\n\n#facts #shorts #factio")
            return
    
    await message.reply_text("Maaf kijiye, ye material nahi mila. #factio")

app.run()
