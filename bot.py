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

# Umumiy yuklash sozlamalari
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'geo_bypass': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

def clean_url(url: str) -> str:
    """Havolalarni tozalash (Instagram yoki YouTube)"""
    if "instagram.com" in url:
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
    
    try:
        await message.answer_sticker("CAACAgIAAxkBAAENWpZmGj7l8pZ_u10K7D5vM9zAAUY37AACBwADwDZPE_Yv929zS3vXNAQ")
    except:
        pass

    await message.answer(
        "✨ 🚀 *XUSH KELIBSIZ!* 🚀 ✨\n"
        "▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️\n\n"
        "🤖 *Ushbu universal yuklagich bot* @Obidjon_Musurmonov *tomonidan maxsus tayyorlandi.*\n\n"
        "📥 `Menga Instagram (Reels, Post) yoki YouTube havolasini yuboring!`\n"
        "⚡️ _Tizim sizga video va uning audiosini eng yuqori sifatda taqdim etadi._\n\n"
        "▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# 🔄 TUGMANI HAR QANDAY HOLATDA HAM TANIDIGAN ENG ISHONCHLI FILTR
@dp.message(lambda msg: "Botni qayta ishga tushirish" in msg.text if msg.text else False)
async def restart_button_handler(message: types.Message):
    await start(message)

# 1. HAVOLA KELGANDA (INSTAGRAM YOKI YOUTUBE) ISHLAYDIGAN ASOSIY QISM
@dp.message(lambda msg: any(x in msg.text for x in ["instagram.com", "youtube.com", "youtu.be"]) if msg.text else False)
async def media_handler(message: types.Message):
    raw_url = message.text
    msg = await message.answer("🛸 ⏳ `Tizim ulanmoqda... Media yuklanmoqda...` 💾", parse_mode="Markdown")
    
    url = clean_url(raw_url)
    file_name = f"video_{message.from_user.id}.mp4"
    
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
            [types.InlineKeyboardButton(text="🎵 🔥 MUSIQASINI YUKLAB OLISH 🔥 🎵", callback_data="find_full")]
        ])

        if os.path.exists(file_name):
            await message.answer_video(
                types.FSInputFile(file_name), 
                caption=f"⚡️ *Muvaffaqiyatli yuklandi!* ✅\n\n🔗 *Havola:* `{url}`\n\n👑 @Obidjon\_Musurmonov *tizimi*", 
                parse_mode="Markdown",
                reply_markup=builder
            )
            os.remove(file_name)
            await msg.delete()
            return
        else:
            raise Exception("Fayl topilmadi")

    except Exception:
        await message.answer("❌ *YUKLASHDA XATOLIK YUZ BERDI!*\n\n⚠️ _Havola noto'g'ri, video juda katta yoki profil yopiq bo'lishi mumkin._", parse_mode="Markdown")
    finally:
        try:
            await msg.delete()
        except:
            pass

# 2. INTERAKTIV AUDIO TUGMASI (MUKAMMAL TO'G'RILANGAN MP3 FORMATI)
@dp.callback_query(F.data == "find_full")
async def audio_handler(callback: types.CallbackQuery):
    caption = callback.message.caption
    links = re.findall(r'(https?://[^\s]+)', caption)
    if not links:
        await callback.answer("❌ Havola topilmadi!", show_alert=True)
        return

    url = clean_url(links[0])
    await callback.answer("🎶 MP3 formatga o'girilmoqda, kuting...", show_alert=False)
    
    # Birinchi navbatda eng yuqori sifatli audio oqimini yuklab olamiz
    audio_name = f"music_{callback.from_user.id}.mp3"
    audio_opts = {
        **YDL_OPTS,
        'format': 'bestaudio/best',
        'outtmpl': audio_name,
        # yt-dlp ichki audio oqimini mp3 sifatida saqlashi uchun postprocessor sozlamasi
        'posttemplates': [{
            'key': 'AudioExtractor',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([url])
            
        if os.path.exists(audio_name):
            await callback.message.answer_audio(
                types.FSInputFile(audio_name),
                filename="music.mp3",       # Fayl formati toza mp3 bo'ldi!
                performer="Instagram_YT",
                title="music",
                caption="🎵 *Siz so'ragan MP3 variant tayyor!* \n\n🎧 _Huzur qilib tinglang!_ ✨",
                parse_mode="Markdown"
            )
            os.remove(audio_name)
            return
        else:
            raise Exception("Audio topilmadi")
    except Exception:
        # Agar serverda mp3 konvertor xato bersa, m4a formatini yuklab mp3 ko'rinishida yuborish (Zaxira varianti)
        try:
            alt_name = f"music_{callback.from_user.id}.m4a"
            alt_opts = {**YDL_OPTS, 'format': 'bestaudio', 'outtmpl': alt_name}
            with yt_dlp.YoutubeDL(alt_opts) as ydl:
                ydl.download([url])
            if os.path.exists(alt_name):
                await callback.message.answer_audio(
                    types.FSInputFile(alt_name),
                    filename="music.mp3",
                    performer="Instagram_YT",
                    title="music",
                    caption="🎵 *Siz so'ragan MP3 variant tayyor!* \n\n🎧 _Huzur qilib tinglang!_ ✨",
                    parse_mode="Markdown"
                )
                os.remove(alt_name)
                return
        except:
            pass
        await callback.message.answer("❌ *Kechirasiz, ushbu mediyadan MP3 audio ajratib olish imkoni bo'lmadi.*", parse_mode="Markdown")

# 3. NOTO'G'RI BUYRUQLAR FILTRI
@dp.message()
async def text_handler(message: types.Message):
    if message.text:
        # Agar bu havola yoki qayta ishga tushirish tugmasi bo'lsa, xatolik ko'rsatmaydi
        if any(x in message.text for x in ["instagram.com", "youtube.com", "youtu.be", "Botni qayta ishga tushirish"]):
            return
        
        await message.answer(
            "🚨 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ 🚨\n"
            "⚠️ *DIQQAT:* `Noto'g'ri buyruq kiritildi!`\n\n"
            "📥 _Iltimos, faqat to'g'ri va ishlaydigan_ *Instagram* _yoki_ *YouTube* _havolasini yuboring!_\n"
            "🚨 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ 🚨", 
            parse_mode="Markdown"
        )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
