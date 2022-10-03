import os


BOT_TOKEN = os.environ.get('BOT_TOKEN')

DB_URI = os.environ.get('DATABASE_URL')

RSS_LIST = [
    "https://news.google.com/rss?hl=ru&gl=RU&ceid=RU:ru",
    "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
]
