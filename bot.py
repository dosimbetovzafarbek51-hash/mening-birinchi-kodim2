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

# Eng xavfsiz va sodda yuklash filtri
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'geo_bypass': True,
    'format': 'best',  # Murakkab formatlardan voz kechib, eng barqarorini tanlaymiz
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def clean_url(url: str) -> str:
    """Instagram linklaridagi ortiqcha parchalarni tozalash"""
    if "instagram.com" in url:
        match = re.search(r'(https?://www\.instagram\.com/(?:p|reel|tv)/[^/?\s]+)', url)
        if match:
            return match.group(1)
    return url

# === START BUYRUG'I ===
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
        parse_mode="Markdown",
        reply_markup=kb
    )

# === TUGMANI ISHLATADIGAN ASOSIY QISM (KAFOLATLANGAN) ===
@dp.message(F.text == "🔄 Botni qayta ishga tushirish")
async def restart_btn(message: types.Message):
    await start_cmd(message)

# Havolalarni tutib qoluvchi asosiy qism
@dp.message(lambda msg: any(x in msg.text for x in ["instagram.com", "youtube.com", "youtu.be"]) if msg.text else False)
async def handle_media(message: types.Message):
    url = clean_url(message.text)
    status_msg = await message.answer("⏳ `So'rov qabul kijindi. Media yuklanmoqda...`", parse_mode="Markdown")
    
    out_filename = f"file_{message.from_user.id}.mp4"
    opts = {**YDL_OPTS, 'outtmpl': out_filename}
    
    try:
        # Yuklash jarayoni
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        
        if os.path.exists(out_filename):
            # Audio tugmachasi
            audio_btn = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="🎵 MP3 shaklini yuklab olish", callback_data="get_audio")]
            ])
            
            await message.answer_video(
                video=types.FSInputFile(out_filename),
                caption=f"✅ **Tayyor!**\n🔗 Havola: {url}",
                parse_mode="Markdown",
                reply_markup=audio_btn
            )
            os.remove(out_filename)
            await status_msg.delete()
        else:
            raise Exception("Fayl serverga yozilmadi")
            
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        await message.answer("❌ **Yuklashda xatolik yuz berdi!**\n\n_Iltimos, havola to'g'riligini yoki profil ochiqligini tekshiring._", parse_mode="Markdown")
        try:
            await status_msg.delete()
        except:
            pass

# Audioni ajratib olib yuborish
@dp.callback_query(F.data == "get_audio")
async def handle_audio(callback: types.CallbackQuery):
    caption = callback.message.caption or ""
    links = re.findall(r'(https?://[^\s]+)', caption)
    
    if not links:
        await callback.answer("❌ Havola topilmadi!", show_alert=True)
        return
        
    url = clean_url(links[0])
    await callback.answer("🎶 Audio tayyorlanmoqda...")
    
    audio_filename = f"audio_{callback.from_user.id}.m4a"
    opts = {**YDL_OPTS, 'format': 'bestaudio/best', 'outtmpl': audio_filename}
    
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
            
        if os.path.exists(audio_filename):
            await callback.message.answer_audio(
                audio=types.FSInputFile(audio_filename),
                filename="music.mp3",  # Foydalanuvchi yuklab olganda .mp3 formatda saqlanadi
                title="music",
                performer="Bot Yuklovchi",
                caption="🎵 **Musiqa mp3 formatda tayyorlandi!**",
                parse_mode="Markdown"
            )
            os.remove(audio_filename)
    except Exception as e:
        print(f"Audio xatosi: {e}")
        await callback.message.answer("❌ **Kechirasiz, audioni ajratib olishda xatolik bo'ldi.**", parse_mode="Markdown")

# Noto'g'ri matn yuborilganda (TUGMA ENDI BU YERDA TO'XTAB QOLMAYDI)
@dp.message()
async def text_fallback(message: types.Message):
    if message.text == "🔄 Botni qayta ishga tushirish":
        await start_cmd(message)
        return
    await message.answer("⚠️ **Iltimos, faqat to'g'ri Instagram yoki YouTube havolasini yuboring!**")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
