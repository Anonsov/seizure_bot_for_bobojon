import asyncio

from bot import dp, bot

from handlers.start_route import start_router
from handlers.send_file import send_file_router
from handlers.add_action import add_action_router
from handlers.add_medicine import add_medicine_router
from handlers.send_chart import send_chart_router
from keyboards.kb import command_menu


async def main():

    dp.include_router(start_router)
    dp.include_router(send_file_router)
    dp.include_router(add_action_router)
    dp.include_router(add_medicine_router)
    dp.include_router(send_chart_router)

    await command_menu()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())