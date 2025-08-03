from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand, BotCommandScopeDefault
from bot import bot
def main_kb():
    kb_list = [
        [KeyboardButton(text="Добавить дату приступа"), KeyboardButton(text="Отправить визуализацию")],
        [KeyboardButton(text="Отправить файл"), KeyboardButton(text="Добавить медицину")]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйтесь меню"
    )
    return keyboard


async def command_menu():
    commands = [
        BotCommand(command='send_file', description="Получите файл Excel или CSV"),
        BotCommand(command='add_action', description="Добавить дату приступа"),
        BotCommand(command='add_medicine', description="Добавить медицину прописанное доктором"),
        BotCommand(command="send_visualisation", description="Визуализированный вид судорог")
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())