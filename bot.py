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

@dp.message(Command("start"))
async def start(message: types.Message):
    # Bot tagidagi doimiy tugma
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🔄 Botni qayta ishga tushirish")]
        ],
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

# 1. TO'G'RI HAVOLA KELGANDA ISHLAYDIGAN QISM (YouTube va Instagram uchun)
@dp.message(F.text.startswith("http"))
async def main_handler(message: types.Message):
    url = message.text
    msg = await message.answer("Video yuklanmoqda... ⏳")
    
    # Bloklarni aylanib o'tuvchi universal yuklovchi API tarmog'i
    api_url = f"https://api.cobalt.tools/api/json"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url,
        "videoQuality": "720", # Eng barqaror va Telegram ko'tara oladigan sifat
        "filenamePattern": "basic"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    # Cobalt API muvaffaqiyatli havola qaytarsa:
                    if data.get("status") == "stream" or data.get("status") == "picker":
                        video_link = data.get("url")
                        
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
                    
        # Agar universal API ishlamay qolsa, zaxira API tizimi ishga tushadi
        raise Exception("Zaxira rejasiga o'tish")

    except Exception:
        # Zaxira yuklash tizimi (Lumiere / Vveb API)
        try:
            backup_url = f"https://api.vveb.dev/download?url={url}"
            async with aiohttp.ClientSession() as session:
                async with session.get(backup_url) as response:
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

# 3. MUSIQASINI YUKLAB OLISH TUGMASI BOSILGANDA
@dp.callback_query(F.data == "find_full")
async def audio_handler(callback: types.CallbackQuery):
    caption = callback.message.caption
    links = re.findall(r'(https?://[^\s]+)', caption)
    if not links:
        await callback.answer("Link topilmadi!", show_alert=True)
        return

    url = links[0]
    await callback.answer("Musiqa tayyorlanmoqda... 🎶")
    
    # Audio uchun maxsus Cobalt API so'rovi
    api_url = f"https://api.cobalt.tools/api/json"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url,
        "downloadMode": "audio", # Faqat audioni ajratib olish tartibi
        "audioFormat": "mp3"     # Toza mp3 formatida saqlash
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "stream":
                        audio_link = data.get("url")
                        
                        await callback.message.answer_audio(
                            audio_link,
                            filename="music.mp3",
                            caption="Marhamat, musiqaning varianti! 🎵"
                        )
                        return
        raise Exception("Zaxira audio rejasiga o'tish")
        
    except Exception:
        # Audio uchun zaxira API tizimi
        try:
            backup_audio_url = f"https://api.vveb.dev/download?url={url}&audio=true"
            async with aiohttp.ClientSession() as session:
                async with session.get(backup_audio_url) as response:
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
