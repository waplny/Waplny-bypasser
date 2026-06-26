import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Токен твоего бота от @BotFather
API_TOKEN = '8798795272:AAFRd6w-Zh5SWLg0gDeBmnQd4qe1Hr-yW0E'

# Ссылка и юзернейм твоего канала
CHANNEL_URL = "https://t.me/waplnyscript"
CHANNEL_USERNAME = "@waplnyscript"

# Настройки прокси для PythonAnywhere + сессия
session = AiohttpSession(proxy="http://proxy.server:3128")
bot = Bot(token=API_TOKEN, session=session)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# 1. Функция для проверки, подписан ли человек
async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
        return False
    except Exception as e:
        logging.error(f"Ошибка проверки подписки: {e}")
        return True

# 2. Создаем меню кнопок (Канал + Проверить)
def get_sub_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📢 Канал", url=CHANNEL_URL))
    builder.row(types.InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_sub"))
    return builder.as_markup()

# 3. Хэндлер на команду /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    is_sub = await check_subscription(message.from_user.id)

    if not is_sub:
        await message.answer(
            "Для использования бота необходимо подписаться на каналы:",
            reply_markup=get_sub_keyboard()
        )
        return

    await message.answer(
        "👋 Привет! Отправь мне ссылку на ключ Delta "
        "и я попробую её обойти."
    )

# 4. Обработка кнопки "Проверить подписку"
@dp.callback_query(lambda c: c.data == "check_sub")
async def process_check_sub(callback_query: types.CallbackQuery):
    is_sub = await check_subscription(callback_query.from_user.id)

    if is_sub:
        await callback_query.message.edit_text(
            "👋 Привет! Отправь мне ссылку на ключ Delta "
            "и я попробую её обойти."
        )
    else:
        await callback_query.answer("❌ Вы всё ещё не подписались на канал!", show_alert=True)

# 5. Хэндлер для обработки и БАЙПАСА входящих ссылок
@dp.message()
async def handle_link(message: types.Message):
    # Защита: проверяем подписку даже при отправке ссылки
    is_sub = await check_subscription(message.from_user.id)
    if not is_sub:
        await message.answer(
            "Для использования бота необходимо подписаться на канал:",
            reply_markup=get_sub_keyboard()
        )
        return

    url = message.text

    if not url.startswith("http://") and not url.startswith("https://"):
        await message.answer("❌ Пожалуйста, отправь корректную ссылку.")
        return

    msg = await message.answer("⏳ Обхожу ссылку, подожди немного...")
    bypass_api_url = f"https://api.bypass.vip/bypass?url={url}"

    try:
        async with aiohttp.ClientSession() as bypass_session:
            async with bypass_session.get(bypass_api_url, proxy="http://proxy.server:3128") as response:
                if response.status == 200:
                    data = await response.json()
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

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
