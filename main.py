import time
import requests
import base64
import hmac
import hashlib
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
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
        "X-Arkham-Api-Key": api_key,
        "X-Arkham-Expires": str(expiry),
        "X-Arkham-Signature": signature_base64,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

def get_balance():
    """ดึงยอดคงเหลือจาก Arkham Exchange"""
    path = "/wallet/balances"
    url = BASE_URL + path
    headers = generate_signature(API_KEY, API_SECRET, "GET", path)
    logging.info("Fetching balance...")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logging.error(f"Error: {e}, Response: {response.text}")
        raise

if __name__ == "__main__":
    if not API_KEY or not API_SECRET:
        logging.error("API_KEY or API_SECRET is missing from .env")
        exit(1)

    try:
        balance = get_balance()
        logging.info(f"Balance: {balance}")
    except Exception as e:
        logging.error("Failed to fetch balance")
