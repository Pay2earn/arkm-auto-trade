import requests
from dotenv import load_dotenv
import os

class ARKMAutoTrade:
    def __init__(self):
        # โหลดค่าคอนฟิกจาก .env
        load_dotenv()
        self.api_key = os.getenv("API_KEY")
        self.api_secret = os.getenv("API_SECRET")
        self.base_url = os.getenv("API_BASE_URL")
        self.default_price = float(os.getenv("DEFAULT_ITEM_PRICE", 100.0))
        
        if not self.api_key or not self.api_secret:
            raise ValueError("API_KEY or API_SECRET is missing in the environment configuration.")

    def get_items(self):
        """ดึงรายการสินค้าจาก ARKM"""
        endpoint = f"{self.base_url}/items"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        return response.json()

    def buy_item(self, item_id, price):
        """สั่งซื้อสินค้า"""
        endpoint = f"{self.base_url}/buy"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {"item_id": item_id, "price": price}
        response = requests.post(endpoint, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def sell_item(self, item_id, price):
        """ขายสินค้า"""
        endpoint = f"{self.base_url}/sell"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {"item_id": item_id, "price": price}
        response = requests.post(endpoint, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
