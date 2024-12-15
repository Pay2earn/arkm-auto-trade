import time
import hmac
import hashlib
import base64
import requests
import os
from dotenv import load_dotenv
import logging

# โหลด environment variables จาก .env
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://arkm.com/api"
SYMBOL = "ETH_USDT"
THRESHOLD_PRICE = 3500  # ราคาที่ตั้งไว้เพื่อซื้อ
TRADE_AMOUNT = 0.02
PROFIT_TARGET = 1.01  # เป้าหมายกำไร 1%
MAX_WAIT = 120         # เวลารอสูงสุดสำหรับการขาย

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def generate_signature(api_key, api_secret, method, path, body=""):
    """ฟังก์ชันในการสร้างลายเซ็นต์ HMAC"""
    expiry = (int(time.time()) + 300) * 1000000  # กำหนดเวลาหมดอายุ 5 นาที
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

def login():
    """ฟังก์ชันสำหรับการล็อกอินเข้าสู่ระบบ ARMK API"""
    path = "/login"
    method = "GET"
    body = ""
    headers = generate_signature(API_KEY, API_SECRET, method, path, body)
    
    response = requests.get(BASE_URL + path, headers=headers)
    if response.status_code == 200:
        logging.info("Login successful")
        return True
    else:
        logging.error(f"Login failed: {response.status_code}")
        return False

def fetch_price(symbol):
    """ฟังก์ชันดึงราคาปัจจุบันของคู่เหรียญ"""
    path = f"/market/{symbol}"
    method = "GET"
    body = ""
    headers = generate_signature(API_KEY, API_SECRET, method, path, body)
    
    response = requests.get(BASE_URL + path, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return float(data['price'])
    else:
        logging.error(f"Error fetching price for {symbol}: {response.status_code}")
        return None

def place_order(symbol, side, price, quantity):
    """ฟังก์ชันสำหรับการวางคำสั่งซื้อหรือขาย"""
    path = "/order"
    method = "POST"
    body = json.dumps({
        "symbol": symbol,
        "side": side,  # 'buy' หรือ 'sell'
        "price": price,
        "quantity": quantity
    })
    headers = generate_signature(API_KEY, API_SECRET, method, path, body)
    
    response = requests.post(BASE_URL + path, data=body, headers=headers)
    if response.status_code == 200:
        logging.info(f"Order placed: {response.json()}")
        return response.json()
    else:
        logging.error(f"Error placing order: {response.status_code}")
        return None

def get_balance():
    """ฟังก์ชันดึงยอดคงเหลือในบัญชี"""
    path = "/balance"
    method = "GET"
    body = ""
    headers = generate_signature(API_KEY, API_SECRET, method, path, body)
    
    response = requests.get(BASE_URL + path, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['balance']
    else:
        logging.error(f"Error fetching balance: {response.status_code}")
        return 0

def trade(symbol, threshold, max_wait_time=10):
    """ฟังก์ชันหลักในการเทรด"""
    while True:
        balance = get_balance()
        if balance <= 0:
            logging.info("Balance is zero, stopping trading.")
            break

        # ดึงราคาปัจจุบัน
        current_price = fetch_price(symbol)
        if current_price is None:
            continue

        logging.info(f"Current price of {symbol}: {current_price}")

        if current_price < threshold:
            # ถ้าราคาต่ำกว่าราคาที่ตั้งไว้ ให้ทำการซื้อ
            logging.info(f"Price is below threshold, placing buy order at {current_price}")
            quantity = balance / current_price  # ปรับจำนวนตามยอดคงเหลือ
            buy_order = place_order(symbol, 'buy', current_price, quantity)

            if buy_order:
                buy_price = current_price
                start_time = time.time()
                while time.time() - start_time < max_wait_time:
                    # ตรวจสอบว่าราคาเพิ่มขึ้น 1% จากราคาที่ซื้อ
                    current_price = fetch_price(symbol)
                    if current_price is None:
                        continue

                    if current_price >= buy_price * PROFIT_TARGET:
                        # หากราคาขึ้น 1% ให้ขาย
                        logging.info(f"Price has increased by 1%, placing sell order at {current_price}")
                        place_order(symbol, 'sell', current_price, quantity)
                        break

                    # รออีกนิดก่อนตรวจสอบราคาอีกครั้ง
                    time.sleep(1)

                else:
                    # หากรอเกินเวลาที่กำหนด ให้บังคับขาย
                    logging.info("Waiting time exceeded, forcing sell.")
                    place_order(symbol, 'sell', current_price, quantity)

        # รอให้ราคากลับมาต่ำกว่าราคาที่ซื้อเพื่อซื้ออีกครั้ง
        logging.info(f"Waiting for price to drop to or below initial buy price {threshold}...")
        while True:
            current_price = fetch_price(symbol)
            if current_price is None:
                continue
            if current_price <= threshold:
                logging.info(f"Price dropped below initial buy price, placing buy order at {current_price}")
                break
            time.sleep(1)

# เริ่มต้นการใช้งาน
if __name__ == "__main__":
    if login():
        trade(SYMBOL, THRESHOLD_PRICE)
