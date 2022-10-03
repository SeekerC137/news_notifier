import asyncio

from telegram_bot.bot import run_bot

from news_tracker.tracker import TrackerLoop


def start_service() -> None:
    loop = TrackerLoop()
    coroutines = [
        run_bot(),
        loop.run(),
    ]
    asyncio.run(asyncio.wait(coroutines))


if __name__ == "__main__":

    start_service()
