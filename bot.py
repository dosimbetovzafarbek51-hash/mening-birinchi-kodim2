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

# Railway serveri uchun eng xavfsiz va barqaror sozlamalar
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'geo_bypass': True,
}

@dp.message(Command("start"))
async def start(message: types.Message):
    # Bot tagida doimiy turadigan tugma
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

@dp.message(F.text.startswith("http"))
async def main_handler(message: types.Message):
    url = message.text
    msg = await message.answer("Video yuklanmoqda... ⏳")
    
    # Videofayl nomi aniq faqat bitta kengaytmada bo'ladi
    file_name = f"video_{message.from_user.id}.mp4"

    video_opts = {
        **YDL_OPTS,
        'format': 'ext=mp4/best',
        'outtmpl': file_name
    }

    try:
        # Videoni yuklash
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            ydl.download([url])
        
        # Inline tugma
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

@dp.callback_query(F.data == "find_full")
async def audio_handler(callback: types.CallbackQuery):
    caption = callback.message.caption
    links = re.findall(r'(https?://[^\s]+)', caption)
    if not links:
        await callback.answer("Link topilmadi!", show_alert=True)
        return

    url = links[0]
    await callback.answer("Musiqa tayyorlanmoqda... 🎶")
    
    video_file = f"video_{callback.from_user.id}.mp4"
    audio_base = f"audio_{callback.from_user.id}"
    
    # 1-REJA: Agar serverda hozirgina yuklangan video fayl bo'lsa (YouTube uchun eng xavfsiz va toza yo'l)
    if os.path.exists(video_file):
        try:
            # Faylni foydalanuvchiga audio pleer shaklida chiroyli sarlavha bilan yuboramiz
            await callback.message.answer_audio(
                types.FSInputFile(video_file, filename="music.mp3"),
                caption="Marhamat, musiqaning varianti! 🎵"
            )
            try:
                os.remove(video_file) # Ishlatib bo'lingach serverni tozalaymiz
            except:
                pass
            return
        except Exception:
            pass

    # 2-REJA: Agar video fayl o'chib ketgan bo'lsa (Zaxira tizimi)
    audio_opts = {
        **YDL_OPTS,
        'format': 'bestaudio/best',
        'outtmpl': f"{audio_base}.%(ext)s", # Kengaytmani yt-dlp o'zi mustaqil toza qo'yadi
    }
    
    try:
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            ext = info.get('ext', 'mp3')
            actual_file = f"{audio_base}.{ext}"

        if os.path.exists(actual_file):
            await callback.message.answer_audio(
                types.FSInputFile(actual_file, filename=f"music.{ext}"), 
                caption="Marhamat, musiqaning varianti! 🎵"
            )
            try:
                os.remove(actual_file)
            except:
                pass
        else:
            await callback.message.answer("❌ Afsuski, musiqani yuklab bo'lmadi.")
    except Exception:
        await callback.message.answer("❌ Musiqa yuklashda xatolik yuz berdi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
