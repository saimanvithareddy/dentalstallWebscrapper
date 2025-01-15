from abc import ABC, abstractmethod
import json
from typing import List, Dict, Optional
import os
from ..scraper.scraper import ScrapedProduct

class StorageStrategy(ABC):
    @abstractmethod
    def save_products(self, products: List[ScrapedProduct]) -> int:
        pass
        
    @abstractmethod
    def get_product(self, product_title: str) -> Optional[Dict]:
        pass

class JsonFileStorage(StorageStrategy):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_file_exists()
        
    def _ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)
                
    def get_product(self, product_title: str) -> Optional[Dict]:
        with open(self.file_path, 'r') as f:
            products = json.load(f)
            for product in products:
                if product['product_title'] == product_title:
                    return product
        return None
        
    def save_products(self, products: List[ScrapedProduct]) -> int:
        existing_products = []
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                existing_products = json.load(f)
                
        updated_count = 0
        for product in products:
            product_dict = {
                'product_title': product.product_title,
                'product_price': product.product_price,
                'path_to_image': product.path_to_image
            }
            
            # Update or append product
            found = False
            for existing_product in existing_products:
                if existing_product['product_title'] == product.product_title:
                    if existing_product['product_price'] != product.product_price:
                        existing_product.update(product_dict)
                        updated_count += 1
                    found = True
                    break
                    
            if not found:
                existing_products.append(product_dict)
                updated_count += 1
                
        with open(self.file_path, 'w') as f:
            json.dump(existing_products, f, indent=2)
            
        return updated_count
