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
from dotenv import load_dotenv  # เพิ่มการใช้งาน dotenv
import os

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# โหลดค่าจากไฟล์ .env
load_dotenv()

# ดึงค่า API Key และ API Secret จาก .env
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = os.getenv("BASE_URL", "https://arkm.com/api")  # กำหนด URL พื้นฐานจาก .env ถ้าไม่มีจะใช้ค่า default
SYMBOL = "ETH_USDT"
TRADE_AMOUNT = 0.02

PROFIT_TARGET = 0.0004  # 0.03% profit target
LOSS_CUTOFF = 0.001    # 0.1% stop-loss cutoff
WAIT_TIME = 60         # Wait time in seconds if no sell occurs

# ตัวแปรสำหรับติดตามสถิติ
wins = 0
losses = 0
total_profit = 0
total_loss = 0
total_volume = 0

# ฟังก์ชันสำหรับสร้าง signature
def generate_signature(api_key, api_secret, method, path, body=""):
    expiry = (int(time.time()) + 300) * 1000000  # ตั้งเวลา expiration 5 นาที
    message = f"{api_key}{expiry}{method}{path}{body}"
    decoded_secret = base64.b64decode(api_secret)
    signature = hmac.new(decoded_secret, message.encode(), hashlib.sha256).digest()  # แก้ไขที่นี่
    signature_base64 = base64.b64encode(signature).decode()
    return {
        "Arkham-Api-Key": api_key,
        "Arkham-Expires": str(expiry),
        "Arkham-Signature": signature_base64,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

# ฟังก์ชันหลักในการทำการซื้อและขาย
def trade():
    # ตัวอย่างการซื้อและขาย
    logging.info("Starting trade process...")

    # คำขอซื้อ
    path = f"/v1/order"
    body = {
        "symbol": SYMBOL,
        "amount": TRADE_AMOUNT,
        "side": "buy",
        "price": fetch_price(SYMBOL)
    }
    headers = generate_signature(API_KEY, API_SECRET, 'POST', path, json.dumps(body))
    url = BASE_URL + path
    response = requests.post(url, headers=headers, data=json.dumps(body))
    if response.status_code == 200:
        logging.info(f"Successfully bought {TRADE_AMOUNT} {SYMBOL}.")
    else:
        logging.error(f"Error in buying: {response.json()}")

    # ตรวจสอบราคาและขาย
    current_price = fetch_price(SYMBOL)
    if current_price:
        buy_price = current_price
        logging.info(f"Buy price: {buy_price}")
        start_time = time.time()

        while True:
            current_price = fetch_price(SYMBOL)
            if current_price >= buy_price * (1 + PROFIT_TARGET):  # หากราคาเพิ่มขึ้นตามเป้าหมาย
                logging.info(f"Price reached target, selling at {current_price}")
                # คำขอขาย
                body = {
                    "symbol": SYMBOL,
                    "amount": TRADE_AMOUNT,
                    "side": "sell",
                    "price": current_price
                }
                response = requests.post(url, headers=headers, data=json.dumps(body))
                if response.status_code == 200:
                    logging.info(f"Successfully sold {TRADE_AMOUNT} {SYMBOL} at {current_price}.")
                    break
                else:
                    logging.error(f"Error in selling: {response.json()}")
                    break
            elif time.time() - start_time > WAIT_TIME:  # ถ้ารอเกินเวลาที่กำหนด
                logging.info("Force selling after waiting for too long.")
                body = {
                    "symbol": SYMBOL,
                    "amount": TRADE_AMOUNT,
                    "side": "sell",
                    "price": current_price
                }
                response = requests.post(url, headers=headers, data=json.dumps(body))
                if response.status_code == 200:
                    logging.info(f"Successfully sold {TRADE_AMOUNT} {SYMBOL} at {current_price}.")
                    break
                else:
                    logging.error(f"Error in selling: {response.json()}")
                    break
            time.sleep(1)

# ฟังก์ชันสำหรับดึงราคา
def fetch_price(symbol):
    path = f"/v1/market/{symbol}"
    headers = generate_signature(API_KEY, API_SECRET, 'GET', path)
    url = BASE_URL + path
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['data']['last_price']  # ดึงราคาล่าสุด
    else:
        logging.error(f"Error fetching price for {symbol}: {response.json()}")
        return None

if __name__ == "__main__":
    trade()
