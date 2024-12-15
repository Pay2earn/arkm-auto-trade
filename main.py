import time
import hmac
import hashlib
import base64
import requests
import json
import logging
import math
from dotenv import load_dotenv
import os

# โหลดค่าจากไฟล์ .env
load_dotenv()

# อ่าน API_KEY และ API_SECRET จากไฟล์ .env
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

BASE_URL = "https://arkm.com/api"
SYMBOL = "ETH_USDT"
TRADE_AMOUNT = 0.02  # Amount to trade
PROFIT_TARGET = 1.01  # Sell when price reaches 1% higher than the buy price
WAIT_TIME = 10  # Force sell if waiting for this long in seconds

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

def login_to_armk_api():
    # Implement login mechanism, if needed (e.g., authenticate and get tokens)
    logging.info("Logged into ARMK API successfully.")

def fetch_price(symbol):
    path = f"/v1/market/{symbol}"
    headers = generate_signature(API_KEY, API_SECRET, 'GET', path)
    url = BASE_URL + path
    response = requests.get(url, headers=headers)
    data = response.json()
    if response.status_code == 200:
        return float(data['data']['last_price'])  # Assuming the response contains this field
    else:
        logging.error(f"Error fetching data for {symbol}: {data}")
        return None

def buy(symbol, amount):
    # Send buy request (adjust as necessary for your API's endpoint and parameters)
    path = "/v1/order"
    body = {
        "symbol": symbol,
        "amount": amount,
        "side": "buy",
        "price": fetch_price(symbol)
    }
    headers = generate_signature(API_KEY, API_SECRET, 'POST', path, json.dumps(body))
    url = BASE_URL + path
    response = requests.post(url, headers=headers, data=json.dumps(body))
    data = response.json()
    if response.status_code == 200 and data.get('status') == 'success':
        logging.info(f"Bought {amount} {symbol} successfully at price {body['price']}")
        return body['price']  # Return the buy price for further calculations
    else:
        logging.error(f"Error placing buy order: {data}")
        return None

def sell(symbol, amount, buy_price):
    # Sell the asset when the price has increased by 1% or after 10 seconds
    current_price = fetch_price(symbol)
    if current_price and current_price >= buy_price * PROFIT_TARGET:
        path = "/v1/order"
        body = {
            "symbol": symbol,
            "amount": amount,
            "side": "sell",
            "price": current_price
        }
        headers = generate_signature(API_KEY, API_SECRET, 'POST', path, json.dumps(body))
        url = BASE_URL + path
        response = requests.post(url, headers=headers, data=json.dumps(body))
        data = response.json()
        if response.status_code == 200 and data.get('status') == 'success':
            logging.info(f"Sold {amount} {symbol} successfully at price {current_price}")
            return True
        else:
            logging.error(f"Error placing sell order: {data}")
            return False
    else:
        logging.info(f"Waiting for price to reach {buy_price * PROFIT_TARGET}, current price is {current_price}")
        return False

def auto_trade():
    balance = 1  # Set an initial balance (for example, you can fetch the actual balance from the API)
    initial_price = fetch_price(SYMBOL)

    while balance > 0:
        current_price = fetch_price(SYMBOL)
        if current_price is None:
            continue

        logging.info(f"Current price: {current_price}")

        # If the price is lower than the initial price, attempt to buy
        if current_price < initial_price:
            logging.info(f"Price {current_price} is lower than initial price {initial_price}. Trying to buy.")
            buy_price = buy(SYMBOL, TRADE_AMOUNT)
            if buy_price:
                # Wait for the price to reach the target
                start_time = time.time()
                while time.time() - start_time < WAIT_TIME:
                    if sell(SYMBOL, TRADE_AMOUNT, buy_price):
                        balance -= TRADE_AMOUNT
                        initial_price = fetch_price(SYMBOL)
                        break
                    time.sleep(1)
                else:
                    logging.info(f"Force selling {SYMBOL} after waiting for {WAIT_TIME} seconds.")
                    sell(SYMBOL, TRADE_AMOUNT, buy_price)
                    balance -= TRADE_AMOUNT
                    initial_price = fetch_price(SYMBOL)
        else:
            logging.info(f"Price {current_price} is not lower than initial price. Waiting for better conditions.")
            time.sleep(5)  # Sleep before checking the price again

        time.sleep(1)  # Sleep before the next loop iteration

if __name__ == "__main__":
    login_to_armk_api()
    auto_trade()
