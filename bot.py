import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# O'zgaruvchilarni olish
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Ishonchli va mutlaqo bepul yuklash API xizmati
API_URL = "https://api.vreden.com.ua/api/downloader"

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "✅ **Assalomu alaykum!**\n"
        "Bot to'liq yangilandi va maksimal tezlikka o'tkazildi! 🚀\n\n"
        "YouTube, Instagram, TikTok yoki Facebook linkini yuboring, "
        "men uni bir necha soniyada yuklab beraman!"
    )

@dp.message(F.text.startswith("http"))
async def download_handler(message: types.Message):
    url = message.text
    msg = await message.answer("Havola tekshirilmoqda va yuklanmoqda... ⏳")

    payload = {"url": url}

    try:
        async with aiohttp.ClientSession() as session:
            # Tashqi API ga so'rov yuboramiz
            async with session.post(API_URL, json=payload, timeout=30) as response:
                if response.status == 200:
                    res_data = await response.json()
                    
                    # API dan to'g'ridan-to'g'ri video havolasini olamiz
                    video_url = res_data.get("video") or res_data.get("url")
                    title = res_data.get("title", "Muvaffaqiyatli yuklandi! ✅")

                    if video_url:
                        await msg.edit_text("Video Telegram'ga yuborilmoqda... 📤")
                        # Videoni serverga yuklamasdan, havola orqali yuboramiz (juda tez!)
                        await message.answer_video(
                            video=video_url,
                            caption=f"🎬 **{title}**\n\n🔗 original havola: {url}"
                        )
                    else:
                        await message.answer("❌ Afsuski, ushbu havoladan video topilmadi.")
                else:
                    await message.answer("❌ Yuklash xizmati vaqtincha band. Birozdan so'ng urinib ko'ring.")
    except Exception as e:
        await message.answer("❌ Xatolik yuz berdi. Havola noto'g'ri yoki video hajmi juda katta.")
    finally:
        try:
            await msg.delete()
        except:
            pass

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
