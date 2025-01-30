from flask import Flask, request
import mysql.connector
import requests

app = Flask(__name__)

# Your Telegram Bot Token
BOT_TOKEN = "7796990854:AAHnCNxciOPO6i2UPQFmJFHB4DhBON3l2-s"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# MySQL Database configuration
DB_HOST = 'sql200.epizy.com'  # Database host, change to your server if hosted elsewhere
DB_USER = 'epiz_32198676'  # Your MySQL username
DB_PASSWORD = 'akqVqZ69kFmX'  # Your MySQL password
DB_NAME = 'epiz_32198676_bot'  # Your database name

# Function to fetch product details from MySQL database
def get_product_details(product_id):
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM products WHERE id = %s"
        cursor.execute(query, (product_id,))
        product = cursor.fetchone()
        print(f"Query executed, product fetched: {product}")  # Debugging line

        if product:
            return (
                f"🛒 *Product Details:*\n"
                f"🔹 *Name:* {product['productName']}\n"
                f"💰 *Price:* {product['sellPrice']} BDT\n"
                f"📏 *Size:* {product['size']}\n"
                f"📦 *Status:* {product['status']}\n"
                f"🖼 *Image:* [View Image](https://yourdomain.com/{product['productImage']})"
            )
        else:
            return None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()
        connection.close()

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
        product_id = parts[1].strip()  # Remove any leading/trailing spaces
        print(f"Received product ID: {product_id}")  # Debugging line
        product_info = get_product_details(product_id)
        if product_info:
            send_message(chat_id, product_info)
        else:
            send_message(chat_id, f"❌ Product ID *{product_id}* not found.")
    else:
        send_message(chat_id, "❌ Please provide a product ID.\nUsage: `/price <product_id>`")

    return "OK", 200

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
