from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from filters.is_admin import is_admin_function
from config import path_to_csv
# from aiogram.filters.base



send_file_router = Router()


@send_file_router.message(lambda message: message.text == "Отправить файл" or
                         (message.text and message.text.startswith("/send_file")))
async def send_file_handler(message: Message):
    user_id = message.from_user.id
    checker_admin = is_admin_function(user_id)
    if checker_admin:
        file = FSInputFile(path_to_csv)
        await message.answer_document(file, caption=f"Вот оригинальный файл с данными о судорогах. {checker_admin}")
    else:
        await message.answer("У вас нет прав получать файл")