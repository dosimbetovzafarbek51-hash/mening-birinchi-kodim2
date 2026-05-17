import asyncio
import os
import re
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# Token va Bot sozlamalari
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

def clean_url(url: str) -> str:
    """Instagram linklaridagi ortiqcha parchalarni tozalash"""
    if "instagram.com" in url:
        # Linkni toza holatga keltirish (Query parametrlarsiz)
        match = re.search(r'(https?://(?:www\.)?instagram\.com/(?:p|reel|tv)/[^/\s\?]+)', url)
        if match:
            return match.group(1)
    return url

# === 1. ORIGINAL START BUYRUG'I ===
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    kb = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="🔄 Botni qayta ishga tushirish")]],
        resize_keyboard=True
    )
    await message.answer(
        "✨ 🚀 *XUSH KELIBSIZ!* 🚀 ✨\n"
        "▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️\n\n"
        "🤖 *Ushbu mukammal va tezkor yuklagich bot* @Obidjon_Musurmonov *tomonidan maxsus tayyorlandi.*\n\n"
        "📥 `Menga faqat Instagram (Reels, Post, TV) havolasini yuboring!`\n"
        "⚡️ _Tizim sizga video va uning audiosini eng yuqori sifatda taqdim etadi._\n\n"
        "▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️",
        reply_markup=kb,
        parse_mode="Markdown"
    )

# === 2. RESTART TUGMASI ===
@dp.message(F.text == "🔄 Botni qayta ishga tushirish")
async def restart_btn(message: types.Message):
    await start_cmd(message)

# === 3. HAVOLALARNI TUTIB QOLUVCHI ASOSIY QISM ===
@dp.message(lambda msg: msg.text and "instagram.com" in msg.text)
async def handle_media(message: types.Message):
    url = clean_url(message.text)
    status_msg = await message.answer("⏳ `So'rov qabul qilindi. Media yuklanmoqda...`", parse_mode="Markdown")
    
    api_url = f"https://api.scraptik.com/instagram/downloader?url={url}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status != 200:
                    raise Exception(f"API xatosi, status kod: {response.status}")
                
                res_json = await response.json()
                
                # API statusini tekshirish
                if res_json.get("status") is True and "data" in res_json:
                    media_data = res_json["data"]
                    video_url = None
                    
                    # API har xil formatda qaytarishi mumkinligini hisobga olamiz:
                    if isinstance(media_data, list) and len(media_data) > 0:
                        # Agar ro'yxat bo'lsa birinchisini tekshiramiz
                        video_url = media_data[0].get("url") or media_data[0].get("video_url") or media_data[0].get("download_url")
                    elif isinstance(media_data, dict):
                        # Agar obyekt bo'lsa
                        video_url = media_data.get("video_url") or media_data.get("url") or media_data.get("download_url")
                    
                    if video_url:
                        # ORIGINAL INLINE TUGMA
                        audio_btn = types.InlineKeyboardMarkup(inline_keyboard=[
                            [types.InlineKeyboardButton(text="🎵 ⬇️ MUSIQASINI YUKLAB OLISH ⬇️ 🎵", callback_data="get_audio")]
                        ])
                        
                        caption_text = (
                            f"⚡️ **Muvaffaqiyatli yuklandi!** ✅\n\n"
                            f"🔗 **Havola:** {url}\n\n"
                            f"👑 **@Obidjon_Musurmonov tizimi**"
                        )
                        
                        await message.answer_video(
                            video=video_url,
                            caption=caption_text,
                            parse_mode="Markdown",
                            reply_markup=audio_btn
                        )
                        await status_msg.delete()
                        return  # Muvaffaqiyatli tugatilganda funksiyadan chiqamiz
                    
                # Agar if shartlariga kirmasa, demak video topilmadi
                raise Exception("Video havolasi API'dan topilmadi")
                
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        await message.answer("❌ **YUKLASHDA XATOLIK YUZ BERDI!**\n\n⚠️ _Havola noto'g'ri, video yopiq yoki o'ta katta bo'lishi mumkin._", parse_mode="Markdown")
        try:
            await status_msg.delete()
        except:
            pass

# === 4. AUDIONI AJRATIB OLIB YUBORISH ===
@dp.callback_query(F.data == "get_audio")
async def handle_audio(callback: types.CallbackQuery):
    caption = callback.message.caption or ""
    links = re.findall(r'(https?://[^\s*?\\#]+)', caption)
    
    if not links:
        await callback.answer("❌ Havola topilmadi!", show_alert=True)
        return
        
    url = clean_url(links[0])
    await callback.answer("🎶 Audio tayyorlanmoqda...")
    
    api_url = f"https://api.scraptik.com/instagram/downloader?url={url}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    res_json = await response.json()
                    if res_json.get("status") is True and "data" in res_json:
                        media_data = res_json["data"]
                        audio_url = None
                        
                        if isinstance(media_data, list) and len(media_data) > 0:
                            audio_url = media_data[0].get("audio") or media_data[0].get("audio_url")
                        elif isinstance(media_data, dict):
                            audio_url = media_data.get("audio_url") or media_data.get("audio")
                        
                        if audio_url:
                            await callback.message.answer_audio(
                                audio=audio_url,
                                filename="music.mp3",
                                title="music",
                                performer="Bot Yuklovchi",
                                caption="🎵 **Siz so'ragan audio variant tayyor!** \n\n🎧 _Huzur qilib tinglang!_ ✨",
                                parse_mode="Markdown"
                            )
                            return
                            
                raise Exception("Audio topilmadi")
    except Exception as e:
        print(f"Audio xatosi: {e}")
        await callback.message.answer("❌ **Kechirasiz, ushbu videoning audio variantini ajratib olish imkoni bo'lmadi.**", parse_mode="Markdown")

# === 5. NOTO'G'RI MATN FILTRI ===
@dp.message()
async def text_fallback(message: types.Message):
    if message.text == "🔄 Botni qayta ishga tushirish":
        await start_cmd(message)
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
