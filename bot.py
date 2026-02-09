import os, asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURATION ---
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = "hd_cinema_zx" 
# Aapka PostImages wala Direct Link niche paste kiya hai
PHOTO_URL = "https://i.postimg.cc/Y0VhDnXv/IMG-20260209-211233.jpg"

app = Client("factio_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)
sheet = client.open("StudyBotProject").sheet1 

async def is_user_member(user_id):
    try:
        member = await app.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except: return False

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    user = message.from_user
    if not await is_user_member(user.id):
        await message.reply_photo(
            photo=PHOTO_URL,
            caption=f"👋 Hello {user.mention}!\n\nBot use karne ke liye aapko hamara channel join karna hoga. 👇",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel 📢", url=f"https://t.me/{CHANNEL_USERNAME}")]])
        )
        return
    await message.reply_text(f"Hello {user.first_name}! 🤗\n\nMy name is OG Prime.\n\nTYPE ANY STUDY NAME AND SEE MAGIC, NAME SHOULD BE CORRECT ✨\n\n#factio")

@app.on_message(filters.text)
async def search_and_delete(client, message):
    # Private chat mein membership check karega
    if message.chat.type == "private":
        if not await is_user_member(message.from_user.id):
            await message.reply_text("Pehle channel join karein! @hd_cinema_zx")
            return

    query = message.text.lower()
    data = sheet.get_all_records()
    found = False
    
    for row in data:
        if query in row['Material'].lower():
            res = await message.reply_text(
                f"✅ **Material Found!**\n\n📦 **Name:** {row['Material']}\n🔗 **Link:** {row['Link']}\n\n⚠️ _Ye message 4 minute mein delete ho jayega!_\n\n#facts #shorts #factio"
            )
            found = True
            # 4 minute (240 seconds) baad delete logic
            await asyncio.sleep(240)
            try:
                await res.delete()
                await message.delete() 
            except: pass # Agar message pehle hi delete ho gaya ho
            return
    
    # Sirf private mein 'not found' bolega taaki group mein spam na ho
    if not found and message.chat.type == "private":
        await message.reply_text("Maaf kijiye, ye naam sahi nahi hai. #factio")

app.run()
