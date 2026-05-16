import asyncio
import os
import re
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# O'zgaruvchilarni olish
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

def clean_youtube_url(url: str) -> str:
    """Murakkab pleylist va radio havolalarini toza video havolasiga o'tkazish"""
    video_id_match = re.search(r'(?:v=|\/v\/|embed\/|youtu\.be\/|shorts\/)([^"&?\/ ]{11})', url)
    if video_id_match:
        return f"https://www.youtube.com/watch?v={video_id_match.group(1)}"
    return url

@dp.message(Command("start"))
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="🔄 Botni qayta ishga tushirish")]],
        resize_keyboard=True
    )
    await message.answer(
        "✅ **Assalomu alaykum!**\n"
        "Bu bot @Obidjon_Musurmonov tomonidan yaratildi!\n"
        "YouTube yoki Instagram linkini yuboring.\n"
        "Men sizga video va uning audiosini yuklab beraman.",
        reply_markup=keyboard
    )

@dp.message(F.text == "🔄 Botni qayta ishga tushirish")
async def restart_button_handler(message: types.Message):
    await start(message)

# 1. HAVOLA KELGANDA ISHLAYDIGAN ASOSIY QISM
@dp.message(F.text.startswith("http"))
async def main_handler(message: types.Message):
    raw_url = message.text
    msg = await message.answer("Video yuklanmoqda... ⏳")
    
    # Havolani tozalash (Pleylist yoki radio parametrlarini olib tashlash)
    url = clean_youtube_url(raw_url)

    # PREMIUM YOUTUBE/INSTAGRAM API SHLYUZI
    api_url = "https://api.savetube.me/download"
    payload = {"url": url, "quality": "720"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=payload, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "success" and data.get("data"):
                        video_link = data["data"].get("video_url") or data["data"].get("url")
                        
                        if video_link:
                            builder = types.InlineKeyboardMarkup(inline_keyboard=[
                                [types.InlineKeyboardButton(text="🎵 Musiqasini yuklab olish", callback_data="find_full")]
                            ])
                            await message.answer_video(
                                video_link,
                                caption=f"Tayyor! ✅\n🔗 Havola: {url}",
                                reply_markup=builder
                            )
                            await msg.delete()
                            return

        # 2-URINISH: UNIVERSAL ZAXIRA SHLYUZI
        backup_url = f"https://api.vveb.dev/download?url={url}"
        async with aiohttp.ClientSession() as session:
            async with session.get(backup_url, timeout=20) as response:
                if response.status == 200:
                    data = await response.json()
                    v_link = data.get("url") or data.get("download_url") or data.get("result")
                    if v_link:
                        builder = types.InlineKeyboardMarkup(inline_keyboard=[
                            [types.InlineKeyboardButton(text="🎵 Musiqasini yuklab olish", callback_data="find_full")]
                        ])
                        await message.answer_video(
                            v_link,
                            caption=f"Tayyor! ✅\n🔗 Havola: {url}",
                            reply_markup=builder
                        )
                        await msg.delete()
                        return

        await message.answer("❌ Video yuklashda xatolik yuz berdi. Link noto'g'ri yoki video juda katta bo'lishi mumkin.")
    except Exception:
        await message.answer("❌ Video yuklashda xatolik yuz berdi. Link noto'g'ri yoki video juda katta bo'lishi mumkin.")
    finally:
        try:
            await msg.delete()
        except:
            pass

# 2. ODDIY SO'Z YOKI MATN YOZILGANDA OGOHLANTIRISH QISMI
@dp.message(F.text)
async def text_handler(message: types.Message):
    await message.answer("⚠️ Iltimos, YouTube yoki Instagram havolasini (linkini) yuboring!")

# 3. MUSIQASINI AJRATIB OLISH TUGMASI
@dp.callback_query(F.data == "find_full")
async def audio_handler(callback: types.CallbackQuery):
    caption = callback.message.caption
    links = re.findall(r'(https?://[^\s]+)', caption)
    if not links:
        await callback.answer("Link topilmadi!", show_alert=True)
        return

    url = clean_youtube_url(links[0])
    await callback.answer("Musiqa tayyorlanmoqda... 🎶")
    
    api_url = "https://api.savetube.me/download"
    payload = {"url": url, "quality": "audio"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=payload, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "success" and data.get("data"):
                        audio_link = data["data"].get("audio_url") or data["data"].get("url")
                        if audio_link:
                            await callback.message.answer_audio(
                                audio_link,
                                filename="music.mp3",
                                caption="Marhamat, musiqaning varianti! 🎵"
                            )
                            return

        # Audio uchun zaxira shlyuzi
        backup_audio_url = f"https://api.vveb.dev/download?url={url}&audio=true"
        async with aiohttp.ClientSession() as session:
            async with session.get(backup_audio_url, timeout=20) as response:
                if response.status == 200:
                    data = await response.json()
                    a_link = data.get("audio_url") or data.get("url") or data.get("result")
                    if a_link:
                        await callback.message.answer_audio(
                            a_link,
                            filename="music.mp3",
                            caption="Marhamat, musiqaning varianti! 🎵"
                        )
                        return
                        
        await callback.message.answer("❌ Afsuski, musiqani yuklab bo'lmadi.")
    except Exception:
        await callback.message.answer("❌ Musiqa yuklashda xatolik yuz berdi. Bir ozdan keyin qayta urinib ko'ring.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
