import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Настройки бота
BOT_TOKEN = "8798795272:AAFRd6w-Zh5SWLg0gDeBmnQd4qe1Hr-yW0E"
CHANNEL_ID = "https://t.me/waplnyscript"  # Например: -1001234567890 или "@my_channel"

logging.basicConfig(level=logging.INFO)
bot = Bot(token="8798795272:AAFRd6w-Zh5SWLg0gDeBmnQd4qe1Hr-ywOE")
dp = Dispatcher()

# Функция для проверки подписки пользователя на канал
async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        # Если статус пользователя не 'left', 'kicked', то он подписан
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        logging.error(f"Ошибка проверки подписки: {e}")
        # Если бота нет в канале или произошла ошибка, по умолчанию пропускаем, 
        # чтобы бот не ломался, либо верните False
        return False

# Функция для запроса к API обхода ссылок
async def bypass_link(url: str) -> tuple[bool, str]:
    api_url = f"https://api.bypass.vip/bypass?url={url}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "success":
                        return True, data.get("result", "")
                    else:
                        return False, data.get("message", "Неизвестная ошибка API")
                else:
                    return False, f"Ошибка сервера (Статус: {response.status})"
    except Exception as e:
        return False, str(e)

# Клавиатура с кнопкой проверки подписки
def get_sub_keyboard():
    # Если CHANNEL_ID это юзернейм (начинается с @), делаем на него ссылку
    invite_link = f"https://t.me/{CHANNEL_ID.replace('@', '')}" if str(CHANNEL_ID).startswith('@') else "https://t.me/telegram"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться на канал", url=invite_link)],
        [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_sub")]
    ])
    return keyboard

@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    is_subscribed = await check_subscription(user_id)
    
    if is_subscribed:
        await message.answer("👋 Скинь ссылку для обхода")
    else:
        await message.answer(
            "⚠️ Для использования бота необходимо подписаться на наш канал!",
            reply_markup=get_sub_keyboard()
        )

@dp.callback_query(lambda c: c.data == "check_sub")
async def process_check_sub(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    is_subscribed = await check_subscription(user_id)
    
    if is_subscribed:
        await callback_query.message.answer("👋 Скинь ссылку для обхода")
        await callback_query.answer()
    else:
        await callback_query.answer("❌ Вы всё еще не подписались на канал!", show_alert=True)

@dp.message()
async def handle_links(message: Message):
    user_id = message.from_user.id
    
    # Перед обработкой ссылки еще раз проверяем подписку
    if not await check_subscription(user_id):
        await message.answer(
            "⚠️ Вы отписались от канала. Пожалуйста, подпишитесь снова для использования бота:",
            reply_markup=get_sub_keyboard()
        )
        return

    text = message.text.strip()
    
    if any(domain in text for domain in ["platorelay.com", "linkvertise.com", "loot-links.com", "lootlabs"]):
        waiting_msg = await message.answer("⏳ Обрабатываю ссылку, пожалуйста, подождите...")
        
        success, result = await bypass_link(text)
        
        if success:
            await waiting_msg.edit_text(
                f"🫡 всё успешно обойдено\n"
                f"Вот твой ключ:\n\n`{result}`", 
                parse_mode="Markdown"
            )
        else:
            await waiting_msg.edit_text(f"❌ Произошла ошибка при обходе: {result}")
    else:
        await message.answer("❌ Отправьте корректную ссылку (Platorelay, Linkvertise или Lootlabs).")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
