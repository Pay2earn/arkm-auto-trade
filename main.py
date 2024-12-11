import requests
from dotenv import load_dotenv
import os

class ARKMAutoTrade:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("API_KEY")
        self.api_secret = os.getenv("API_SECRET")
        self.base_url = "https://arkm.com/api"

        if not self.api_key or not self.api_secret:
            raise ValueError("API_KEY or API_SECRET is missing")

    def get_balance(self):
        """ดึงยอดคงเหลือจาก ARKM"""
        endpoint = f"{self.base_url}/balance"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        return response.json()

    def buy(self, symbol, amount, price):
        """ทำการซื้อ"""
        endpoint = f"{self.base_url}/buy"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {
            "symbol": symbol, 
            "amount": amount, 
            "price": price
        }
        response = requests.post(endpoint, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def sell(self, symbol, amount, price):
        """ทำการขาย"""
        endpoint = f"{self.base_url}/sell"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {
            "symbol": symbol, 
            "amount": amount, 
            "price": price
        }
        response = requests.post(endpoint, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    bot = ARKMAutoTrade()

    # เช็คยอดคงเหลือ
    balance = bot.get_balance()
    print("Balance:", balance)

    # ซื้อ BTC/USDT
    buy_response = bot.buy("BTC_USDT", 0.001, 50000)
    print("Buy Response:", buy_response)

    # ขาย BTC/USDT
    sell_response = bot.sell("BTC_USDT", 0.001, 51000)
    print("Sell Response:", sell_response)
