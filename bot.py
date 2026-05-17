import asyncio
import os
import re
import yt_dlp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# Token va Bot sozlamalari
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# INSTAGRAM BLOKLARIDAN 100% AYLANIB O'TISH UCHUN PROFESSIONAL SOZLAMALAR
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'geo_bypass': True,
    'format': 'best',
    # Instagram bot deb o'ylamasligi uchun haqiqiy brauzer sarlavhalari
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,uz;q=0.8',
        'Connection': 'keep-alive',
    },
    'cookiesfrombrowser': None,  # Serverda xatolik bermasligi uchun
}

def clean_url(url: str) -> str:
    """Instagram linklaridagi ortiqcha parchalarni tozalash"""
    if "instagram.com" in url:
        match = re.search(r'(https?://www\.instagram\.com/(?:p|reel|tv)/[^/\s\?*\\]+)', url)
        if match:
            return match.group(1)
    return url

# === 1. ORIGINAL START BUYRUG'I (MATNLARGA UMUMAN TEGILMADI) ===
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    kb = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="🔄 Botni qayta ishga tushirish")]],
        resize_keyboard=True
    )
    await message.answer(
        "✨ 🚀 *XUSH KELIBSIZ!* 🚀 ✨\n"
        "▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️\n\n"
        "🤖 *Ushbu mukammal va tezkor yuklagich bot* @Obidjon_Musurmonov *tomonidan maxsus tayyorlandi.*\n\n"
        "📥 `Menga faqat Instagram (Reels, Post, TV) havolasini yuboring!`\n"
        "⚡️ _Tizim sizga video va uning audiosini eng yuqori sifatda taqdim etadi._\n\n"
        "▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️",
        reply_markup=kb
    )

# === 2. RESTART TUGMASI ===
@dp.message(F.text == "🔄 Botni qayta ishga tushirish")
async def restart_btn(message: types.Message):
    await start_cmd(message)

# === 3. HAVOLALARNI TUTIB QOLUVCHI ASOSIY QISM ===
@dp.message(lambda msg: msg.text and not msg.text.startswith("/") and any(x in msg.text for x in ["instagram.com", "youtube.com", "youtu.be"]))
async def handle_media(message: types.Message):
    url = clean_url(message.text)
    status_msg = await message.answer("⏳ `So'rov qabul qilindi. Media yuklanmoqda...`", parse_mode="Markdown")
    
    out_filename = f"file_{message.from_user.id}.mp4"
    opts = {**YDL_OPTS, 'outtmpl': out_filename}
    
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        
        if os.path.exists(out_filename):
            # ORIGINAL INLINE TUGMA
            audio_btn = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="🎵 ⬇️ MUSIQASINI YUKLAB OLISH ⬇️ 🎵", callback_data="get_audio")]
            ])
            
            # Aynan sizning skrinshotingizdagi chiroyli caption dizayni
            caption_text = (
                f"⚡️ **Muvaffaqiyatli yuklandi!** ✅\n\n"
                f"🔗 **Havola:** {url}\n\n"
                f"👑 **@Obidjon_Musurmonov tizimi**"
            )
            
            await message.answer_video(
                video=types.FSInputFile(out_filename),
                caption=caption_text,
                parse_mode="Markdown",
                reply_markup=audio_btn
            )
            os.remove(out_filename)
            await status_msg.delete()
        else:
            raise Exception("Fayl serverga yozilmadi")
            
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        await message.answer("❌ **YUKLASHDA XATOLIK YUZ BERDI!**\n\n⚠️ _Havola noto'g'ri, video yopiq yoki o'ta katta bo'lishi mumkin._", parse_mode="Markdown")
        try:
            await status_msg.delete()
        except:
            pass

# === 4. AUDIONI AJRATIB OLIB YUBORISH ===
@dp.callback_query(F.data == "get_audio")
async def handle
