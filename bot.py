from flask import Flask, request
import requests
import mysql.connector

app = Flask(__name__)

# Telegram Bot Token
BOT_TOKEN = "7796990854:AAHnCNxciOPO6i2UPQFmJFHB4DhBON3l2-s"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# Database credentials
DB_CONFIG = {
    "host": "sql.freedb.tech",
    "user": "freedb_bot-tele",
    "password": "8%6ne2FbcyM%fKd",
    "database": "freedb_bot-tele"
}

# JSON URL for /p command
JSON_URL = "https://peaceful-pika-5db9ea.netlify.app/"

# Function to fetch product details from MySQL
def get_product_details_from_db(product_id):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # Fetch product by ID
        query = "SELECT * FROM products WHERE id = %s"
        cursor.execute(query, (product_id,))
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
            return None  # Product not found
    except mysql.connector.Error as err:
        print(f"Database error: {err}")  # Debugging step
        return None

# Function to fetch product details from JSON
def get_product_details_from_json(product_id):
    try:
        response = requests.get(JSON_URL)
        response.raise_for_status()
        stock_data = response.json()

        for product in stock_data:
            if str(product["id"]) == str(product_id):
                return (
                    f"🛒 *Product Details from JSON:*\n"
                    f"🔹 *Name:* {product['productName']}\n"
                    f"💰 *Price:* {product['sellPrice']} BDT\n"
                    f"📏 *Size:* {product['size']}\n"
                    f"📦 *Status:* {product['status']}\n"
                    f"🖼 *Image:* [View Image](https://silkrood.42web.io/stock/{product['productImage']})"
                )
        return None  # Product not found
    except requests.RequestException as err:
        print(f"Error fetching JSON: {err}")  # Debugging step
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
            send_message(chat_id, "Hello from the script! 😊")
        elif text.lower().startswith("/price"):
            parts = text.split(" ", 1)
            if len(parts) > 1:
                product_id = parts[1].strip()
                print(f"Received product ID from /price: {product_id}")  # Debugging step

                product_info = get_product_details_from_db(product_id)
                if product_info:
                    send_message(chat_id, product_info)
                else:
                    send_message(chat_id, f"❌ Product ID *{product_id}* not found in database.")
            else:
                send_message(chat_id, "❌ Please provide a product ID.\nUsage: `/price <product_id>`")
        elif text.lower().startswith("/p"):
            parts = text.split(" ", 1)
            if len(parts) > 1:
                product_id = parts[1].strip()
                print(f"Received product ID from /p: {product_id}")  # Debugging step

                product_info = get_product_details_from_json(product_id)
                if product_info:
                    send_message(chat_id, product_info)
                else:
                    send_message(chat_id, f"❌ Product ID *{product_id}* not found in JSON.")
            else:
                send_message(chat_id, "❌ Please provide a product ID.\nUsage: `/p <product_id>`")
        else:
            send_message(chat_id, "❌ Unknown command.\nTry `/hi`, `/price <product_id>`, or `/p <product_id>`.")

    return "OK", 200

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
