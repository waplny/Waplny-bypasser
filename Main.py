import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# Вставьте сюда токен, который дал @BotFather
API_TOKEN = '8798795272:AAFRd6w-Zh5SWLg0gDeBmnQd4qe1Hr-yW0E'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# Хэндлер на команду /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Отправь мне ссылку на ключ Delta (Linkvertise/Lootlabs), "
        "и я попробую её обойти."
    )

# Хэндлер для обработки входящих ссылок
@dp.message()
async def handle_link(message: types.Message):
    url = message.text

    # Базовая проверка, что пользователь отправил именно ссылку
    if not url.startswith("http://") and not url.startswith("https://"):
        await message.answer("❌ Пожалуйста, отправь корректную ссылку.")
        return

    msg = await message.answer("⏳ Обхожу ссылку, подожди немного...")

    # URL стороннего API для байпаса (замените на актуальный рабочий эндпоинт)
    bypass_api_url = f"https://api.bypass.vip/bypass?url={url}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(bypass_api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Структура JSON зависит от выбранного API. 
                    # Обычно результат лежит в ключе 'result', 'destination' или 'bypassed'
                    bypassed_link = data.get("result") or data.get("destination")
                    
                    if bypassed_link:
                        await msg.edit_text(f"✅ **Готово!**\n\nТвоя ссылка/ключ:\n`{bypassed_link}`", parse_mode="Markdown")
                    else:
                        await msg.edit_text("❌ Не удалось извлечь ключ из ответа API.")
                else:
                    await msg.edit_text(f"❌ Ошибка API сервиса обхода (Код: {response.status}).")
    except Exception as e:
        logging.error(f"Ошибка при байпасе: {e}")
        await msg.edit_text("❌ Произошла ошибка при обработке запроса. Попробуй позже.")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
