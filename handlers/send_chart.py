from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from filters.is_admin import is_admin_function
from services.chart_generator import ChartGenerator
from config import path_to_csv
import os

send_chart_router = Router()


@send_chart_router.message(lambda message: message.text == "Отправить визуализацию" or
                                           message.text and message.text.startswith("/send_visualisation"))
async def send_charts_handler(message: Message):
    user_id = message.from_user.id

    if not is_admin_function(user_id):
        await message.answer("У вас нет прав для просмотра графиков")
        return

    await message.answer("Генерирую графики, пожалуйста подождите...")

    try:
        chart_gen = ChartGenerator(path_to_csv)
        interval_buffer = chart_gen.generate_interval_chart()
        temp_interval_path = "temp_interval_chart.png"
        with open(temp_interval_path, 'wb') as f:
            f.write(interval_buffer.getvalue())
        await message.answer_photo(
            FSInputFile(temp_interval_path),
            caption="График интервалов между приступами 📊"
        )
        duration_buffer = chart_gen.generate_duration_chart()

        temp_duration_path = "temp_duration_chart.png"
        with open(temp_duration_path, 'wb') as f:
            f.write(duration_buffer.getvalue())

        await message.answer_photo(
            FSInputFile(temp_duration_path),
            caption="График продолжительности приступов 📊"
        )

        os.remove(temp_interval_path)
        os.remove(temp_duration_path)

    except Exception as e:
        await message.answer(f"❌ Ошибка при генерации графиков: {str(e)}")