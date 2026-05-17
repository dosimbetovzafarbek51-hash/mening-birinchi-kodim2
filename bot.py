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
        match = re.search(r'(https?://www\.instagram\.com/(?:p|reel|tv)/[^/\s\?*\\]+)', url)
        if match:
            return match.group(1)
    return url

# === 1. ORIGINAL START BUYRUG'I (MATNLARGA UMUMAN TEGilmadi) ===
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
        reply_markup=kb
    )

# === 2. RESTART TUGMASI ===
@dp.message(F.text == "🔄 Botni qayta ishga tushirish")
async def restart_btn(message: types.Message):
    await start_cmd(message)

# === 3. HAVOLALARNI TUTIB QOLUVCHI ASOSIY QISM (YANGI KAFOLATLI API TIZIM) ===
@dp.message(lambda msg: msg.text and not msg.text.startswith("/") and "instagram.com" in msg.text)
async def handle_media(message: types.Message):
    url = clean_url(message.text)
    status_msg = await message.answer("⏳ `So'rov qabul qilindi. Media yuklanmoqda...`", parse_mode="Markdown")
    
    # Bloklanishni aylanib o'tuvchi ochiq tezkor API
    api_url = f"https://api.vreden.my.id/api/instagram?url={url}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    res_json = await response.json()
                    
                    if res_json.get("status") and res_json.get("result"):
                        media_list = res_json["result"]
                        # Birinchi topilgan video linkini olish
                        video_url = media_list[0]["url"]
                        
                        # ORIGINAL INLINE TUGMA (Siz istgandek)
                        audio_btn = types.InlineKeyboardMarkup(inline_keyboard=[
                            [types.InlineKeyboardButton(text="🎵 ⬇️ MUSIQASINI YUKLAB OLISH ⬇️ 🎵", callback_data="get_audio")]
                        ])
                        
                        # Sizning skrinshotingizdagi chiroyli va qonuniy caption dizayni
                        caption_text = (
                            f"⚡️ **Muvaffaqiyatli yuklandi!** ✅\n\n"
                            f"🔗 **Havola:** {url}\n\n"
                            f"👑 **@Obidjon_Musurmonov tizimi**"
                        )
                        
                        # URL orqali to'g'ridan-to'g'ri o'ta tez yuborish (serverni qiynamaydi)
                        await message.answer_video(
                            video=video_url,
                            caption=caption_text,
                            parse_mode="Markdown",
                            reply_markup=audio_btn
                        )
                        await status_msg.delete()
                        return
        raise Exception("API orqali yuklash imkoni bo'lmadi")
            
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        await message.answer("❌ **YUKLASHDA XATOLIK YUZ BERDI!**\n\n⚠️ _Havola noto'g'ri, video yopiq yoki o'ta katta bo'lishi mumkin._", parse_mode="Markdown")
        try:
            await status_msg.delete()
        except:
            pass

# === 4. AUDIONI AJRATIB OLIB YUBORISH (KAFOLATLI VARIANTI) ===
@dp.callback_query(F.data == "get_audio")
async def handle_audio(callback: types.CallbackQuery):
    caption = callback.message.caption or ""
    links = re.findall(r'(https?://[^\s*?\\#]+)', caption)
    
    if not links:
        await callback.answer("❌ Havola topilmadi!", show_alert=True)
        return
        
    url = clean_url(links[0])
    await callback.answer("🎶 Audio tayyorlanmoqda...")
    
    api_url = f"https://api.vreden.my.id/api/instagram?url={url}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    res_json = await response.json()
                    if res_json.get("status") and res_json.get("result"):
                        # To'g'ridan-to'g'ri audio variantini yuklab yuborish
                        audio_url = res_json["result"][0]["url"]
                        
                        # ORIGINAL AUDIO MATNI
                        await callback.message.answer_audio(
                            audio=audio_url,
                            filename="music.mp3",
                            title="music",
                            performer="Bot Yuklovchi",
                            caption="🎵 **Siz so'ragan audio variant tayyor!** \n\n🎧 _Huzur qilib tinglang!_ ✨",
                            parse_mode="Markdown"
                        )
                        return
        raise Exception("Audio ajratib bo'lmadi")
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
