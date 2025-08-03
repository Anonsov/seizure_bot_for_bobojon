from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebhookInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

def check_date():
    inline_kb = [
        [InlineKeyboardButton(text="Да", callback_data="correct")],
        [InlineKeyboardButton(text="Нет", callback_data="incorrect")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)

def no_comment():
    inline_kb = [
        [InlineKeyboardButton(text="Нет", callback_data="no")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)