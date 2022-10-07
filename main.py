import asyncio

from db import set_db_connection

from telegram_bot.bot import run_bot

from news_tracker.tracker import TrackerLoop


async def start_service() -> None:
    news_tracking_loop = TrackerLoop()

    loop = asyncio.get_running_loop()

    #task1 = loop.create_task(news_tracking_loop.run())

    #task2 = loop.create_task(set_db_connection())

    task3 = loop.create_task(run_bot())

    await task3


if __name__ == "__main__":

    asyncio.run(start_service())
