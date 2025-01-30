from flask import Flask, request
import requests

app = Flask(__name__)

# Your Telegram Bot Token
BOT_TOKEN = "7796990854:AAHnCNxciOPO6i2UPQFmJFHB4DhBON3l2-s"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# JSON file URL
JSON_URL = "https://peaceful-pika-5db9ea.netlify.app/"

# Function to fetch stock data
def get_stock_data():
    try:
        response = requests.get(JSON_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

# Function to get product details by ID
def get_product_details(product_id):
    stock_data = get_stock_data()
    if stock_data:
        for product in stock_data:
            if product["id"] == product_id:
                return (
                    f"ðŸ›’ *Product Details:*\n"
                    f"ðŸ”¹ *Name:* {product['productName']}\n"
                    f"ðŸ’° *Price:* {product['sellPrice']} BDT\n"
                    f"ðŸ“ *Size:* {product['size']}\n"
                    f"ðŸ“¦ *Status:* {product['status']}\n"
                    f"ðŸ–¼ *Image:* [View Image](https://silkrood.42web.io/stock/{product['productImage']})"
                )
    return None

# Function to send a message to Telegram
def send_message(chat_id, text, parse_mode="Markdown"):
    url = TELEGRAM_API_URL + "sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    requests.post(url, json=payload)

# Telegram webhook route
@app.route("/", methods=["POST"])
def telegram_webhook():
    update = request.json  # Get incoming message JSON

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "").strip()

        # Handle commands
        if text.lower() == "/hi":
            send_message(chat_id, "Hello from the script! ðŸ˜Š")
        elif text.lower().startswith("/price"):
            parts = text.split(" ", 1)
            if len(parts) > 1:
                product_id = parts[1].strip()
                product_info = get_product_details(product_id)
                if product_info:
                    send_message(chat_id, product_info)
                else:
                    send_message(chat_id, f"âŒ Product ID *{product_id}* not found.")
            else:
                send_message(chat_id, "âŒ Please provide a product ID.\nUsage: `/price <product_id>`")
        else:
            send_message(chat_id, "âŒ Unknown command.\nTry `/hi` or `/price <product_id>`.")

    return "OK", 200

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
