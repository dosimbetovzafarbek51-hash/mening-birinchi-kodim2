import asyncio
import os
import re
import yt_dlp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# O'zgaruvchilarni olish
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# yt-dlp uchun maxsus bypass va xavfsizlik sozlamalari
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'geo_bypass': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'http_headers': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
}

def clean_url(url: str) -> str:
    """Pleylist, radio va ortiqcha parametrlarni havoladan tozalash"""
    if "youtube.com" in url or "youtu.be" in url:
        video_id_match = re.search(r'(?:v=|\/v\/|embed\/|youtu\.be\/|shorts\/)([^"&?\/ ]{11})', url)
        if video_id_match:
            return f"https://www.youtube.com/watch?v={video_id_match.group(1)}"
    elif "instagram.com" in url:
        clean_insta = re.search(r'(https?:\/\/www\.instagram\.com\/(?:p|reel|tv)\/[^\/\?]+)', url)
        if clean_insta:
            return clean_insta.group(1)
    return url

@dp.message(Command("start"))
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="🔄 Botni qayta ishga tushirish")]],
        resize_keyboard=True
    )
    await message.answer(
        "✅ **Assalomu alaykum!**\n"
        "Bu bot @Obidjon_Musurmonov tomonidan yaratildi!\n"
        "YouTube yoki Instagram linkini yuboring.\n"
        "Men sizga video va uning audiosini yuklab beraman.",
        reply_markup=keyboard
    )

@dp.message(F.text == "🔄 Botni qayta ishga tushirish")
async def restart_button_handler(message: types.Message):
    await start(message)

# 1. TO'G'RI HAVOLA KELGANDA ISHLAYDIGAN QISM
@dp.message(F.text.startswith("http"))
async def main_handler(message: types.Message):
    raw_url = message.text
    msg = await message.answer("Video yuklanmoqda... ⏳")
    
    url = clean_url(raw_url)
    file_name = f"v_{message.from_user.id}.mp4"
    
    video_opts = {
        **YDL_OPTS,
        'format': 'best[ext=mp4]/best',
        'outtmpl': file_name,
        'max_filesize': 48 * 1024 * 1024
    }

    try:
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            ydl.download([url])
        
        builder = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎵 Musiqasini yuklab olish", callback_data="find_full")]
        ])

        if os.path.exists(file_name):
            await message.answer_video(
                types.FSInputFile(file_name), 
                caption=f"Tayyor! ✅\n🔗 Havola: {url}", 
                reply_markup=builder
            )
            os.remove(file_name)
            await msg.delete()
            return
        else:
            raise Exception("Fayl yuklanmadi")

    except Exception:
        await message.answer("❌ Video yuklashda xatolik yuz berdi. Link noto'g'ri yoki video juda katta bo'lishi mumkin.")
    finally:
        try:
            await msg.delete()
        except:
            pass

# 2. ODDIY MATN YOKI SO'Z YOZILGANDA
@dp.message(F.text)
async def text_handler(message: types.Message):
    await message.answer("⚠️ Iltimos, YouTube yoki Instagram havolasini (linkini) yuboring!")

# 3. INTERAKTIV AUDIO TUGMASI
@dp.callback_query(F.data == "find_full")
async def audio_handler(callback: types.CallbackQuery):
    caption = callback.message.caption
    links = re.findall(r'(https?://[^\s]+)', caption)
    if not links:
        await callback.answer("Link topilmadi!", show_alert=True)
        return

    url = clean_url(links[0])
    await callback.answer("Musiqa tayyorlanmoqda... 🎶")
    
    audio_name = f"a_{callback.from_user.id}.mp3"
    audio_opts = {
        **YDL_OPTS,
        'format': 'bestaudio/best',
        'outtmpl': audio_name,
    }

    try:
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([url])
            
        if os.path.exists(audio_name):
            await callback.message.answer_audio(
                types.FSInputFile(audio_name),
                filename="music.mp3",
                caption="Marhamat, musiqaning varianti! 🎵"
            )
            os.remove(audio_name)
            return
    except Exception:
        await callback.message.answer("❌ Musiqa yuklashda xatolik yuz berdi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
