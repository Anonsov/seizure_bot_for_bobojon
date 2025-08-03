from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from filters.is_admin import is_admin_function
from keyboards.kb import main_kb
from keyboards.inline_kb import check_date
import pandas as pd
from datetime import datetime
from config import path_to_medicine_csv

add_medicine_router = Router()


class AddMedicineStates(StatesGroup):
    waiting_for_date = State()
    waiting_for_comment = State()


@add_medicine_router.message(lambda message: message.text and (
        message.text.startswith("/add_medicine") or
        message.text.startswith("Добавить медицину")
))
async def add_medicine_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if not is_admin_function(user_id):
        await message.answer("У вас нет прав для добавления записей о лекарствах")
        return

    await state.set_state(AddMedicineStates.waiting_for_date)
    await message.answer(
        "Введите дату в формате ДД.ММ.ГГГГ (например, 18.07.2024)",
        reply_markup=None
    )


@add_medicine_router.message(AddMedicineStates.waiting_for_date)
async def process_date(message: Message, state: FSMContext):
    try:
        date_str = message.text.strip()
        input_date = datetime.strptime(date_str, "%d.%m.%Y")
        formatted_date = input_date.strftime("%m/%d/%Y")

        await state.update_data(formatted_date=formatted_date)
        await state.set_state(AddMedicineStates.waiting_for_comment)

        await message.answer(
            "Введите информацию о лечении или комментарий:",
            reply_markup=None
        )
    except ValueError:
        await message.answer(
            "Неверный формат даты. Используйте формат ДД.ММ.ГГГГ (например, 18.07.2024)"
        )


@add_medicine_router.message(AddMedicineStates.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext):
    comment = message.text
    user_data = await state.get_data()

    result = add_medicine_record(
        user_data['formatted_date'],
        comment
    )

    if result:
        await message.answer(
            f"Данные о лечении сохранены:\n"
            f"Дата: {user_data['formatted_date']}\n"
            f"Комментарий: {comment}",
            reply_markup=main_kb()
        )
    else:
        await message.answer("Произошла ошибка при сохранении данных.",
                             reply_markup=main_kb())

    await state.clear()


def add_medicine_record(date_str, comment):
    """
    Add a new medicine record to the CSV file

    Args:
        date_str (str): Date in format 'MM/DD/YYYY'
        comment (str): Treatment information or comment

    Returns:
        bool: Success status
    """
    try:
        try:
            df = pd.read_csv(path_to_medicine_csv)
        except:
            df = pd.DataFrame(columns=['Дата', 'Лечение/Комментарии'])

        new_row = {
            'Дата': date_str,
            'Лечение/Комментарии': comment
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(path_to_medicine_csv, index=False)

        return True

    except Exception as e:
        print(f"Error adding medicine record: {e}")
        return False