from fastapi import FastAPI, HTTPException, Depends, Header
from typing import Optional
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from .scraper.scraper import WebScraper
from .storage.storage import JsonFileStorage
from .notification.notifications import ConsoleNotification,EmailNotification
from .cache.cache import CacheManager
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = FastAPI()

API_TOKEN = os.getenv("API_TOKEN", "manvitha")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
BASE_URL = os.getenv("BASE_URL", "https://dentalstall.com/shop/")
STORAGE_PATH = os.getenv("STORAGE_PATH", "products.json")

smtp_settings = {
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', '587')),
    'sender_email': os.getenv('SENDER_EMAIL'),
    'sender_password': os.getenv('SENDER_PASSWORD'),
    'recipients': os.getenv('NOTIFICATION_RECIPIENTS', '').split(',')
}
logging.info("SMTP Settings (excluding password):")
logging.info(f"Server: {smtp_settings['smtp_server']}")
logging.info(f"Port: {smtp_settings['smtp_port']}")
logging.info(f"Sender: {smtp_settings['sender_email']}")
logging.info(f"Recipients: {smtp_settings['recipients']}")

storage = JsonFileStorage(STORAGE_PATH)
notifier = ConsoleNotification()
cache_manager = CacheManager(REDIS_URL)

console_notification = ConsoleNotification()
# email_notification = EmailNotification(smtp_settings)


class ScrapeRequest(BaseModel):
    page_limit: Optional[int] = None
    proxy: Optional[str] = None

async def verify_token(api_token: str = Header(...)):
    if api_token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API token")
    return api_token

@app.get("/")
async def root():
    return {"message" : "hello world"}


@app.get("/test")
async def test_endpoint():
    return {"status": "Working!", "setup": "completed"}

@app.get("/getCustomMessage")
async def get_custom_message(message : str):
    return {"status": "success","custom_message" :message}

@app.post("/scrape")
async def scrape_products(
    request: ScrapeRequest,
    api_token: str = Depends(verify_token)
):
    try:
        # Initialize scraper
        scraper = WebScraper(BASE_URL)
        
        # Perform scraping
        products = scraper.scrape_catalog(
            page_limit=request.page_limit,
            proxy=request.proxy
        )
        
        # Update storage and get count of updated products
        updated_count = storage.save_products(products)
        message = f"Scraping completed: {len(products)} products scraped, {updated_count} products updated"
        
        # Send notification
        console_notification.notify(message)
        # email_notification.notify(message)
        
        return {
            "status": "success",
            "products_scraped": len(products),
            "products_updated": updated_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)