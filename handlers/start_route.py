from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from keyboards.kb import main_kb

start_router = Router()

@start_router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋 Я бот для трэкинга судорог Бобочона. Рад помочь вам!",
        reply_markup=main_kb()
    )

