import re
import asyncio
import traceback
from time import mktime
from datetime import datetime

import feedparser

from telegram_bot.bot import bot

from db import get_all_users
from db import get_user

from config import RSS_LIST


class TrackerLoop:

    def __init__(self) -> None:
        self.users_id_list = None
        self.rss_feeds_last_update_times = {}
        self.users_id_to_keywords = {}
        self.rss_list = RSS_LIST

    async def run(self) -> None:
        await asyncio.sleep(60)  # fly.io deployment process support
        self.update_feeds_last_update_times()
        while True:
            await self.update_user_id_list()
            await self.update_users_id_to_keywords_dict()
            for rss_link in self.rss_list:
                try:
                    feed = feedparser.parse(rss_link)
                    if len(feed['entries']) == 0:
                        print(f"Пустой ответ для {rss_link}")
                        continue
                    old_feed_update_time = self.rss_feeds_last_update_times[rss_link]
                    try:
                        for entry in feed['entries']:
                            entry_publishing_time = get_entry_publishing_time(entry)
                            if entry_publishing_time > old_feed_update_time:
                                if entry_publishing_time > self.rss_feeds_last_update_times[rss_link]:
                                    self.rss_feeds_last_update_times[rss_link] = entry_publishing_time
                                link = entry['link']
                                title = clean_str_from_html_tags(entry['title'])
                                try:
                                    summary = clean_str_from_html_tags(entry['summary'])
                                except KeyError:
                                    summary = ''
                                for user_id in self.users_id_list:
                                    for keyword in self.users_id_to_keywords[user_id]:
                                        keyword = keyword.lower()
                                        if keyword in title.lower():
                                            await send_notice_to_user(user_id, title, keyword, summary, link)
                                        elif keyword in summary.lower():
                                            await send_notice_to_user(user_id, title, keyword, summary, link)
                                        await asyncio.sleep(0)
                                    await asyncio.sleep(0)
                            await asyncio.sleep(0)
                    except Exception:
                        print(f"Ошибка доступа к 'entry' в {rss_link}.")
                        print(traceback.format_exc())
                except Exception:
                    print(f"Ошибка feedparser при обработке {rss_link}.")
                    print(traceback.format_exc())
                await asyncio.sleep(0)
            await asyncio.sleep(30)

    def update_feeds_last_update_times(self) -> None:
        now = datetime.utcnow()
        for rrs_link in self.rss_list:
            self.rss_feeds_last_update_times[rrs_link] = now

    async def update_user_id_list(self) -> None:
        users = await get_all_users()
        self.users_id_list = []
        for user in users:
            self.users_id_list.append(user.user_id)
            await asyncio.sleep(0)

    async def update_users_id_to_keywords_dict(self) -> None:
        for user_id in self.users_id_list:
            user = await get_user(user_id)
            self.users_id_to_keywords[user_id] = user.user_data["keywords"]


def get_entry_publishing_time(entry: dict) -> datetime:

    entry_update_time = entry['published_parsed']

    # Исправление даты новостей которые не парсятся автоматически
    if not entry_update_time:
        entry_update_time = datetime.strptime(entry['published'], "%b %d, %Y %H:%M GMT")
    else:
        entry_update_time = datetime.fromtimestamp(mktime(entry_update_time))

    return entry_update_time


def clean_str_from_html_tags(raw_html: str) -> str:
    """Очищает строку от html тегов."""
    string = re.sub("<.*?>", "", raw_html)
    string = re.sub("&nbsp;&nbsp;", " ", string)
    return string


async def send_notice_to_user(user_id: int, title: str, keyword: str, summary: str, link: str) -> None:

    max_summary_length = 3000
    summary_list = [summary[i:(i + max_summary_length)] for i in range(0, len(summary), max_summary_length)]

    for i, _summary in enumerate(summary_list):
        if i == len(summary_list):
            message = (
                f"Ключевое слово: #{keyword}\n\n"
                f"{title}\n\n"
                f"<a href='{link}'>Ссылка на новость</a>\n\n"
                f"{_summary}"
            )
        else:
            if i == 0:
                message = (
                    f"Ключевое слово: #{keyword}\n\n"
                    f"{title}\n\n"
                    f"<a href='{link}'>Ссылка на новость</a>\n\n"
                    f"{_summary}\n\n"
                    "продолжение 👇"
                )
            elif i == len(summary_list):
                message = (
                    f"{_summary}"
                )
            else:
                message = (
                    f"{_summary}\n\n"
                    "продолжение 👇"
                )
        await bot.send_message(user_id, message, disable_web_page_preview=True)
