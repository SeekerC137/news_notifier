import os


BOT_TOKEN = os.environ.get('BOT_TOKEN')

DB_URI = os.environ.get('DATABASE_URL')

RSS_LIST = [
    "http://www.cbr.ru/rss/RssNews",  # Новое на сайте
    "https://www.cbr.ru/rss/eventrss",  # Новости, интервью, выступления
    "https://www.cbr.ru/rss/RssPress",  # Пресс-релизы Банка России
    "https://www.cbr.ru/rss/RssCurrency",  # Курсы валют Банка России устанавливаемые ежедневно
    "https://www.cbr.ru/rss/nregimr2",  # Информация выполнения регламента обработки электронных документов (МЦИ)
    #"https://news.google.com/rss?hl=ru&gl=RU&ceid=RU:ru",
    #"https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    #"https://www.interfax.ru/rss.asp",
]
