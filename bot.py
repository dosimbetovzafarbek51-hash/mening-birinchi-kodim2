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

# Railway serveri uchun eng optimal va xavfsiz sozlamalar
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'geo_bypass': True,
}

@dp.message(Command("start"))
async def start(message: types.Message):
    # Pastdagi doimiy start tugmasi
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🔄 Botni qayta ishga tushirish")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "✅ **Assalomu alaykum!**\n"
        "Bu bot @Obidjon_Musurmonov tomonidan qayta optimallashtirildi!\n"
        "YouTube yoki Instagram linkini yuboring.\n"
        "Men sizga videoni tezkor formatda yuklab beraman.",
        reply_markup=keyboard
    )

@dp.message(F.text == "🔄 Botni qayta ishga tushirish")
async def restart_button_handler(message: types.Message):
    await start(message)

@dp.message(F.text.startswith("http"))
async def main_handler(message: types.Message):
    url = message.text
    msg = await message.answer("Video yuklanmoqda... ⏳")
    
    # Unikal fayl nomi
    file_name = f"v_{message.from_user.id}_{message.message_id}.mp4"

    # YouTube va Instagram uchun eng xavfsiz format kombinatsiyasi
    video_opts = {
        **YDL_OPTS,
        'format': 'best',  # Murakkab filtrlarsiz eng mos keladigan tayyor formatni oladi
        'outtmpl': file_name
    }

    try:
        # Videoni yuklash
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            ydl.download([url])
        
        # Ovoz yuklash tugmasi
        builder = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎵 Musiqasini yuklab olish", callback_data="find_full")]
        ])

        if os.path.exists(file_name):
            await message.answer_video(
                types.FSInputFile(file_name), 
                caption=f"Tayyor! ✅\n🔗 Havola: {url}", 
                reply_markup=builder
            )
            # Diqqat: Videoni serverda biroz ushlab turamiz, toki audio tugmasi bosilganda ishlata olsin
    except Exception as e:
        await message.answer("❌ Video yuklashda xatolik yuz berdi. Havola noto'g'ri yoki server hozir yuklay olmadi.")
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
    
    video_file = f"v_{callback.from_user.id}_{callback.message.message_id}.mp4"
    audio_file = f"a_{callback.from_user.id}_{callback.message.message_id}.mp3"
    
    # 1-REJA: Agar yuklangan video hali serverda turgan bo'lsa (Uni shundoq audio qilib yuboramiz - 100% xatosiz yo'l)
    if os.path.exists(video_file):
        try:
            await callback.message.answer_audio(
                types.FSInputFile(video_file, filename="music.mp3"),
                caption="Marhamat, musiqaning varianti! 🎵"
            )
            try:
                os.remove(video_file) # Yuborilgach tozalaymiz
            except:
                pass
            return
        except Exception:
            pass

    # 2-REJA: Agar video serverdan o'chib ketgan bo'lsa, audioni qayta yuklash
    audio_opts = {
        **YDL_OPTS,
        'format': 'bestaudio/best',
        'outtmpl': audio_file,
    }
    
    try:
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([url])
        
        # Qo'shaloq kengaytmalarni oldini olish uchun tekshiramiz
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
        await callback.message.answer("❌ Musiqa yuklashda xatolik yuz berdi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
