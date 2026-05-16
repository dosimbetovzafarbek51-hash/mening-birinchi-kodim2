import asyncio
import os
import re
import aiohttp
import yt_dlp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# O'zgaruvchilarni olish
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Eng barqaror va xavfsiz yt-dlp sozlamalari
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
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

    # 1-URINISH: yt-dlp orqali to'g'ridan-to'g'ri yuklash (Instagram uchun)
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
            try:
                os.remove(file_name)
            except:
                pass
            await msg.delete()
            return
    except Exception:
        pass  # Agar yt-dlp xato bersa (YouTube holatida), zaxira rejasiga o'tadi

    # 2-URINISH: Tashqi API orqali yuklash zaxira tizimi (YouTube muammosini hal qiladi)
    try:
        api_url = f"https://api.vveb.dev/download?url={url}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    video_link = data.get("url") or data.get("download_url") or data.get("result")
                    
                    if video_link:
                        builder = types.InlineKeyboardMarkup(inline_keyboard=[
                            [types.InlineKeyboardButton(text="🎵 Musiqasini yuklab olish", callback_data="find_full")]
                        ])
                        await message.answer_video(
                            video_link,
                            caption=f"Tayyor! ✅\n🔗 Havola: {url}",
                            reply_markup=builder
                        )
                        await msg.delete()
                        return

        await message.answer("❌ Video yuklashda xatolik yuz berdi. Link noto'g'ri yoki video juda katta bo'lishi mumkin.")
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
    
    audio_file = f"a_{callback.from_user.id}_{callback.message.message_id}.mp3"
    
    # 1-URINISH: yt-dlp orqali audio yuklash
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
            return
    except Exception:
        pass

    # 2-URINISH: Audio uchun zaxira API tizimi
    try:
        api_url = f"https://api.vveb.dev/download?url={url}&audio=true"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    audio_link = data.get("audio_url") or data.get("url") or data.get("result")
                    
                    if audio_link:
                        await callback.message.answer_audio(
                            audio_link,
                            filename="music.mp3",
                            caption="Marhamat, musiqaning varianti! 🎵"
                        )
                        return
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
