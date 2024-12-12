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
