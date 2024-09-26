import asyncio

from db import set_db_connection

from telegram_bot.bot import run_bot

from news_tracker.tracker import TrackerLoop


async def start_service() -> None:
    loop = TrackerLoop()
    task1 = asyncio.create_task(set_db_connection())
    task2 = asyncio.create_task(run_bot())
    task3 = asyncio.create_task(loop.run())
    await asyncio.gather(task1, task2, task3)


if __name__ == "__main__":

    asyncio.run(start_service())
