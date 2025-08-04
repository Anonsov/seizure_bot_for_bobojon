from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.kb import main_kb
from filters.is_admin import is_admin_function
from keyboards.inline_kb import check_date, no_comment
from services.csv_manager import csv_manager
from utils.date_parser import parse_user_datetime, format_datetime_for_csv
from utils.escape_markdown_v2 import escape_markdown_v2


add_action_router = Router()


class AddActionStates(StatesGroup):
    waiting_for_datetime = State()
    waiting_for_duration = State()
    waiting_for_comment = State()



@add_action_router.message(lambda message: message.text and (
    message.text.startswith("/add_action") or
    message.text == "Добавить дату приступа"
))
async def add_action_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    checker = is_admin_function(user_id)
    if checker:
        await message.answer(
            f"*{checker}*, пожалуйста напишите когда случился приступ:\n\n"
            f"*📅 Примеры форматов даты и времени:*\n"
            f"• `25.12.2023 14:30`\n"
            f"• `25/12/2023 в 2 часа дня`\n"
            f"• `25-12-2023 примерно 2:30 вечера`\n"
            f"• `25.12.23 7 утра`",
            parse_mode="MarkdownV2"
        )
        await state.set_state(AddActionStates.waiting_for_datetime)
    else:
        await message.answer("Вы не имеете права добавлять приступы, берите разрешение у Акобира")


@add_action_router.message(AddActionStates.waiting_for_datetime)
async def process_datetime(message: Message, state: FSMContext):
    user_input = message.text
    datetime_obj = parse_user_datetime(user_input)

    if datetime_obj:
        formatted_date = format_datetime_for_csv(datetime_obj)
        await state.update_data(datetime=datetime_obj, formatted_date=formatted_date)
        await message.answer(
            f"Вы указали: {formatted_date}\n\nВерно?",
            reply_markup=check_date()
        )
    else:
        await message.answer(
            "❌ Не удалось распознать дату и время\\. Пожалуйста, попробуйте еще раз\\.\n"
            "Например\\: `25\\.12\\.2023 14\\:30` -- попробуйте такой формат",
            parse_mode="MarkdownV2"
        )


@add_action_router.callback_query(F.data == "correct")
async def confirm_datetime(callback, state: FSMContext):
    current_state = await state.get_state()
    if current_state != AddActionStates.waiting_for_datetime.state:
        await callback.answer("Это действие больше недоступно", show_alert=True)
        return

    await callback.message.answer(
    "✅ Отлично\\! Теперь укажите продолжительность приступа \\(например\\: `30 сек`\\)",
    parse_mode="MarkdownV2"
)
    await state.set_state(AddActionStates.waiting_for_duration)
    await callback.answer()


@add_action_router.callback_query(F.data == "incorrect")
async def decline_datetime(callback, state: FSMContext):
    current_state = await state.get_state()
    if current_state != AddActionStates.waiting_for_datetime.state:
        await callback.answer("Это действие больше недоступно", show_alert=True)
        return

    await callback.message.answer(
        "Пожалуйста, укажите дату и время приступа снова\\.\n"
        "Например\\: `25\\.12\\.2023 14\\:30` 🔄",
        parse_mode="MarkdownV2"
    )
    await state.set_state(AddActionStates.waiting_for_datetime)
    await callback.answer()


@add_action_router.message(AddActionStates.waiting_for_duration)
async def process_duration(message: Message, state: FSMContext):
    duration = message.text.strip()
    if not duration.replace(" ", "").replace("сек", "").isdigit():
        await message.answer(
            "❌ Неверный формат продолжительности. Укажите продолжительность в секундах, например: `30 сек`.",
            parse_mode="MarkdownV2"
        )
        return

    if duration.isdigit():
        duration = f"{duration} сек"

    await state.update_data(duration=duration)
    await message.answer(
        "Есть ли комментарии к приступу? Если нет, нажмите кнопку 'Нет'",
        reply_markup=no_comment()
    )
    await state.set_state(AddActionStates.waiting_for_comment)


@add_action_router.message(AddActionStates.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext):
    comment = message.text.strip() if message.text else "нет"
    user_data = await state.get_data()

    result, interval_days = csv_manager.add_seizure_record(
        user_data['formatted_date'],
        user_data['duration'],
        comment
    )

    if result:
        interval_msg = f"\nИнтервал: {interval_days} дней с предыдущего приступа" if interval_days is not None else ""
        await message.answer(
            escape_markdown_v2(
                f"✅ Данные о приступе сохранены:\n"
                f"📅 Дата и время: `{user_data['formatted_date']}`\n"
                f"⏱️ Продолжительность: `{user_data['duration']}`\n"
                f"📝 Комментарий: {comment}{interval_msg}"
            ),
            reply_markup=main_kb(),
            parse_mode="MarkdownV2"
        )
    else:
        await message.answer(
            escape_markdown_v2("❌ Произошла ошибка при сохранении данных."),
            reply_markup=main_kb(),
            parse_mode="MarkdownV2"
        )
    await state.clear()

@add_action_router.callback_query(F.data == "no")
async def no_comment_callback(callback, state: FSMContext):
    current_state = await state.get_state()
    if current_state != AddActionStates.waiting_for_comment.state:
        await callback.answer("Это действие больше недоступно", show_alert=True)
        return

    user_data = await state.get_data()

    result, interval_days = csv_manager.add_seizure_record(
        user_data['formatted_date'],
        user_data['duration'],
        ""
    )

    if result:
        interval_msg = f"\nИнтервал: {interval_days} дней с предыдущего приступа" if interval_days is not None else ""
        await callback.message.answer(
            f"✅ Данные о приступе сохранены:\n"
            f"📅 Дата и время: `{user_data['formatted_date']}`\n"
            f"⏱️ Продолжительность: `{user_data['duration']}`\n"
            f"📝 Комментарий: нет{interval_msg}",
            reply_markup=main_kb(),
            parse_mode="MarkdownV2"
        )
    else:
        await callback.message.answer("❌ Произошла ошибка при сохранении данных.",
                                      reply_markup=main_kb(),
                                      parse_mode="MarkdownV2")
    await state.clear()
    await callback.answer()