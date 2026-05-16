import asyncio
import os
import re
import yt_dlp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# Token va Bot sozlamalari
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'geo_bypass': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

def clean_url(url: str) -> str:
    """Instagram havolalarini ortiqcha parametrlardan tozalash"""
    if "instagram.com" in url:
        clean_insta = re.search(r'(https?:\/\/www\.instagram\.com\/(?:p|reel|tv)\/[^\/\?]+)', url)
        if clean_insta:
            return clean_insta.group(1)
    return url

# === 1. START BUYRUG'I ===
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
        "🤖 *Ushbu mukammal va tezkor yuklagich bot* @Obidjon_Musurmonov *tomonidan maxsus tayyorlandi.*\n\n"
        "📥 `Menga faqat Instagram (Reels, Post, TV) havolasini yuboring!`\n"
        "⚡️ _Tizim sizga video va uning audiosini eng yuqori sifatda taqdim etadi._\n\n"
        "▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# === 2. RESTART TUGMASI (TUGMANI HAR QANDAY REJIMDA USHLAYDIGAN REJAX FILTR) ===
@dp.message(lambda msg: msg.text and ("qayta" in msg.text.lower() or "tushirish" in msg.text.lower()))
async def restart_button_handler(message: types.Message):
    await start(message)

# === 3. VIDEO YUKLASH QISMI (YOUTUBE VA INSTAGRAM) ===
@dp.message(lambda msg: msg.text and any(x in msg.text for x in ["instagram.com", "youtube.com", "youtu.be"]))
async def media_handler(message: types.Message):
    raw_url = message.text
    msg = await message.answer("🛸 ⏳ `Tizim ulanmoqda... Video yuklanmoqda...` 💾", parse_mode="Markdown")
    
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
            [types.InlineKeyboardButton(text="🎵 ⬇️ MUSIQASINI YUKLAB OLISH ⬇️ 🎵", callback_data="find_full")]
        ])

        if os.path.exists(file_name):
            await message.answer_video(
                types.FSInputFile(file_name), 
                caption=f"⚡️ *Muvaffaqiyatli yuklandi!* ✅\n\n🔗 *Havola:* {url}\n\n👑 @Obidjon\_Musurmonov *tizimi*", 
                parse_mode="Markdown",
                reply_markup=builder
            )
            os.remove(file_name)
            await msg.delete()
            return
        else:
            raise Exception("Video fayl yaratilmadi")

    except Exception:
        await message.answer("❌ *YUKLASHDA XATOLIK YUZ BERDI!*\n\n⚠️ _Havola noto'g'ri, video yopiq yoki o'ta katta bo'lishi mumkin._", parse_mode="Markdown")
    finally:
        try:
            await msg.delete()
        except:
            pass

# === 4. MUSIQANI XATOSIZ AJRATIB OLISH ===
@dp.callback_query(F.data == "find_full")
async def audio_handler(callback: types.CallbackQuery):
    # Havolani caption ichidan juda qat'iy rejaqs orqali qidiramiz
    caption = callback.message.caption or ""
    links = re.findall(r'https?://[^\s👑]+', caption)
    
    if not links:
        await callback.answer("❌ Havola topilmadi!", show_alert=True)
        return

    url = clean_url(links[0])
    await callback.answer("🎶 Audio yuklanmoqda, iltimos kuting...", show_alert=False)
    
    audio_name = f"audio_{callback.from_user.id}.m4a"
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
                performer="music",
                title="music",
                caption="🎵 *Siz so'ragan audio variant tayyor!* \n\n🎧 _Huzur qilib tinglang!_ ✨",
                parse_mode="Markdown"
            )
            os.remove(audio_name)
            return
        else:
            raise Exception("Audio fayl yaratilmadi")
    except Exception:
        await callback.message.answer("❌ *Kechirasiz, ushbu videoning audio variantini ajratib olish imkoni bo'lmadi.*", parse_mode="Markdown")

# === 5. BOSHQA NOTO'G'RI MATNLAR FILTRI ===
@dp.message()
async def text_handler(message: types.Message):
    if message.text:
        # Agar matnda biron-bir kalit so'z bo'lsa, xato xabarini chiqarmasdan o'tkazib yuboradi
        text_lower = message.text.lower()
        if "qayta" in text_lower or "tushirish" in text_lower or any(x in text_lower for x in ["instagram.com", "youtube.com", "youtu.be"]):
            return
        
        await message.answer(
            "🚨 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ 🚨\n"
            "⚠️ *DIQQAT:* `Noto'g'ri buyruq kiritildi!`\n\n"
            "📥 _Iltimos, faqat to'g'ri va ishlaydigan_ *Instagram* _havolasini (linkini) yuboring!_\n"
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
