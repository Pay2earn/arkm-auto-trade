import time
import hmac
import hashlib
import base64
import requests
import logging
import os
from dotenv import load_dotenv

# โหลดตัวแปรจากไฟล์ .env
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# ดึง API_KEY และ API_SECRET จาก .env
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://arkm.com/api"
SYMBOL = "ETH_USDT"
TRADE_AMOUNT = 0.02

PROFIT_TARGET = 0.0004  # 0.03% profit target
LOSS_CUTOFF = 0.001    # 0.1% stop-loss cutoff
WAIT_TIME = 60         # Wait time in seconds if no sell occurs

# ตรวจสอบค่าที่ดึงมาจาก .env
if API_KEY is None or API_SECRET is None:
    logging.error("Error: API_KEY or API_SECRET is not set in the .env file")
else:
    logging.info("Successfully loaded API_KEY and API_SECRET from .env")

# Statistics tracking
wins = 0
losses = 0
total_profit = 0
total_loss = 0
total_volume = 0

def generate_signature(api_key, api_secret, method, path, body=""):
    expiry = (int(time.time()) + 300) * 1000000
    message = f"{api_key}{expiry}{method}{path}{body}"
    decoded_secret = base64.b64decode(api_secret)
    signature = hmac.new(decoded_secret, message.encode(), hashlib.sha256).digest()
    signature_base64 = base64.b64encode(signature).decode()
    return {
        "Arkham-Api-Key": api_key,
        "Arkham-Expires": str(expiry),
        "Arkham-Signature": signature_base64,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

def fetch_data_from_api(path):
    logging.info(f"Preparing to fetch data from API endpoint: {path}")
    method = "GET"
    headers = generate_signature(API_KEY, API_SECRET, method, path)
    url = f"{BASE_URL}/{path}"
    try:
        logging.info(f"Sending request to {url}...")
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            logging.info("Data fetched successfully.")
            return response.json()
        else:
            logging.error(f"Failed to fetch data: {response.status_code}, {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data: {e}")
        return None

def start_trading():
    logging.info("Starting the trading bot...")
    
    # Fetch trade data
    trade_data = fetch_data_from_api("trade_data")
    if trade_data:
        logging.info(f"Trade data: {trade_data}")
        # Process trade logic here...
        logging.info("Trading process completed.")
    else:
        logging.error("Unable to fetch trade data. Aborting trading.")

if __name__ == "__main__":
    start_trading()
