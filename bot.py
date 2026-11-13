import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, BusinessMessagesDeleted

TOKEN = os.getenv("BOT_TOKEN")
MY_ID = int(os.getenv("MY_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()
messages_db = {}

def extract_media(message: Message):
    if message.photo:
        return "photo", message.photo[-1].file_id
    if message.voice:
        return "voice", message.voice.file_id
    if message.video_note:
        return "video_note", message.video_note.file_id
    if message.video:
        return "video", message.video.file_id
    if message.document:
        return "document", message.document.file_id
    return None, None

@dp.business_message()
async def save_msg(message: Message):
    text = message.text or message.caption or ""
    sender = message.from_user.full_name if message.from_user else "Неизвестно"
    media_type, file_id = extract_media(message)
    messages_db[message.message_id] = {
        "sender": sender,
        "text": text,
        "media_type": media_type,
        "file_id": file_id
    }

@dp.edited_business_message()
async def on_edit(message: Message):
    old_data = messages_db.get(message.message_id)
    new_text = message.text or message.caption or "[Без текста]"
    sender = message.from_user.full_name if message.from_user else "Неизвестно"

    if old_data:
        old_text = old_data["text"] or "[Без текста]"
        if old_text != new_text:
            await bot.send_message(
                MY_ID,
                f"✏️ <b>Сообщение изменено</b>\nОт: {sender}\n\n<b>Было:</b> {old_text}\n<b>Стало:</b> {new_text}",
                parse_mode="HTML"
            )
    save_msg_data(message, sender, new_text)

def save_msg_data(message: Message, sender: str, text: str):
    media_type, file_id = extract_media(message)
    messages_db[message.message_id] = {
        "sender": sender,
        "text": text,
        "media_type": media_type,
        "file_id": file_id
    }

@dp.deleted_business_messages()
async def on_delete(event: BusinessMessagesDeleted):
    for msg_id in event.message_ids:
        if msg_id in messages_db:
            data = messages_db.pop(msg_id)
            sender = data["sender"]
            text = data["text"]
            m_type = data["media_type"]
            f_id = data["file_id"]

            caption = f"🗑 <b>Удалено сообщение</b>\nОт: {sender}"
            if text:
                caption += f"\nТекст: {text}"

            if m_type == "photo":
                await bot.send_photo(MY_ID, f_id, caption=caption, parse_mode="HTML")
            elif m_type == "voice":
                await bot.send_voice(MY_ID, f_id, caption=caption, parse_mode="HTML")
            elif m_type == "video_note":
                await bot.send_message(MY_ID, caption + "\n<i>(Удаленный кружочек ниже)</i>", parse_mode="HTML")
                await bot.send_video_note(MY_ID, f_id)
            elif m_type == "video":
                await bot.send_video(MY_ID, f_id, caption=caption, parse_mode="HTML")
            elif m_type == "document":
                await bot.send_document(MY_ID, f_id, caption=caption, parse_mode="HTML")
            else:
                await bot.send_message(MY_ID, caption, parse_mode="HTML")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
