from typing import Optional, List, Dict
import httpx
from bs4 import BeautifulSoup
import time
from dataclasses import dataclass
import logging
import re

@dataclass
class ScrapedProduct:
    product_title: str
    product_price: float
    path_to_image: str


class WebScraper:
    def __init__(self, base_url: str, max_retries: int = 3, retry_delay: int = 5):
        self.base_url = base_url.rstrip('/')
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
    def _get_with_retry(self, url: str, proxy: Optional[str] = None) -> httpx.Response:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        proxies = None
        if proxy:
            proxies = {"http://": proxy, "https://": proxy}
            
        for attempt in range(self.max_retries):
            try:
                # Create client with follow_redirects=True
                with httpx.Client(proxies=proxies, follow_redirects=True) as client:
                    response = client.get(url, headers=headers)
                    response.raise_for_status()
                    return response
            except httpx.HTTPError as e:
                if attempt == self.max_retries - 1:
                    raise
                logging.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                time.sleep(self.retry_delay)

    def scrape_page(self, page_number: int, proxy: Optional[str] = None) -> List[ScrapedProduct]:
        url = f"{self.base_url}/page/{page_number}" if page_number > 1 else self.base_url
        logging.info(f"Scraping URL: {url}")
        
        response = self._get_with_retry(url, proxy)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all product containers
        product_containers = soup.select('li.product')
        logging.info(f"Found {len(product_containers)} products")
        
        products = []
        for product_elem in product_containers:
            try:
                # Get title
                title_elem = product_elem.select_one('h2.woo-loop-product__title a')
                if not title_elem:
                    logging.error("Could not find title element")
                    continue
                title = title_elem.text.strip()
                
                # Get price - look for sale price first, then regular price
                price_elem = product_elem.select_one('ins .woocommerce-Price-amount')
                if not price_elem:
                    # If no sale price, get regular price
                    price_elem = product_elem.select_one('.woocommerce-Price-amount')
                
                if not price_elem:
                    logging.error("Could not find price element")
                    continue
                    
                price_text = price_elem.text.strip()
                # Remove currency symbol and commas
                price = float(re.sub(r'[^\d.]', '', price_text))
                
                # Get image
                img_elem = product_elem.select_one('img.attachment-woocommerce_thumbnail')
                if not img_elem or 'src' not in img_elem.attrs:
                    logging.error("Could not find image source")
                    continue
                    
                img_src = img_elem['src']
                
                product = ScrapedProduct(
                    product_title=title,
                    product_price=price,
                    path_to_image=img_src
                )
                
                logging.info(f"Successfully scraped product: {title} - ₹{price}")
                products.append(product)
                
            except Exception as e:
                logging.error(f"Error parsing product: {str(e)}")
                continue
                
        return products
    def scrape_catalog(self, page_limit: Optional[int] = None, proxy: Optional[str] = None) -> List[ScrapedProduct]:
        all_products = []
        page = 1
        
        while True:
            try:
                logging.info(f"Scraping page {page}")
                products = self.scrape_page(page, proxy)
                
                if not products:
                    logging.info("No more products found, stopping")
                    break
                    
                logging.info(f"Found {len(products)} products on page {page}")
                all_products.extend(products)
                
                if page_limit and page >= page_limit:
                    logging.info(f"Reached page limit of {page_limit}, stopping")
                    break
                    
                page += 1
                
            except Exception as e:
                logging.error(f"Error scraping page {page}: {str(e)}", exc_info=True)
                break
                
        logging.info(f"Scraping completed. Total products found: {len(all_products)}")
        return all_products