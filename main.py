import time
import hmac
import hashlib
import base64
import requests
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://arkm.com/api"
SYMBOL = "ETH_USDT"
THRESHOLD_PRICE = 3500  # Example threshold
TRADE_AMOUNT = 0.02
PROFIT_TARGET = 1.01  # 1% profit
MAX_WAIT = 120         # Maximum wait time in seconds for sell

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

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

def fetch_market_data(symbol):
    """Fetch market data for a specific symbol."""
    path = f"/market_data/{symbol}"
    headers = generate_signature(API_KEY, API_SECRET, "GET", path)
    url = f"{BASE_URL}{path}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to fetch market data: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logging.error(f"Error fetching market data: {e}")
        return None

def execute_order(order_type, symbol, amount):
    """Execute buy or sell order."""
    path = f"/orders"
    body = {
        "type": order_type,
        "symbol": symbol,
        "amount": amount
    }
    headers = generate_signature(API_KEY, API_SECRET, "POST", path, str(body))
    url = f"{BASE_URL}{path}"
    try:
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Order execution failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logging.error(f"Error executing order: {e}")
        return None

def auto_trade():
    """Run the trading bot."""
    balance = 1000  # Initial balance for trading
    while balance > 0:
        market_data = fetch_market_data(SYMBOL)
        if not market_data:
            logging.error("Failed to fetch market data, retrying...")
            time.sleep(5)
            continue

        current_price = market_data.get("price")
        logging.info(f"Current price of {SYMBOL}: {current_price}")

        # Buy condition
        if current_price <= THRESHOLD_PRICE:
            logging.info(f"Buying {SYMBOL} at {current_price}")
            buy_order = execute_order("buy", SYMBOL, TRADE_AMOUNT)
            if not buy_order:
                logging.error("Buy order failed.")
                continue

            buy_price = current_price
            start_time = time.time()

            # Wait for sell condition
            while True:
                market_data = fetch_market_data(SYMBOL)
                if not market_data:
                    time.sleep(1)
                    continue
                current_price = market_data.get("price")

                # Check profit target
                if current_price >= buy_price * PROFIT_TARGET:
                    logging.info(f"Selling {SYMBOL} at {current_price} (profit target reached)")
                    sell_order = execute_order("sell", SYMBOL, TRADE_AMOUNT)
                    if sell_order:
                        balance += (current_price - buy_price) * TRADE_AMOUNT
                    break

                # Check max wait time
                if time.time() - start_time > MAX_WAIT:
                    logging.info(f"Selling {SYMBOL} at {current_price} (timeout)")
                    sell_order = execute_order("sell", SYMBOL, TRADE_AMOUNT)
                    if sell_order:
                        balance += (current_price - buy_price) * TRADE_AMOUNT
                    break

            logging.info(f"Balance: {balance}")
        else:
            logging.info(f"Waiting for price to drop below threshold ({THRESHOLD_PRICE})...")
        time.sleep(5)

if __name__ == "__main__":
    auto_trade()
