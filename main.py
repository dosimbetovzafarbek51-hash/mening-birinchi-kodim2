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

# yt-dlp uchun optimal sozlamalar
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'geo_bypass': True,
}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "✅ **Assalomu alaykum!**\n"
        "Bu bot @Obidjon_Musurmonov tomonidan yaratildi!\n"
        "YouTube yoki Instagram linkini yuboring.\n"
        "Men sizga video va uning audiosini yuklab beraman."
    )

@dp.message(F.text.startswith("http"))
async def main_handler(message: types.Message):
    url = message.text
    msg = await message.answer("Video yuklanmoqda... ⏳")
    file_name = f"v_{message.from_user.id}.mp4"

    try:
        # Videoni yuklash
        with yt_dlp.YoutubeDL({**YDL_OPTS, 'format': 'best', 'outtmpl': file_name}) as ydl:
            ydl.download([url])
        
        # Tugma yaratish
        builder = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎵 Musiqasini yuklab olish", callback_data="find_full")]
        ])

        if os.path.exists(file_name):
            await message.answer_video(
                types.FSInputFile(file_name), 
                caption=f"Tayyor! ✅\n🔗 Havola: {url}", 
                reply_markup=builder
            )
            os.remove(file_name) # Video yuborilgach o'chiramiz
    except Exception as e:
        await message.answer("❌ Video yuklashda xatolik yuz berdi. Link noto'g'ri yoki video juda katta bo'lishi mumkin.")
    finally:
        await msg.delete()

@dp.callback_query(F.data == "find_full")
async def audio_handler(callback: types.CallbackQuery):
    # Caption ichidan linkni qidirib topish
    caption = callback.message.caption
    links = re.findall(r'(https?://[^\s]+)', caption)
    if not links:
        await callback.answer("Link topilmadi!", show_alert=True)
        return

    url = links[0]
    await callback.answer("Musiqa tayyorlanmoqda... 🎶")
    
    audio_file = f"a_{callback.from_user.id}.mp3"
    audio_opts = {
        **YDL_OPTS,
        'format': 'bestaudio/best',
        'outtmpl': audio_file,
    }
    
    try:
        # Audioni yuklash
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([url])
        
        if os.path.exists(audio_file):
            await callback.message.answer_audio(
                types.FSInputFile(audio_file), 
                caption="Marhamat, musiqaning varianti! 🎵"
            )
            os.remove(audio_file) # Audio yuborilgach o'chiramiz
    except Exception:
        await callback.message.answer("❌ Afsuski, musiqani yuklab bo'lmadi.")

async def main():
    # Botni ishga tushirish
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
