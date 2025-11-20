import os
from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).parent.parent
    CONFIG_DIR = BASE_DIR / "config"
    STATIC_DIR = BASE_DIR / "static"

    CSS_FILE = STATIC_DIR / "css/style.css"
    
    MODEL_NAME = "gemini-2.5-flash"
    MODEL_TEMPERATURE = 0
    MODEL_MAX_RETRIES = 0

    API_TITLE = "Split Bill API"
    API_DESCRIPTION = "API for splitting bills based on receipt images."
    API_VERSION = "1.0.0"
    API_HOST = "0.0.0.0"
    API_PORT = 8000

    APP_PAGE_TITLE = "Split Bill App"
    APP_PAGE_ICON = STATIC_DIR / "img/favicon.ico"
    APP_LAYOUT = "wide"
    APP_MENU_ITEMS = {
        'Get Help': 'https://docs.streamlit.io/',
        'Report a bug': 'https://github.com/streamlit/streamlit/issues',
        'About': 'This site made with Streamlit and FastAPI.'
    }
    APP_CACHE_TTL = 3600
    
    PROMPT = """
    You are given an image of a receipt. Please read the content into JSON format:
    {
        "items": [
            {
                "name": <item name>,
                "quantity": <item quantity>,
                "price": <item price>
            }
        ],
        "service_price": <service price or 0>,
        "tax_price": <tax price or 0>,
        "discount_price": <discount price or 0>
    }
    Return only JSON.
    """