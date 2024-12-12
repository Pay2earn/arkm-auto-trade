import os
import time
import hmac
import hashlib
import base64
import requests
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# โหลดค่า .env
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://arkm.com/api"
SYMBOL = "ETH_USDT"

def generate_signature(api_key, api_secret, method, path, body=""):
    expiry = (int(time.time()) + 300) * 1_000_000  # 5 นาทีในไมโครวินาที
    message = f"{api_key}{expiry}{method}{path}{body}"
    decoded_secret = base64.b64decode(api_secret)
    signature = hmac.new(decoded_secret, message.encode(), hashlib.sha256).digest()
    signature_base64 = base64.b64encode(signature).decode()
    return {
        "X-API-Key": api_key,
        "X-Arkham-Expires": str(expiry),
        "X-Arkham-Signature": signature_base64,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

def get_balance():
    path = "/account/balance"
    url = f"{BASE_URL}{path}"
    headers = generate_signature(API_KEY, API_SECRET, "GET", path)
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    try:
        logging.info("Fetching balance...")
        balance = get_balance()
        logging.info(f"Balance: {balance}")
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()
