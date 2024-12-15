import time
import hmac
import hashlib
import base64
import requests
import json
import logging
import os

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# อ่านค่าจาก .env หรือกำหนด API_KEY และ API_SECRET ที่นี่
API_KEY = os.getenv("API_KEY", "your-api-key")
API_SECRET = os.getenv("API_SECRET", "your-api-secret")

# ค่า BASE_URL สำหรับการเชื่อมต่อกับ API
BASE_URL = "https://arkm.com/api"

# ฟังก์ชันสำหรับสร้าง signature
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

# ฟังก์ชันดึงข้อมูลราคา
def fetch_price(symbol):
    path = f"/v1/market/{symbol}"  # ใช้เส้นทาง v1/market/{symbol}
    url = BASE_URL + path  # รวม BASE_URL และ path
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data['data']['last_price']  # สมมติว่า response มี key 'data' และ 'last_price' ที่เก็บราคา
    else:
        logging.error(f"Error fetching price for {symbol}: {response.text}")
        return None

# ฟังก์ชันสำหรับการ place order
def place_order(symbol, amount, price, side):
    path = "/v1/order"  # เส้นทางสำหรับการส่งคำสั่งซื้อหรือขาย
    body = {
        "symbol": symbol,
        "amount": amount,
        "price": price,
        "side": side  # "buy" หรือ "sell"
    }
    
    url = BASE_URL + path  # รวม BASE_URL และ path
    headers = generate_signature(API_KEY, API_SECRET, 'POST', path, json.dumps(body))
    
    response = requests.post(url, headers=headers, data=json.dumps(body))  # ส่งคำขอแบบ POST

    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            logging.info(f"Order placed successfully: {side} {amount} {symbol} at {price}")
        else:
            logging.error(f"Error placing order: {data}")
    else:
        logging.error(f"Error with request: {response.text}")

# ตัวอย่างการใช้งาน:
def auto_trade():
    symbol = "ETH_USDT"
    amount = 0.02  # จำนวนที่จะซื้อหรือขาย

    price = fetch_price(symbol)
    if price:
        logging.info(f"Current price: {price}")
        # Place a buy order
        place_order(symbol, amount, price, 'buy')

        # รอให้ราคาเพิ่มขึ้น 1% หรือเวลาผ่านไป 10 วินาที
        start_time = time.time()
        while time.time() - start_time < 10:
            current_price = fetch_price(symbol)
            if current_price and current_price >= price * 1.01:
                # Place a sell order
                place_order(symbol, amount, current_price, 'sell')
                break
            time.sleep(1)
        else:
            # Force sell if price doesn't reach target within 10 seconds
            logging.info(f"Force selling after waiting for 10 seconds.")
            place_order(symbol, amount, price * 1.01, 'sell')

if __name__ == "__main__":
    auto_trade()
