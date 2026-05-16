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

# Eng xavfsiz yuklash sozlamalari
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'geo_bypass': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

# START TUGMASI (EBLAB EMOLARSIZ MATN QO'YILDI, ADASHMAYDI)
def get_start_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="Botni qayta ishga tushirish")]],
        resize_keyboard=True
    )

# === 1. START BUYRUG'I ===
@dp.message(Command("start"))
async def start_command(message: types.Message):
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
        reply_markup=get_start_keyboard()
    )

# === 2. RESTART TUGMASI (ENG ISHONCHLI FILTR) ===
# Tugma bosilganda ham, foydalanuvchi o'zi yozganda ham darhol startga otadi
@dp.message(F.text.casefold().contains("qayta ishga") | (F.text == "Botni qayta ishga tushirish"))
async def restart_button_handler(message: types.Message):
    await start_command(message)

# === 3. VIDEO YUKLASH QISMI ===
@dp.message(lambda msg: msg.text and any(x in msg.text for x in ["instagram.com", "youtube.com", "youtu.be"]))
async def media_handler(message: types.Message):
    raw_url = message.text.strip()
    
    if "instagram.com" in raw_url:
        match = re.search(r'(https?://(?:www\.)?instagram\.com/(?:p|reel|tv)/[^/?\s]+)', raw_url)
        url = match.group(1) if match else raw_url
    else:
        url = raw_url

    msg = await message.answer("🛸 ⏳ `Tizim ulanmoqda... Video yuklanmoqda...` 💾", parse_mode="Markdown")
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
        
        short_id = url.split('/')[-1] if url.endswith('/') == False else url.split('/')[-2]
        is_yt = "yt" if "you" in url else "ig"
        
        builder = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎵 ⬇️ MUSIQASINI YUKLAB OLISH ⬇️ 🎵", callback_data=f"audio_{is_yt}_{short_id}")]
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
        else:
            raise Exception("Video yuklanmadi")

    except Exception as e:
        print(f"Video yuklash xatosi: {e}")
        await message.answer("❌ *YUKLASHDA XATOLIK YUZ BERDI!*\n\n⚠️ _Havola noto'g'ri, video yopiq yoki o'ta katta bo'lishi mumkin._", parse_mode="Markdown")
        try:
            await msg.delete()
        except:
            pass

# === 4. MUSIQANI AJRATIB OLISH ===
@dp.callback_query(F.data.startswith("audio_"))
async def audio_handler(callback: types.CallbackQuery):
    data_parts = callback.data.split("_")
    is_yt = data_parts[1]
    short_id = data_parts[2]
    
    if is_yt == "ig":
        url = f"https://www.instagram.com/reel/{short_id}"
    else:
        url = f"https://www.youtube.com/watch?v={short_id}"
        
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
        else:
            raise Exception("Audio fayl yaratilmadi")
    except Exception as e:
        print(f"Audio yuklash xatosi: {e}")
        await callback.message.answer("❌ *Kechirasiz, ushbu videoning audio variantini ajratib olish imkoni bo'lmadi.*", parse_mode="Markdown")

# === 5. NOTO'G'RI MATNLAR FILTRI (FAQAT ENG OXIRIDA ISHLAYDI) ===
@dp.message()
async def text_handler(message: types.Message):
    if not message.text:
        return
        
    text_lower = message.text.lower()
    # Agar matnda qayta ishga tushirish yoki link bo'lsa, xato xabari chiqmasligi kafolatlanadi
    if "qayta" in text_lower or "ishga" in text_lower or any(x in text_lower for x in ["instagram.com", "youtube.com", "youtu.be"]):
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
    asyncio.run(main())
