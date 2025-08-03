import logging
from aiogram import Bot, Dispatcher
import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('TOKEN')
# print(TOKEN)
# ---- CONFIG VARIABLES
from config import path_to_csv, admin_json
# ---- CONFIG VARIABLES

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

