from flask import Flask, request
import requests

# Initialize Flask app
app = Flask(__name__)

# Your Telegram Bot Token
BOT_TOKEN = "7796990854:AAHnCNxciOPO6i2UPQFmJFHB4DhBON3l2-s"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# JSON file URL
JSON_URL = "https://silkrood.42web.io/stock/stock_data.json"

# Function to fetch stock data
def get_stock_data():
    try:
        response = requests.get(JSON_URL)
        response.raise_for_status()  # Raise an error if the request fails
        return response.json()  # Return JSON data
    except requests.RequestException:
        return None  # Return None if there is an error

# Function to get price by product ID
def get_price_by_product_id(product_id):
    stock_data = get_stock_data()
    
    if stock_data:
        for product in stock_data:
            if str(product["id"]) == str(product_id):
                return product["sellPrice"]
    
    return None  # Return None if product not found

# Function to send a message to Telegram
def send_message(chat_id, text):
    url = TELEGRAM_API_URL + "sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

# Telegram webhook route
@app.route("/", methods=["POST"])
def telegram_webhook():
    update = request.json  # Get the incoming message JSON

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "").strip()

        # Split command into parts
        parts = text.split(" ")
        command = parts[0].lower()

        # Handle commands
        if command == "/hi":
            send_message(chat_id, "Hello from the script!")
        elif command == "/price" and len(parts) > 1:
            product_id = parts[1]
            price = get_price_by_product_id(product_id)
            if price:
                send_message(chat_id, f"The price for product ID {product_id} is {price}.")
            else:
                send_message(chat_id, f"Product ID {product_id} not found.")
        else:
            send_message(chat_id, "Usage: /hi or /price <product_id>")

    return "OK", 200  # Respond to Telegram that the request was handled

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)