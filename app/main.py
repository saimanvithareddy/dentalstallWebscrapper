from dotenv import load_dotenv
load_dotenv() 

from fastapi import FastAPI, HTTPException, Depends, Header
from typing import Optional
from pydantic import BaseModel
import os
import logging

from .scraper.scraper import WebScraper
from .storage.storage import JsonFileStorage
from .notification.notifications import ConsoleNotification, EmailNotification
from .cache.cache import CacheManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = FastAPI()

API_TOKEN = os.getenv("API_TOKEN")
REDIS_URL = os.getenv("REDIS_URL")
BASE_URL = os.getenv("BASE_URL")
STORAGE_PATH = os.getenv("STORAGE_PATH")

smtp_settings = {
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', '587')),
    'sender_email': os.getenv('SENDER_EMAIL'),
    'sender_password': os.getenv('SENDER_PASSWORD'),
    'recipients': os.getenv('NOTIFICATION_RECIPIENTS', '').split(',')
}

storage = JsonFileStorage(STORAGE_PATH)
cache_manager = CacheManager(REDIS_URL)
console_notification = ConsoleNotification()

class ScrapeRequest(BaseModel):
    page_limit: Optional[int] = None
    proxy: Optional[str] = None

async def verify_token(api_token: str = Header(...)):
    if api_token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API token")
    return api_token

# Initialize email notification
try:
    email_notification = EmailNotification(smtp_settings)
    logging.info("Email notification service initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize email notification: {str(e)}")
    email_notification = None

@app.get("/")
async def root():
    return {"message": "hello world"}

@app.get("/test")
async def test_endpoint():
    return {"status": "Working!", "setup": "completed"}

@app.get("/getCustomMessage")
async def get_custom_message(message: str):
    return {"status": "success", "custom_message": message}

@app.post("/scrape")
async def scrape_products(
    request: ScrapeRequest,
    api_token: str = Depends(verify_token)
):
    try:
        scraper = WebScraper(BASE_URL)
        products = scraper.scrape_catalog(
            page_limit=request.page_limit,
            proxy=request.proxy
        )
        
        updated_count = storage.save_products(products)
        message = f"Scraping completed: {len(products)} products scraped, {updated_count} products updated"
        
        console_notification.notify(message)
        
        if email_notification:
            try:
                email_notification.notify(message)
                logging.info("Email notification sent successfully")
            except Exception as e:
                logging.error(f"Failed to send email notification: {str(e)}")
        
        return {
            "status": "success",
            "products_scraped": len(products),
            "products_updated": updated_count
        }
        
    except Exception as e:
        logging.error(f"Scraping error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)