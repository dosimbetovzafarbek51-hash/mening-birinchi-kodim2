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

# Instagram yuklash sozlamalari
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'geo_bypass': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

def clean_instagram_url(url: str) -> str:
    """Instagram havolasidan ortiqcha parametrlarni tozalash"""
    clean_insta = re.search(r'(https?:\/\/www\.instagram\.com\/(?:p|reel|tv)\/[^\/\?]+)', url)
    if clean_insta:
        return clean_insta.group(1)
    return url

@dp.message(Command("start"))
async def start(message: types.Message):
    # Katta harflar va chiroyli emoji bilan boshqaruv tugmasi
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="🔄 BOTNI QAYTA ISHGA TUSHIRISH")]],
        resize_keyboard=True
    )
    
    # 🌟 Foydalanuvchini chiroyli kutib olish stikeri (Animatsiyali sovg'a stikeri)
    try:
        await message.answer_sticker("CAACAgIAAxkBAAENWpZmGj7l8pZ_u10K7D5vM9zAAUY37AACBwADwDZPE_Yv929zS3vXNAQ")
    except:
        pass

    await message.answer(
        "✨ 🚀 *XUSH KELIBSIZ!* 🚀 ✨\n"
        "▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️\n\n"
        "🤖 *Ushbu mukammal va tezkor yuklagich bot* @Obidjon_Musurmonov *tomonidan maxsus tayyorlandi.*\n\n"
        "📥 `Menga faqat Instagram (Reels, Post, TV) havolasini yuboring!`\n"
        "⚡️ _Tizim sizga video va uning audiosini eng yuqori sifatda taqdim etadi._\n\n"
        "▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@dp.message(F.text == "🔄 BOTNI QAYTA ISHGA TUSHIRISH")
async def restart_button_handler(message: types.Message):
    await start(message)

# 1. INSTAGRAM HAVOLASI KELGANDA ISHLAYDIGAN QISM
@dp.message(F.text.contains("instagram.com"))
async def instagram_handler(message: types.Message):
    raw_url = message.text
    msg = await message.answer("🛸 ⏳ `Tizim ulanmoqda... Video yuklanmoqda...` 💾", parse_mode="Markdown")
    
    url = clean_instagram_url(raw_url)
    file_name = f"insta_{message.from_user.id}.mp4"
    
    video_opts = {
        **YDL_OPTS,
        'format': 'best',
        'outtmpl': file_name,
        'max_filesize': 48 * 1024 * 1024
    }

    try:
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            ydl.download([url])
        
        # Tugmaga yorqin va jalb qiluvchi emojilar qo'shildi
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
        await message.answer("❌ *YUKLASHDA XATOLIK YUZ BERDI!*\n\n⚠️ _Havola noto'g'ri, profil yopiq yoki server hozirda band bo'lishi mumkin._", parse_mode="Markdown")
    finally:
        try:
            await msg.delete()
        except:
            pass

# 2. NOTO'G'RI BUYRUQ YOKI BOSHQA LINK KELGANDA
@dp.message(F.text)
async def text_handler(message: types.Message):
    await message.answer(
        "🚨 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ 🚨\n"
        "⚠️ *DIQQAT:* `Noto'g'ri buyruq kiritildi!`\n\n"
        "📥 _Iltimos, faqat to'g'ri va ishlaydigan_ *Instagram* _havolasini (linkini) yuboring!_\n"
        "🚨 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ 🚨", 
        parse_mode="Markdown"
    )

# 3. INTERAKTIV AUDIO TUGMASI (MP3 VA M4A MUQOBIL FORMATLAR BILAN)
@dp.callback_query(F.data == "find_full")
async def audio_handler(callback: types.CallbackQuery):
    caption = callback.message.caption
    links = re.findall(r'(https?://[^\s]+)', caption)
    if not links:
        await callback.answer("❌ Havola topilmadi!", show_alert=True)
        return

    url = clean_instagram_url(links[0])
    await callback.answer("🎶 Audio oqimi tayyorlanmoqda, kuting...", show_alert=False)
    
    audio_name = f"music_{callback.from_user.id}.mp3"
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
                filename="Instagram_Audio.mp3",
                caption="🎵 *Siz so'ragan audio variant tayyor!* \n\n🎧 _Huzur qilib tinglang!_ ✨",
                parse_mode="Markdown"
            )
            os.remove(audio_name)
            return
        else:
            raise Exception("Audio xatosi")
    except Exception:
        # Agar mp3da server konvertatsiya qila olmasa, toza m4a formatida yuklaydi
        try:
            alt_name = f"music_{callback.from_user.id}.m4a"
            alt_opts = {**YDL_OPTS, 'format': 'm4a/bestaudio', 'outtmpl': alt_name}
            with yt_dlp.YoutubeDL(alt_opts) as ydl:
                ydl.download([url])
            if os.path.exists(alt_name):
                await callback.message.answer_audio(
                    types.FSInputFile(alt_name),
                    filename="Audio.mp3",
                    caption="🎵 *Siz so'ragan audio variant tayyor!* \n\n🎧 _Huzur qilib tinglang!_ ✨",
                    parse_mode="Markdown"
                )
                os.remove(alt_name)
                return
        except:
            pass
        await callback.message.answer("❌ *Kechirasiz, ushbu videoning audio variantini ajratib olish imkoni bo'lmadi.*", parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
