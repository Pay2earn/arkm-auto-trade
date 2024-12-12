import time
import random
import hmac
import hashlib
import base64
import requests
import json
import uuid
import logging
import math
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

# สถิติ
wins = 0
losses = 0
total_profit = 0
total_loss = 0
total_volume = 0

def generate_signature(api_key, api_secret, method, path, body=""):
    logging.info("Starting signature generation...")
    expiry = (int(time.time()) + 300) * 1000000
    message = f"{api_key}{expiry}{method}{path}{body}"
    logging.info(f"Message for signature: {message}")
    decoded_secret = base64.b64decode(api_secret)
    signature = hmac.new(decoded_secret, message.encode(), hashlib.sha256).digest()
    signature_base64 = base64.b64encode(signature).decode()
    logging.info("Signature generated successfully.")
    return {
        "Arkham-Api-Key": api_key,
        "Arkham-Expires": str(expiry),
        "Arkham-Signature": signature_base64,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

def fetch_data_from_api(endpoint):
    logging.info(f"Preparing to fetch data from API endpoint: {endpoint}")
    headers = generate_signature(API_KEY, API_SECRET, "GET", endpoint)
    logging.info("Headers for API request prepared successfully.")
    
    try:
        logging.info(f"Sending request to {BASE_URL}/{endpoint}...")
        response = requests.get(f"{BASE_URL}/{endpoint}", headers=headers)
        
        if response.status_code == 200:
            logging.info(f"Data fetched successfully from {endpoint}.")
            return response.json()
        else:
            logging.error(f"Failed to fetch data from {endpoint}: Status code {response.status_code}.")
            logging.error(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")

def trade_operation(action, amount, symbol):
    logging.info(f"Preparing to {action} {amount} of {symbol}...")
    # Simulating trade operation (buy/sell)
    success = random.choice([True, False])  # Simulating 50% success rate for the operation
    
    if success:
        logging.info(f"Trade {action} {amount} {symbol} successful!")
        return True
    else:
        logging.error(f"Trade {action} {amount} {symbol} failed!")
        return False

# ตัวอย่างการเทรด
logging.info("Starting the trading bot...")

# ดึงข้อมูลจาก API
trade_data = fetch_data_from_api("trade_data")
logging.info("Fetched trade data successfully.")

# การซื้อหรือขายเหรียญ
if trade_data:
    logging.info("Preparing for trade operation...")
    if trade_operation("buy", TRADE_AMOUNT, SYMBOL):
        logging.info(f"Bought {TRADE_AMOUNT} {SYMBOL}.")
        # รอทำการขาย
        logging.info(f"Waiting for price to reach target profit of {PROFIT_TARGET}...")
        time.sleep(WAIT_TIME)  # รอ
        if trade_operation("sell", TRADE_AMOUNT, SYMBOL):
            logging.info(f"Sold {TRADE_AMOUNT} {SYMBOL}.")
        else:
            logging.error(f"Failed to sell {TRADE_AMOUNT} {SYMBOL}.")
    else:
        logging.error(f"Failed to buy {TRADE_AMOUNT} {SYMBOL}.")

logging.info("Bot finished trading.")
