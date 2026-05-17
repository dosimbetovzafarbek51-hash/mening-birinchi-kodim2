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

# INSTAGRAM BLOKLARIDAN AYLANIB O'TISH UCHUN SOZLAMALAR
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'geo_bypass': True,
    'format': 'best',
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,uz;q=0.8',
        'Connection': 'keep-alive',
    },
    'cookiesfrombrowser': None,
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

# === 4. AUDIONI AJRATIB OLIB YUBORISH (SOZLANGAN MUZIKA QISMI) ===
@dp.callback_query(F.data == "get_audio")
async def handle_audio(callback: types.CallbackQuery):
    caption = callback.message.caption or ""
    
    # MUZIKA UCHUN LINKNI TOZA AJRATIB OLISH FILTRI (Atrofidagi emojilar va yulduzchalarni tashlab ketadi)
    links = re.findall(r'(https?://www\.instagram\.com/[^\s*?👑\\]+)', caption)
    
    if not links:
        # Agar tepadagidan topa olmasa, muqobil toza qidiruv
        links = re.findall(r'(https?://[^\s*?\\]+)', caption)
        
    if not links:
        await callback.answer("❌ Havola topilmadi!", show_alert=True)
        return
        
    url = clean_url(links[0])
    await callback.answer("🎶 Audio tayyorlanmoqda...")
    
    audio_filename = f"audio_{callback.from_user.id}.mp3"
    # Audio yuklash formatini yanada barqaror qildik
    opts = {**YDL_OPTS, 'format': 'bestaudio/best', 'outtmpl': audio_filename}
    
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
            
        if os.path.exists(audio_filename):
            # ORIGINAL AUDIO MATNI
            await callback.message.answer_audio(
                audio=types.FSInputFile(audio_filename),
                filename="music.mp3",
                title="music",
                performer="Bot Yuklovchi",
                caption="🎵 **Siz so'ragan audio variant tayyor!** \n\n🎧 _Huzur qilib tinglang!_ ✨",
                parse_mode="Markdown"
            )
            os.remove(audio_filename)
        else:
            raise Exception("Audio fayl topilmadi")
    except Exception as e:
        print(f"Audio xatosi: {e}")
        await callback.message.answer("❌ **Kechirasiz, ushbu videoning audio variantini ajratib olish imkoni bo'lmadi.**", parse_mode="Markdown")

# === 5. NOTO'G'RI MATN YUBORILGANDA ASLIY "DIQQAT" OGOHLANTIRISHI ===
@dp.message()
async def text_fallback(message: types.Message):
    if message.text == "🔄 Botni qayta ishga tushirish":
        await start_cmd(message)
        return
        
    await message.answer(
        "🚨 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ 🚨\n"
        "⚠️ *DIQQAT:* `Noto'g'ri buyruq kiritildi!`\n\n"
        "📥 _Iltimos, faqat to'g'ri va ishlaydigan_ *Instagram* _havolasini (linkini) yuboring!_\n"
        "🚨 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ 🚨",
        parse_mode="Markdown"
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
