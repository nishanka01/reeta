import requests
from typing import Dict, Any, List
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

def get_weather(location: str) -> str:
    """
    Get the current weather for a specific city or location.
    
    Args:
        location: The name of the city (e.g., "London", "New York").
    """
    if not settings.OPENWEATHERMAP_API_KEY:
        return "Weather API key is not configured."
        
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={settings.OPENWEATHERMAP_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            return f"The current weather in {location} is {temp}°C with {desc}."
        return f"Could not fetch weather: {data.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Weather tool error: {e}")
        return "An error occurred while fetching the weather."

def get_stock_price(ticker: str) -> str:
    """
    Get the current stock price for a given ticker symbol.
    
    Args:
        ticker: The stock ticker symbol (e.g., "AAPL", "MSFT").
    """
    if not settings.ALPHAVANTAGE_API_KEY:
        return "Stock API key is not configured."
        
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={settings.ALPHAVANTAGE_API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        if "Global Quote" in data and "05. price" in data["Global Quote"]:
            price = data["Global Quote"]["05. price"]
            return f"The current price of {ticker} is ${float(price):.2f}."
        elif "Information" in data:
            return "API rate limit reached for stock data."
        return f"Could not fetch stock price for {ticker}."
    except Exception as e:
        logger.error(f"Stock tool error: {e}")
        return "An error occurred while fetching the stock price."

def get_news(topic: str = "general") -> str:
    """
    Get the latest top news headlines, optionally for a specific topic.
    
    Args:
        topic: The topic to search for (e.g., "technology", "sports", "general").
    """
    if not settings.NEWSAPI_KEY:
        return "News API key is not configured."
        
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&category={topic}&apiKey={settings.NEWSAPI_KEY}"
        if topic not in ["business", "entertainment", "general", "health", "science", "sports", "technology"]:
             # Fallback to everything search if it's not a standard category
             url = f"https://newsapi.org/v2/everything?q={topic}&sortBy=relevancy&apiKey={settings.NEWSAPI_KEY}"
             
        response = requests.get(url)
        data = response.json()
        
        if data.get("status") == "ok":
            articles = data.get("articles", [])[:3]
            if not articles:
                return f"No recent news found for {topic}."
            
            headlines = [f"- {a['title']}" for a in articles]
            return f"Top news for {topic}:\n" + "\n".join(headlines)
        return "Could not fetch news at this time."
    except Exception as e:
        logger.error(f"News tool error: {e}")
        return "An error occurred while fetching the news."

def get_route(origin: str, destination: str) -> str:
    """
    Get driving directions or route information between two locations.
    
    Args:
        origin: The starting location.
        destination: The destination location.
    """
    # Note: A full openrouteservice integration requires geocoding first.
    # For simplicity, we just return a placeholder or use a simpler direct lookup if possible.
    if not settings.OPENROUTESERVICE_API_KEY:
        return "Routing API key is not configured."
        
    return f"Routing from {origin} to {destination} requires geocoding which is complex. Suggest checking Google Maps."

# List of all tools available to the LLM
AVAILABLE_TOOLS = [get_weather, get_stock_price, get_news, get_route]
