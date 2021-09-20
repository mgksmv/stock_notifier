import requests
import os
from dotenv import load_dotenv

load_dotenv('.env')

# Set up a stock symbol and a company name you're interested in.
# You can find symbols here: https://www.nasdaq.com/market-activity/stocks/screener
STOCK = os.getenv('STOCK')
COMPANY_NAME = os.getenv('COMPANY_NAME')

# Set up Alphavantage API Key (https://www.alphavantage.co), News API Key (https://newsapi.org)
# and Telegram Bot API Key (search for @BotFather in Telegram)
ALPHAVANTAGE_API_KEY = os.getenv('ALPHAVANTAGE_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
BOT_API_KEY = os.getenv('BOT_API_KEY')

# Set up your Telegram user ID (search for @userinfobot)
USER_ID = os.getenv('CHAT_ID')


def percentage_change():
    endpoint = 'https://www.alphavantage.co/query'
    parameters = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': STOCK,
        'apikey': ALPHAVANTAGE_API_KEY,
    }

    response = requests.get(endpoint, params=parameters)
    data = response.json()

    yesterday = list(data['Time Series (Daily)'].keys())[0]
    day_before_yesterday = list(data['Time Series (Daily)'].keys())[1]
    yesterday_close_price = data['Time Series (Daily)'][yesterday]['4. close']
    day_before_yesterday_close_price = data['Time Series (Daily)'][day_before_yesterday]['4. close']

    result = round((float(yesterday_close_price) - float(day_before_yesterday_close_price)) / float(
        day_before_yesterday_close_price) * 100)
    return result


def get_articles():
    endpoint = 'https://newsapi.org/v2/everything'
    parameters = {
        'qInTitle': COMPANY_NAME,
        'sortBy': 'publishedAt',
        'apiKey': NEWS_API_KEY,
    }

    response = requests.get(endpoint, params=parameters)
    response.raise_for_status()

    three_articles = response.json()['articles'][:3]
    return three_articles


if percentage_change() >= 5 or percentage_change() <= -5:
    if percentage_change() > 0:
        arrow = '🔺'
    else:
        arrow = '🔻'
    articles = [f"{article['title']}\n{article['url']}\n\n" for article in get_articles()]

    bot_endpoint = f'https://api.telegram.org/bot{BOT_API_KEY}/sendMessage'
    bot_parameters = {
        'chat_id': USER_ID,
        'text': f"{COMPANY_NAME}: {arrow} {percentage_change()}%\n\n"
                f"{articles[0]}"
                f"{articles[1]}"
                f"{articles[2]}",
    }

    response = requests.post(bot_endpoint, params=bot_parameters)
    response.raise_for_status()
