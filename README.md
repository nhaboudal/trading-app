# Flask Stock & News Application

## Overview

This project is a Flask-based web application that provides stock market data and the latest news for a given company. Users can search by stock symbol (e.g., AMZN for Amazon) and retrieve:

- Current stock price
- Daily stock performance (opening, closing, high, low prices)
- After-hours trading information
- The latest news articles related to the company (excluding Yahoo articles)

## Features

- **Stock Data**: Fetches current and daily stock data (open, close, high, low) for a company using the [Polygon.io API](https://polygon.io/).
- **News Articles**: Displays the latest news articles related to the company using the [NewsAPI.org](https://newsapi.org/) (excluding Yahoo articles).
- **Interactive Stock Chart**: Displays a graph of today's stock performance.
- **Responsive Design**: Optimized for both desktop and mobile.
- **Built with Flask**: A lightweight Python web framework.

## Technologies Used

- **Backend**: Flask (Python)
- **APIs**: 
  - Polygon.io (for stock data)
  - NewsAPI (for news articles)
- **Frontend**: HTML, CSS, Jinja2 templating, Chart.js (for the stock performance graph)
- **Deployment**: Can be hosted on any Python-compatible platform (e.g., Heroku, DigitalOcean, etc.)


## Prerequisites

To run this app locally, you need the following installed:

- Python 3.x
- pip (Python package installer)
- An account on [Polygon.io](https://polygon.io/) and [NewsAPI.org](https://newsapi.org/) to get API keys.

