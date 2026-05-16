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

# Railway serveri uchun eng barqaror va xatosiz sozlamalar
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'geo_bypass': True,
}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "✅ **Assalomu alaykum!**\n"
        "Bot qayta tiklandi va eng barqaror rejimga o'tkazildi! 🚀\n\n"
        "YouTube yoki Instagram linkini yuboring.\n"
        "Men sizga video va uning audiosini yuklab beraman."
    )

@dp.message(F.text.startswith("http"))
async def main_handler(message: types.Message):
    url = message.text
    msg = await message.answer("1. Havola tahlil qilinmoqda... 📡")
    file_name = f"v_{message.from_user.id}.mp4"

    # Server qiynalmasligi uchun videoni o'rtacha sifatda (360p yoki 480p) yuklaymiz
    video_opts = {
        **YDL_OPTS,
        'format': 'worstvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': file_name
    }

    try:
        await msg.edit_text("2. Video serverga yuklanmoqda... ⏳\n(Bu jarayon 1-2 daqiqa olishi mumkin, iltimos kuting)")
        
        # Videoni yuklash
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            ydl.download([url])
        
        # Tugma yaratish
        builder = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎵 Musiqasini yuklab olish", callback_data="find_full")]
        ])

        if os.path.exists(file_name):
            await msg.edit_text("3. Video Telegram'ga yuborilmoqda... 📤")
            await message.answer_video(
                types.FSInputFile(file_name), 
                caption=f"Tayyor! ✅\n🔗 Havola: {url}", 
                reply_markup=builder
            )
            os.remove(file_name) # Faylni darhol o'chiramiz
    except Exception as e:
        await message.answer("❌ Video yuklashda xatolik yuz berdi. Havola noto'g'ri yoki ushbu videoni yuklash taqiqlangan.")
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
        await callback.answer("Havola topilmadi!", show_alert=True)
        return

    url = links[0]
    await callback.answer("Musiqa yuklanmoqda... 🎶")
    
    audio_file = f"a_{callback.from_user.id}.mp3"
    audio_opts = {
        **YDL_OPTS,
        'format': 'bestaudio/best',
        'outtmpl': audio_file,
    }
    
    try:
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([url])
        
        if os.path.exists(audio_file):
            await callback.message.answer_audio(
                types.FSInputFile(audio_file), 
                caption="Marhamat, musiqaning varianti! 🎵"
            )
            os.remove(audio_file)
    except Exception:
        await callback.message.answer("❌ Afsuski, musiqani yuklab bo'lmadi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
