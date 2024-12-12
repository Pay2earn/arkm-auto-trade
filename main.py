import os
import time
import base64
import hmac
import hashlib
import requests
from dotenv import load_dotenv
import logging

# โหลดค่าจากไฟล์ .env
load_dotenv()

# ตั้งค่าคีย์
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://arkm.com/api"
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def generate_signature(api_key, api_secret, method, path, body=""):
    expiry = (int(time.time()) + 300) * 1000000
    message = f"{api_key}{expiry}{method}{path}{body}"
    decoded_secret = base64.b64decode(api_secret)
    signature = hmac.new(decoded_secret, message.encode(), hashlib.sha256).digest()
    signature_base64 = base64.b64encode(signature).decode()
    return {
        "X-API-Key": api_key,
        "X-Arkham-Expires": str(expiry),
        "X-Arkham-Signature": signature_base64,
        "Content-Type": "application/json"
    }

def get_balance():
    """ดึงข้อมูลยอดคงเหลือ"""
    path = "/account/balance"  # ตรวจสอบ Endpoint ที่ถูกต้อง
    headers = generate_signature(API_KEY, API_SECRET, "GET", path)
    url = BASE_URL + path
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        logging.info("Balance fetched successfully")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error: {e}")
        return None

if __name__ == "__main__":
    balance = get_balance()
    if balance:
        logging.info(f"Balance: {balance}")
    else:
        logging.error("Failed to fetch balance")
