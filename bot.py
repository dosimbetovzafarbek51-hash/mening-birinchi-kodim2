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

# Railway serveri uchun eng xavfsiz umumiy sozlamalar
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
        # Videoni yuklash (Eng barqaror formatda)
        with yt_dlp.YoutubeDL({**YDL_OPTS, 'format': 'best', 'outtmpl': file_name}) as ydl:
            ydl.download([url])
        
        # Tugma yaratish (InlineKeyboardMarkup to'g'ri shaklda)
        builder = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎵 Musiqasini yuklab olish", callback_data="find_full")]
        ])

        if os.path.exists(file_name):
            await message.answer_video(
                types.FSInputFile(file_name), 
                caption=f"Tayyor! ✅\n🔗 Havola: {url}", 
                reply_markup=builder
            )
            # Diqqat: Videoni darhol o'chirmaymiz, chunki foydalanuvchi audio tugmasini bosishi mumkin!
            # Server to'lib ketmasligi uchun eski videolarni tozalash mantig'i pastda ishlaydi
    except Exception as e:
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
    
    # FFmpeg xatoligini aylanib o'tish uchun to'g'ridan-to'g'ri eng yengil audio oqimini ko'chiramiz
    audio_file = f"a_{callback.from_user.id}.mp3"
    audio_opts = {
        **YDL_OPTS,
        'format': 'bestaudio/best',
        'outtmpl': audio_file,
        # Quyidagi qator xatoliklarni oldini oladi va konvertatsiyasiz saqlaydi
        'keepvideo': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([url])
        
        # Agar fayl yuklangan bo'lsa (ba'zan yt-dlp uni .m4a formatda qoldirishi mumkin, uni tekshiramiz)
        actual_file = audio_file
        if not os.path.exists(actual_file):
            # yt-dlp o'zgartirgan bo'lishi mumkin bo'lgan kengaytmalarni qidiramiz
            for ext in ['.m4a', '.webm', '.aac']:
                possible_file = audio_file.replace('.mp3', ext)
                if os.path.exists(possible_file):
                    actual_file = possible_file
                    break

        if os.path.exists(actual_file):
            await callback.message.answer_audio(
                types.FSInputFile(actual_file), 
                caption="Marhamat, musiqaning varianti! 🎵"
            )
            try:
                os.remove(actual_file)
            except:
                pass
            
            # Ishlatib bo'lingan eski videoni ham endi tozalab yuboramiz
            video_file = f"v_{callback.from_user.id}.mp4"
            if os.path.exists(video_file):
                os.remove(video_file)
        else:
            raise Exception("Fayl topilmadi")

    except Exception:
        # Agar baribir xato bersa, eng xavfsiz va 100% ishlaydigan muqobil: videoni qayta yuklab, audio sifatida yuborish
        video_file = f"v_{callback.from_user.id}.mp4"
        if os.path.exists(video_file):
            await callback.message.answer_audio(
                types.FSInputFile(video_file),
                caption="Marhamat, musiqaning varianti! 🎵"
            )
            os.remove(video_file)
        else:
            await callback.message.answer("❌ Afsuski, ushbu ijtimoiy tarmoqdan audioni ajratib bo'lmadi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
