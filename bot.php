<?php
// Your Telegram Bot Token
$botToken = "bot-tocken";
$apiUrl = "https://api.telegram.org/bot" . $botToken . "/";

// URL of the stock_data.json file
$jsonUrl = "https://silkrood.42web.io/stock/stock_data.json";

// Function to fetch and decode JSON data
function getStockData() {
    global $jsonUrl;
    
    // Fetch JSON file from the external URL
    $jsonData = file_get_contents($jsonUrl);
    
    // Check if data is received
    if ($jsonData) {
        return json_decode($jsonData, true);
    }
    
    return null;  // Return null if data is not found
}

// Function to find product price by ID
function getPriceByProductId($productId) {
    $stockData = getStockData();
    
    if ($stockData) {
        foreach ($stockData as $product) {
            if ($product['id'] == $productId) {
                return $product['sellPrice'];
            }
        }
    }
    
    return null;  // Return null if product is not found
}

// Function to send a message to Telegram
function sendMessage($chatId, $message) {
    global $apiUrl;
    
    // Create the API request URL
    $url = $apiUrl . "sendMessage?chat_id=" . $chatId . "&text=" . urlencode($message);
    
    // Send request to Telegram API
    file_get_contents($url);
}

// Read the incoming update from Telegram
$update = file_get_contents("php://input");
$updateData = json_decode($update, true);

// Check if the update contains a message
if (isset($updateData["message"])) {
    $chatId = $updateData["message"]["chat"]["id"];
    $messageText = trim($updateData["message"]["text"]);
    
    // Split the message into parts
    $messageParts = explode(" ", $messageText);
    $command = strtolower($messageParts[0]);  // First part of the message is the command
    
    // Handle commands
    if ($command == "/hi") {
        sendMessage($chatId, "Hello from the script!");
    } 
    elseif ($command == "/price" && isset($messageParts[1])) {
        $productId = $messageParts[1];
        $price = getPriceByProductId($productId);
        
        if ($price !== null) {
            sendMessage($chatId, "The price for product ID $productId is $price.");
        } else {
            sendMessage($chatId, "Product ID $productId not found.");
        }
    } 
    else {
        sendMessage($chatId, "Usage: /hi or /price <product_id>");
    }
}
?>
