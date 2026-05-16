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

# Instagram uchun yuklash sozlamalari
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'geo_bypass': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

def clean_instagram_url(url: str) -> str:
    """Instagram havolasidan ortiqcha parametrlarni tozalab, toza havola qoldirish"""
    clean_insta = re.search(r'(https?:\/\/www\.instagram\.com\/(?:p|reel|tv)\/[^\/\?]+)', url)
    if clean_insta:
        return clean_insta.group(1)
    return url

@dp.message(Command("start"))
async def start(message: types.Message):
    # Doimiy tugma (Siz xohlagandek original holatda)
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="🔄 Botni qayta ishga tushirish")]],
        resize_keyboard=True
    )
    await message.answer(
        "✅ **Assalomu alaykum!**\n"
        "Bu bot @Obidjon_Musurmonov tomonidan yaratildi!\n"
        "Instagram linkini yuboring.\n"
        "Men sizga video va uning audiosini yuklab beraman.",
        reply_markup=keyboard
    )

@dp.message(F.text == "🔄 Botni qayta ishga tushirish")
async def restart_button_handler(message: types.Message):
    await start(message)

# 1. INSTAGRAM HAVOLASI KELGANDA ISHLAYDIGAN QISM
@dp.message(F.text.contains("instagram.com"))
async def instagram_handler(message: types.Message):
    raw_url = message.text
    msg = await message.answer("Instagram videosi yuklanmoqda... ⏳")
    
    url = clean_instagram_url(raw_url)
    file_name = f"insta_{message.from_user.id}.mp4"
    
    video_opts = {
        **YDL_OPTS,
        'format': 'best',
        'outtmpl': file_name,
        'max_filesize': 48 * 1024 * 1024  # 48MB gacha cheklov
    }

    try:
        # To'g'ridan-to'g'ri Instagram'dan yuklash
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            ydl.download([url])
        
        # Audio tugmasi (Siz xohlagandek original holatda)
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
        await message.answer("❌ Video yuklashda xatolik yuz berdi. Havola noto'g'ri yoki video yuklash imkonsiz.")
    finally:
        try:
            await msg.delete()
        except:
            pass

# 2. BOSHQA HAR QANDAY MATN YOKI YOUTUBE HAVOLASI KELGANDA
@dp.message(F.text)
async def text_handler(message: types.Message):
    await message.answer("⚠️ Iltimos, faqat Instagram havolasini (linkini) yuboring!")

# 3. INTERAKTIV AUDIO TUGMASI BOSILGANDA
@dp.callback_query(F.data == "find_full")
async def audio_handler(callback: types.CallbackQuery):
    caption = callback.message.caption
    links = re.findall(r'(https?://[^\s]+)', caption)
    if not links:
        await callback.answer("Link topilmadi!", show_alert=True)
        return

    url = clean_instagram_url(links[0])
    await callback.answer("Musiqa tayyorlanmoqda... 🎶")
    
    audio_name = f"mus_{callback.from_user.id}.mp3"
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
