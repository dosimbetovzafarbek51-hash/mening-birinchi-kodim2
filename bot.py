import asyncio
import os
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import yt_dlp

# Token va Bot sozlamalari
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

def clean_url(url: str) -> str:
    """Instagram linklaridagi ortiqcha parchalarni tozalash"""
    if url and "instagram.com" in url:
        match = re.search(r'(https?://(?:www\.)?instagram\.com/(?:p|reel|tv)/[^/\s\?]+)', url)
        if match:
            return match.group(1)
    return url

# === 1. START BUYRUG'I (ENG TEPADA TURISHI SHART) ===
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    kb = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="🔄 Botni qayta ishga tushirish")]],
        resize_keyboard=True
    )
    await message.answer(
        "✨ 🚀 <b>XUSH KELIBSIZ!</b> 🚀 ✨\n"
        "▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️\n\n"
        "🤖 <b>Ushbu mukammal va tezkor yuklagich bot</b> @Obidjon_Musurmonov <b>tomonidan maxsus tayyorlandi.</b>\n\n"
        "📥 <code>Menga faqat Instagram (Reels, Post, TV) havolasini yuboring!</code>\n"
        "⚡️ <i>Tizim sizga video va uning audiosini eng yuqori sifatda taqdim etadi.</i>\n\n"
        "▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️",
        reply_markup=kb,
        parse_mode="HTML"
    )

# === 2. RESTART TUGMASI ===
@dp.message(F.text == "🔄 Botni qayta ishga tushirish")
async def restart_btn(message: types.Message):
    await start_cmd(message)

# === 3. AUDIONI AJRATIB OLIB YUBORISH ===
@dp.callback_query(F.data == "get_audio")
async def handle_audio(callback: types.CallbackQuery):
    caption = callback.message.caption or ""
    links = re.findall(r'(https?://[^\s*?\\#]+)', caption)
    
    if not links:
        await callback.answer("❌ Havola topilmadi!", show_alert=True)
        return
        
    url = clean_url(links[0])
    await callback.answer("🎶 Audio tayyorlanmoqda...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
    }
    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'
    
    try:
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            audio_url = info.get('url')
            
            if audio_url:
                await callback.message.answer_audio(
                    audio=audio_url,
                    filename="music.mp3",
                    title="music",
                    performer="Bot Yuklovchi",
                    caption="🎵 <b>Siz so'ragan audio variant tayyor!</b> \n\n🎧 <i>Huzur qilib tinglang!</i> ✨",
                    parse_mode="HTML"
                )
                return
                
        raise Exception("Audio topilmadi")
    except Exception as e:
        print(f"Audio xatosi: {e}")
        await callback.message.answer("❌ <b>Kechirasiz, ushbu videoning audio variantini ajratib olish imkoni bo'lmadi.</b>", parse_mode="HTML")

# === 4. HAVOLALARNI TUTIB QOLUVCHI ASOSIY QISM ===
@dp.message(lambda msg: msg.text and "instagram.com" in msg.text)
async def handle_media(message: types.Message):
    url = clean_url(message.text)
    status_msg = await message.answer("⏳ <code>So'rov qabul qilindi. Media yuklanmoqda...</code>", parse_mode="HTML")
    
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }
    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'
    
    try:
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            video_url = info.get('url')
            
            if video_url:
                audio_btn = types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(text="🎵 ⬇️ MUSIQASINI YUKLAB OLISH ⬇️ 🎵", callback_data="get_audio")]
                ])
                
                # HTML formatiga o'tkazilgan caption matni
                caption_text = (
                    f"⚡️ <b>Muvaffaqiyatli yuklandi!</b> ✅\n\n"
                    f"🔗 <b>Havola:</b> {url}\n\n"
                    f"👑 <b>@Obidjon_Musurmonov tizimi</b>"
                )
                
                await message.answer_video(
                    video=video_url,
                    caption=caption_text,
                    parse_mode="HTML",
                    reply_markup=audio_btn
                )
                await status_msg.delete()
                return
            
        raise Exception("Video manzili bo'sh qaytdi")
                
    except Exception as e:
        print(f"Yuklash xatosi: {e}")
        # Xatolik matnini xavfsiz stringga o'giramiz
        error_msg = str(e)[:50].replace("<", "&lt;").replace(">", "&gt;")
        await message.answer(f"❌ <b>YUKLASHDA XATOLIK YUZ BERDI!</b>\n\n⚠️ <i>Tizim xatosi: {error_msg}</i>", parse_mode="HTML")
        try:
            await status_msg.delete()
        except:
            pass

# === 5. NOTO'G'RI MATN FILTRI (ENG PASDA TURISHI SHART) ===
@dp.message()
async def text_fallback(message: types.Message):
    await message.answer(
        "🚨 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ 🚨\n"
        "⚠️ <b>DIQQAT:</b> <code>Noto'g'ri buyruq kiritildi!</code>\n\n"
        "📥 <i>Iltimos, faqat to'g'ri va ishlaydigan</i> <b>Instagram</b> <i>havolasini (linkini) yuboring!</i>\n"
        "🚨 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ 🚨",
        parse_mode="HTML"
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
