import re
import requests
import asyncio
import traceback

import feedparser

from telegram_bot.bot import bot

from db import get_all_users

from config import RSS_LIST


class TrackerLoop:
    """
    Оповещает пользователей о выходе новостей.
    Время реакции 9 минут при 3-х RSS источниках.
    """

    def __init__(self) -> None:
        self.users_id_list = None
        self.users_keywords_list = None
        self.users_id_to_keywords = {}
        self.rss_list = RSS_LIST
        self.last_news_titles = None

    async def run(self) -> None:
        await asyncio.sleep(60)  # fly.io deployment process support
        await self.update_last_news_titles()  # main loop, time to execute 9 min. (from 2022-11-02 00:00) (need 70GB/month traffic or 200Kb/s)
        while True:
            await self.update_user_id_list()
            await self.update_user_id_to_keywords_dict()
            for rss_link in self.rss_list:
                try:
                    response = requests.get(rss_link, timeout=5)
                    if response.status_code == 200:
                        feed = feedparser.parse(response.content)
                        if len(feed['entries']) == 0:
                            print(f"Пустой ответ для {rss_link}")
                            continue
                        try:
                            for entry in feed['entries']:
                                title = clean_str_from_html_tags(entry['title'])
                                if title not in self.last_news_titles:
                                    link = entry['link']
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
                                    self.last_news_titles.append(title)
                                    self.last_news_titles.pop(0)
                                await asyncio.sleep(0)
                        except Exception:
                            print(f"Ошибка доступа к 'entry' в {rss_link}.")
                            print(traceback.format_exc())
                except Exception:
                    print(f"Ошибка feedparser при обработке {rss_link}.")
                    print(traceback.format_exc())
                await asyncio.sleep(0)
            await asyncio.sleep(0)

    async def update_last_news_titles(self) -> None:
        """
        Начинает работать первой. Выполняется четыре минуты.
        Обновляет словарь с последними заголовками новостей, он нужен для
        того, чтобы новости не повторялись.
        :return:
        None
        """
        self.last_news_titles = [""] * (1000 * len(self.rss_list))
        for rss_link in self.rss_list:
            while True:
                try:
                    response = requests.get(rss_link, timeout=5)
                    if response.status_code == 200:
                        feed = feedparser.parse(response.content)
                        for entry in feed['entries']:
                            title = clean_str_from_html_tags(entry['title'])
                            self.last_news_titles.append(title)
                            self.last_news_titles.pop(0)
                except Exception:
                    await asyncio.sleep(60)
                    continue
                else:
                    break
            await asyncio.sleep(0)

    async def update_user_id_list(self) -> None:
        while True:
            try:
                users = await get_all_users()
                self.users_id_list = []
                self.users_keywords_list = []
                for user in users:
                    self.users_id_list.append(user.user_id)
                    self.users_keywords_list.append(user.user_data["keywords"])
                    await asyncio.sleep(0)
            except Exception:
                continue
            else:
                return

    async def update_user_id_to_keywords_dict(self) -> None:
        for i, user_id in enumerate(self.users_id_list):
            self.users_id_to_keywords[user_id] = self.users_keywords_list[i]
            await asyncio.sleep(0)


def clean_str_from_html_tags(raw_html: str) -> str:
    """Очищает строку от html тегов."""
    string = re.sub("<.*?>", "", raw_html)
    string = re.sub("&nbsp;&nbsp;", " ", string)
    return string


async def send_notice_to_user(user_id: int, title: str, keyword: str, summary: str, link: str) -> None:

    if summary:
        summary = crop_summary(summary)
        message = (
            f"<a href='{link}'>{title}</a>\n\n"
            f"{summary}\n\n"
            f"Ключевое слово: #{keyword}"
        )
    else:
        message = (
            f"<a href='{link}'>{title}</a>\n\n"
            f"Ключевое слово: #{keyword}"
        )

    await bot.send_message(user_id, message, disable_web_page_preview=True)


def crop_summary(summary: str) -> str:
    summary_length_limit = 3000
    word_list = summary.split(" ")
    new_summary = ""
    for word in word_list:
        new_summary += f"{word} "
        if len(new_summary) >= summary_length_limit:
            new_summary += "..."
            break
    return new_summary
