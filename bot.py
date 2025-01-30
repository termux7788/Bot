import mysql.connector
import requests
from flask import Flask, request

app = Flask(__name__)

# Your Telegram Bot Token
BOT_TOKEN = "7796990854:AAHnCNxciOPO6i2UPQFmJFHB4DhBON3l2-s"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# Database configuration
DB_CONFIG = {
    'host': 'sql.freedb.tech',
    'user': 'freedb_bot-tele',
    'password': '8%6ne2FbcyM%fKd',
    'database': 'freedb_bot-tele'
}

# JSON file URL
JSON_URL = "https://peaceful-pika-5db9ea.netlify.app/"

# Function to send a message to Telegram
def send_message(chat_id, text, parse_mode="Markdown"):
    url = TELEGRAM_API_URL + "sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    requests.post(url, json=payload)

# Function to fetch product details from the database
def get_product_details_from_db(product_id):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # Fetch product by ID using LIKE for flexible matching
        query = "SELECT * FROM products WHERE id LIKE %s"
        cursor.execute(query, (f"%{product_id}%",))
        product = cursor.fetchone()

        cursor.close()
        conn.close()

        if product:
            return (
                f"🛒 *Product Details from DB:*\n"
                f"🔹 *Name:* {product['productName']}\n"
                f"💰 *Price:* {product['sellPrice']} BDT\n"
                f"📏 *Size:* {product['size']}\n"
                f"📦 *Status:* {product['status']}\n"
                f"🖼 *Image:* [View Image](https://silkrood.42web.io/stock/{product['productImage']})"
            )
        else:
            return f"❌ Product ID *{product_id}* not found in database."

    except mysql.connector.Error as err:
        return f"❌ Database error: {err}"

# Function to fetch product details from JSON
def get_product_details_from_json(product_id):
    try:
        response = requests.get(JSON_URL)
        response.raise_for_status()
        stock_data = response.json()

        for product in stock_data:
            if product["id"] == product_id:
                return (
                    f"🛒 *Product Details from JSON:*\n"
                    f"🔹 *Name:* {product['productName']}\n"
                    f"💰 *Price:* {product['sellPrice']} BDT\n"
                    f"📏 *Size:* {product['size']}\n"
                    f"📦 *Status:* {product['status']}\n"
                    f"🖼 *Image:* [View Image](https://silkrood.42web.io/stock/{product['productImage']})"
                )
        return f"❌ Product ID *{product_id}* not found in JSON."
    except requests.RequestException:
        return "❌ Failed to fetch data from the JSON source."

# Telegram webhook route
@app.route("/", methods=["POST"])
def telegram_webhook():
    update = request.json  # Get incoming message JSON

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "").strip()

        # Handle commands
        if text.lower() == "/hi":
            send_message(chat_id, "Hello from the script! 😊")
        elif text.lower().startswith("/price"):
            parts = text.split(" ", 1)
            if len(parts) > 1:
                product_id = parts[1].strip()
                product_info = get_product_details_from_db(product_id)
                send_message(chat_id, product_info)
            else:
                send_message(chat_id, "❌ Please provide a product ID.\nUsage: `/price <product_id>`")
        elif text.lower().startswith("/p"):
            parts = text.split(" ", 1)
            if len(parts) > 1:
                product_id = parts[1].strip()
                product_info = get_product_details_from_json(product_id)
                send_message(chat_id, product_info)
            else:
                send_message(chat_id, "❌ Please provide a product ID.\nUsage: `/p <product_id>`")
        else:
            send_message(chat_id, "❌ Unknown command.\nTry `/hi`, `/price <product_id>`, or `/p <product_id>`.")

    return "OK", 200

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
