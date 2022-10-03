import traceback
import re
import asyncio
import feedparser
from time import mktime
from datetime import datetime, timedelta

from telegram_bot.bot import bot


def clean_str_from_html_tags(raw_html: str) -> str:
    """Очищает строку от html тегов."""
    return re.sub("<.*?>", "", raw_html)


class TrackerLoop:
    """
    Отслеживает новости по RSS ссылкам, ищет в них упоминания компаний и найденные отправляет пользователю
    для редактирования и отправки в Пульс.
    """

    def __init__(self):
        self.redactor_id = redactor_id
        self.rss_list = rss_list
        self.ticker_list = ticker_list
        self.ticker_to_company_name = ticker_to_company_name
        self.rss_feeds_last_entry_time = {}
        server_time_delta = int(datetime.strftime(datetime.now().astimezone(), '%z')[:3])
        for rrs_link in self.rss_list:
            self.rss_feeds_last_entry_time[rrs_link] = datetime.now() - timedelta(hours=server_time_delta)

    async def run(self):
        while True:
            for rrs_link in self.rss_list:
                await asyncio.sleep(1)
                while True:
                    await asyncio.sleep(1)
                    try:
                        feed = feedparser.parse(rrs_link)
                        if len(feed['entries']) == 0:
                            print(f"Пустой ответ для {rrs_link}")
                            await asyncio.sleep(5)
                            continue
                        new_feed_last_entry_time = feed['entries'][0]['published_parsed']
                        # Исправление даты новостей которые не парсятся автоматически
                        if not new_feed_last_entry_time:
                            new_feed_last_entry_time = datetime.strptime(feed['entries'][0]['published'], "%b %d, %Y %H:%M GMT")
                        else:
                            new_feed_last_entry_time = datetime.fromtimestamp(mktime(new_feed_last_entry_time))
                        old_feed_last_entry_time = self.rss_feeds_last_entry_time[rrs_link]
                        try:
                            if new_feed_last_entry_time > old_feed_last_entry_time:
                                for entry in feed['entries']:
                                    await asyncio.sleep(1)
                                    # Исправление даты новостей которые не парсятся автоматически
                                    if not entry['published_parsed']:
                                        entry_time = datetime.strptime(entry['published'], "%b %d, %Y %H:%M GMT")
                                    else:
                                        entry_time = datetime.fromtimestamp(mktime(entry['published_parsed']))
                                    if entry_time > self.rss_feeds_last_entry_time[rrs_link]:
                                        link = entry['link']
                                        title = clean_str_from_html_tags(entry['title'])
                                        try:
                                            summary = clean_str_from_html_tags(entry['summary'])
                                        except:
                                            summary = ''
                                        for ticker in self.ticker_list:
                                            if self.ticker_to_company_name[ticker] in title:
                                                await send_notice_to_user(self.redactor_id, ticker, title, summary, link)
                                            elif ticker in title:
                                                if len(ticker) > 1:
                                                    await send_notice_to_user(self.redactor_id, ticker, title, summary, link)
                                    else:
                                        break
                                self.rss_feeds_last_entry_time[rrs_link] = new_feed_last_entry_time
                            else:
                                break
                        except Exception as e:
                            print(f"Ошибка доступа к 'entry' в {rrs_link}.")
                            print(traceback.format_exc())
                            await asyncio.sleep(5)
                            continue
                        else:
                            break
                    except Exception as e:
                        print(f"Ошибка feedparser при обработке {rrs_link}.")
                        print(traceback.format_exc())
                        await asyncio.sleep(5)
                        continue
                    else:
                        break
            await asyncio.sleep(5)


async def send_notice_to_user(redactor_id_one, ticker, title, summary, link):
    if len(summary) > 7600:
        print(f"Сообщение слишком длинное - {link}")
        return
    if len(summary) > 3600:
        msg = summary.split(' ')
        summary1 = msg[:len(msg)//2]
        summary2 = msg[len(msg)//2:]
        summary1 = ' '.join(summary1)
        summary2 = ' '.join(summary2)
        msg1 = (
            f"{{${ticker}}}\n"
            f"{title}\n\n"
            f"{summary1}\n"
            '\nпродолжение 👇'
        )
        msg2 = (
            f"{summary2}\n"
            "#новости\n\n"
            f"{link}"
        )
        await bot.send_message(redactor_id_one, msg1, disable_web_page_preview=True)
        await bot.send_message(redactor_id_one, msg2, disable_web_page_preview=True)
    else:
        msg = (
            f"{{${ticker}}}\n"
            f"{title}\n\n"
            f"{summary}\n"
            "#новости\n\n"
            f"{link}"
        )
        await bot.send_message(redactor_id_one, msg, disable_web_page_preview=True)
    if len(summary) > 1000:
        try:
            ai_summary = summarize(summary)
            msg = (
                "Краткий пересказ новости👆 от Искусственного Интеллекта🤖:\n\n"
                f"{ai_summary}"
            )
            await bot.send_message(redactor_id_one, msg, disable_web_page_preview=True)
        except SberCloudSummarizeError:
            print(f"Ошибка Суммаризатора от SberCloud для новости {link}.")
