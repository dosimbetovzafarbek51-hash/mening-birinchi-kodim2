import asyncio
import os
import re
import aiohttp
import yt_dlp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# O'zgaruvchilarni olish
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# yt-dlp sozlamalari (Instagram yuklashlari uchun)
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'geo_bypass': True,
}

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

# 1. TO'G'RI HAVOLA KELGANDA ISHLAYDIGAN QISM
@dp.message(F.text.startswith("http"))
async def main_handler(message: types.Message):
    url = message.text
    msg = await message.answer("Video yuklanmoqda... ⏳")
    
    # AGAR YOUTUBE HAVOLASI BO'LSA - TO'G'RIDAN-TO'G'RI ENG KUChLI TIZIMGA YUBORAMIZ
    if "youtube.com" in url or "youtu.be" in url:
        try:
            # YouTube block'larini osongina aylanib o'tuvchi maxsus API tarmog'i
            api_url = f"https://api.shrtco.de/v3/yt-donwload?url={url}" # Muqobil barqaror API manzili
            # Tizim yuklamasini kamaytirish va tezlikni oshirish uchun universal premium API shlyuzi
            backup_api = f"https://api.vveb.dev/download?url={url}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(backup_api) as response:
                    if response.status == 200:
                        data = await response.json()
                        video_link = data.get("url") or data.get("download_url") or data.get("result")
                        
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
            raise Exception("Zaxira tarmog'iga o'tish")
        except Exception:
            # YouTube uchun 2-darajali super proxy yuklovchi
            try:
                super_api = f"https://endpoint.s9.im/api/download?url={url}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(super_api) as response:
                        if response.status == 200:
                            data = await response.json()
                            v_url = data.get("data", {}).get("video") or data.get("url")
                            if v_url:
                                builder = types.InlineKeyboardMarkup(inline_keyboard=[
                                    [types.InlineKeyboardButton(text="🎵 Musiqasini yuklab olish", callback_data="find_full")]
                                ])
                                await message.answer_video(
                                    v_url,
                                    caption=f"Tayyor! ✅\n🔗 Havola: {url}",
                                    reply_markup=builder
                                )
                                await msg.delete()
                                return
            except:
                pass

    # AGAR INSTAGRAM HAVOLASI BO'LSA (Yoki yt-dlp muqobili uchun)
    file_name = f"v_{message.from_user.id}_{message.message_id}.mp4"
    video_opts = {**YDL_OPTS, 'format': 'best', 'outtmpl': file_name}

    try:
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            ydl.download([url])
        
        builder = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎵 Musiqasini yuklab olish", callback_data="find_full")]
        ])

        if os.path.exists(file_name):
            await message.answer_video(
                types.FSInputFile(file_name), 
                caption=f"Tayyor! ✅\n🔗 Havola: {url}", 
                reply_markup=builder
            )
            try:
                os.remove(file_name)
            except:
                pass
            await msg.delete()
            return
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

# 3. AUDIONI ALOHIDA YUKLAB OLISH QISMI
@dp.callback_query(F.data == "find_full")
async def audio_handler(callback: types.CallbackQuery):
    caption = callback.message.caption
    links = re.findall(r'(https?://[^\s]+)', caption)
    if not links:
        await callback.answer("Link topilmadi!", show_alert=True)
        return

    url = links[0]
    await callback.answer("Musiqa tayyorlanmoqda... 🎶")
    
    # YouTube audio block'larini aylanib o'tish uchun toza oqim API so'rovi
    try:
        api_audio_url = f"https://api.vveb.dev/download?url={url}&audio=true"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_audio_url) as response:
                if response.status == 200:
                    data = await response.json()
                    audio_link = data.get("audio_url") or data.get("url") or data.get("result")
                    
                    if audio_link:
                        await callback.message.answer_audio(
                            audio_link,
                            filename="music.mp3",
                            caption="Marhamat, musiqaning varianti! 🎵"
                        )
                        return
        raise Exception("Zaxira rejasiga o'tish")
    except Exception:
        # Audioni qidirish uchun ikkinchi zaxira proxy kanali
        try:
            super_api = f"https://endpoint.s9.im/api/download?url={url}"
            async with aiohttp.ClientSession() as session:
                async with session.get(super_api) as response:
                    if response.status == 200:
                        data = await response.json()
                        a_url = data.get("data", {}).get("audio") or data.get("url")
                        if a_url:
                            await callback.message.answer_audio(
                                a_url,
                                filename="music.mp3",
                                caption="Marhamat, musiqaning varianti! 🎵"
                            )
                            return
            await callback.message.answer("❌ Afsuski, musiqani yuklab bo'lmadi.")
        except:
            await callback.message.answer("❌ Musiqa yuklashda xatolik yuz berdi. Bir ozdan keyin qayta urinib ko'ring.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
