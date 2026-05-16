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

# FFmpeg-siz serverlar uchun eng mustahkam sozlamalar
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'geo_bypass': True,
}

@dp.message(Command("start"))
async def start(message: types.Message):
    # Bot tagidagi doimiy tugma
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🔄 Botni qayta ishga tushirish")]
        ],
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
    url = message.text
    msg = await message.answer("Video yuklanmoqda... ⏳")
    
    file_name = f"v_{message.from_user.id}_{message.message_id}.mp4"

    video_opts = {
        **YDL_OPTS,
        'format': 'best',
        'outtmpl': file_name
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
    except Exception:
        await message.answer("❌ Video yuklashda xatolik yuz berdi. Link noto'g'ri yoki video juda katta bo'lishi mumkin.")
    finally:
        try:
            await msg.delete()
        except:
            pass

# 2. ODDIY SO'Z YOKI MATN YOZILGANDA OGOHLANTIRISH QISMI
@dp.message(F.text)
async def text_handler(message: types.Message):
    await message.answer("⚠️ Iltimos, YouTube yoki Instagram havolasini (linkini) yuboring!")

@dp.callback_query(F.data == "find_full")
async def audio_handler(callback: types.CallbackQuery):
    caption = callback.message.caption
    links = re.findall(r'(https?://[^\s]+)', caption)
    if not links:
        await callback.answer("Link topilmadi!", show_alert=True)
        return

    url = links[0]
    await callback.answer("Musiqa tayyorlanmoqda... 🎶")
    
    video_file = f"v_{callback.from_user.id}_{callback.message.message_id}.mp4"
    audio_file = f"a_{callback.from_user.id}_{callback.message.message_id}.mp3"
    
    if os.path.exists(video_file):
        try:
            await callback.message.answer_audio(
                types.FSInputFile(video_file, filename="music.mp3"),
                caption="Marhamat, musiqaning varianti! 🎵"
            )
            try:
                os.remove(video_file)
            except:
                pass
            return
        except Exception:
            pass

    audio_opts = {
        **YDL_OPTS,
        'format': 'bestaudio/best',
        'outtmpl': audio_file,
    }
    
    try:
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([url])
        
        actual_file = audio_file
        if not os.path.exists(actual_file):
            for ext in ['.m4a', '.webm', '.aac', '.mp4']:
                possible_file = audio_file.replace('.mp3', ext)
                if os.path.exists(possible_file):
                    actual_file = possible_file
                    break

        if os.path.exists(actual_file):
            await callback.message.answer_audio(
                types.FSInputFile(actual_file, filename="music.mp3"), 
                caption="Marhamat, musiqaning varianti! 🎵"
            )
            try:
                os.remove(actual_file)
            except:
                pass
        else:
            await callback.message.answer("❌ Afsuski, musiqani yuklab bo'lmadi.")
    except Exception:
        await callback.message.answer("❌ Musiqa yuklashda xatolik yuz berdi. Bir ozdan keyin qayta urinib ko'ring.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
