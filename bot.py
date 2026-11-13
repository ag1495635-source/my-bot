import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, BusinessMessagesDeleted

TOKEN = os.getenv("BOT_TOKEN")
MY_ID = int(os.getenv("MY_ID")) 

bot = Bot(token=TOKEN)
dp = Dispatcher()
messages_db = {}

@dp.business_message()
async def save_msg(message: Message):
    text = message.text or message.caption or "[Медиафайл без текста]"
    sender = message.from_user.full_name if message.from_user else "Неизвестно"
    messages_db[message.message_id] = (sender, text)

@dp.deleted_business_messages()
async def on_delete(event: BusinessMessagesDeleted):
    for msg_id in event.message_ids:
        if msg_id in messages_db:
            sender, text = messages_db.pop(msg_id)
            await bot.send_message(
                MY_ID,
                f"🗑 <b>Удалено сообщение</b>\nОт: {sender}\nТекст: {text}",
                parse_mode="HTML"
            )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
