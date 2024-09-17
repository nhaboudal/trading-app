import aiohttp  # For making asynchronous requests
import asyncio
from flask import Flask, render_template, request
from datetime import datetime
import pytz

app = Flask(__name__)

# API configuration
POLYGON_API_KEY = 'NcJlUHEovU5uBOkCTR6JefSbjpnFxyNb'  # Replace with your actual Polygon.io API key
POLYGON_BASE_URL = 'https://api.polygon.io'
NEWS_API_KEY = 'e12650cd28f04043bbae415354c3b349'  # Replace with your actual NewsAPI key
NEWS_API_URL = 'https://newsapi.org/v2/everything'

# Fetch the full company name from Polygon.io
async def get_company_name(symbol):
    url = f"{POLYGON_BASE_URL}/v3/reference/tickers/{symbol}"
    params = {'apiKey': POLYGON_API_KEY}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()

    # Ensure we have a valid response with results
    if 'results' in data and 'name' in data['results']:
        return data['results']['name']  # Return the company name
    else:
        print(f"Error: Could not fetch company name for symbol {symbol}. Response: {data}")
        return symbol  # Fallback to symbol if no name is found

# Fetch stock data from Polygon.io (daily close prices)
async def get_stock_data(symbol):
    url = f"{POLYGON_BASE_URL}/v2/aggs/ticker/{symbol}/prev"
    params = {'apiKey': POLYGON_API_KEY}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()

    # Check if the API returned an error or if 'results' is missing
    if 'results' not in data:
        print(f"Error: No results found for symbol {symbol}. Response: {data}")
        return {
            'symbol': symbol,
            'close_price': 0,
            'open_price': 0,
            'high_price': 0,
            'low_price': 0,
            'daily_change': 0,
            'daily_percentage_change': 0,
            'after_hours_price': 0,
            'current_datetime': datetime.now().strftime("%b %d, %Y, %I:%M %p %Z")
        }

    close_price = data['results'][0].get('c', 0)
    open_price = data['results'][0].get('o', 0)
    high_price = data['results'][0].get('h', 0)
    low_price = data['results'][0].get('l', 0)
    after_hours_price = close_price - 0.37 if close_price else 0
    daily_change = close_price - open_price if open_price else 0
    daily_percentage_change = (daily_change / open_price * 100) if open_price else 0

    timezone = pytz.timezone('America/New_York')
    current_datetime = datetime.now(timezone).strftime("%b %d, %Y, %I:%M %p %Z")

    return {
        'symbol': symbol,
        'close_price': close_price,
        'open_price': open_price,
        'high_price': high_price,
        'low_price': low_price,
        'daily_change': daily_change,
        'daily_percentage_change': daily_percentage_change,
        'after_hours_price': after_hours_price,
        'current_datetime': current_datetime
    }

# Fetch hourly stock data from Polygon.io
async def get_hourly_stock_data(symbol):
    # Get today's date to fetch hourly data for today
    today = datetime.now().strftime('%Y-%m-%d')
    url = f"{POLYGON_BASE_URL}/v2/aggs/ticker/{symbol}/range/1/hour/{today}/{today}"
    params = {'apiKey': POLYGON_API_KEY}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()

    if 'results' not in data:
        print(f"Error: No hourly data found for symbol {symbol}. Response: {data}")
        return []

    return data['results']  # Returns the list of hourly stock data

# Fetch relevant news articles using the /v2/everything endpoint and ignore Yahoo articles
async def get_news_articles(company_name):
    url = NEWS_API_URL

    params = {
        'q': company_name,  # Search for the company name in the news
        'searchIn': 'title,description',  # Search in title and description
        'pageSize': 3,  # Limit the results to 3 articles
        'language': 'en',  # Fetch only English-language news
        'sortBy': 'publishedAt',  # Sort by the most recent articles
        'apiKey': NEWS_API_KEY
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            news_data = await response.json()

    # Check if the API response status is 'ok' and contains articles
    if news_data.get('status') == 'ok' and 'articles' in news_data:
        # Filter out articles that come from Yahoo (by checking 'source' or 'url')
        filtered_articles = [
            article for article in news_data['articles']
            if 'yahoo.com' not in article['url'].lower() and 'yahoo' not in article.get('source', {}).get('name', '').lower()
        ]
        return filtered_articles[:3]  # Return up to 3 non-Yahoo articles
    else:
        print(f"Error fetching news for {company_name}: {news_data}")
        return []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/quote', methods=['POST'])
async def quote():
    symbol = request.form['symbol'].upper()

    # Fetch the full company name dynamically from Polygon.io
    company_name = await get_company_name(symbol)

    # Run stock data, hourly data, and news fetching in parallel
    stock_data, hourly_stock_data, news_articles = await asyncio.gather(
        get_stock_data(symbol),
        get_hourly_stock_data(symbol),
        get_news_articles(company_name)
    )

    # Pass both the stock data, hourly data, and the news articles to the template
    return render_template('quote.html', **stock_data, hourly_stock_data=hourly_stock_data, company_name=company_name, news_articles=news_articles)

# Format datetime for the news
@app.template_filter('datetimeformat')
def datetimeformat(value):
    try:
        date = datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
        return date.strftime('%b %d, %Y, %I:%M %p %Z')
    except ValueError:
        return value

if __name__ == '__main__':
    app.run(debug=True)