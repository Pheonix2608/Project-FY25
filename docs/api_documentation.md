# API Documentation

## Introduction

The Intelligent Chatbot exposes a secure, RESTful API for programmatic interaction. This document provides a comprehensive guide for developers looking to integrate with the chatbot's API.

## Base URL

The API is served from the root of the application. By default, this is:
```
http://localhost:8080
```

## Authentication

All requests to the API must be authenticated using an API key. The key must be included in the `X-API-Key` header of every request.

```
X-API-Key: YOUR_API_KEY_HERE
```

API keys can be generated and managed through the **API Key Management** tab in the Admin Panel. Unauthorized requests will receive a `401 Unauthorized` response.

## Core Endpoint

### `POST /chat`

This is the primary endpoint for sending a message to the chatbot and receiving a response.

**Request Headers**
-   `Content-Type`: `application/json`
-   `X-API-Key`: Your unique API key.

**Request Body**

The request body must be a JSON object containing the user's message.

```json
{
  "message": "Hello, how are you today?"
}
```

**Example Request (`curl`)**

```bash
curl -X POST http://localhost:8080/chat \
     -H "Content-Type: application/json" \
     -H "X-API-Key: YOUR_API_KEY" \
     -d '{"message": "Tell me about your features"}'
```

**Success Response (`200 OK`)**

A successful request will return a JSON object with the chatbot's response and additional metadata.

```json
{
  "user_id": "the_user_id_associated_with_the_key",
  "response": "I can classify intents using either SVM or BERT, and I can even search Google if I don't know the answer!",
  "intent": "about_features",
  "confidence": 0.995
}
```

-   `user_id` (string): The user ID associated with the API key used for the request.
-   `response` (string): The chatbot's textual response.
-   `intent` (string): The intent predicted by the model for the user's message.
-   `confidence` (float): The confidence score (from 0.0 to 1.0) of the intent prediction.

## Error Responses

The API uses standard HTTP status codes to indicate the outcome of a request.

-   **`400 Bad Request`**: The request was malformed (e.g., missing the `message` field).
-   **`401 Unauthorized`**: The provided `X-API-Key` is missing, invalid, or expired.
-   **`503 Service Unavailable`**: The chatbot application is not yet initialized or is currently unavailable. This may occur briefly during application startup.

**Example `401 Unauthorized` Response**
```json
{
  "detail": "Invalid or expired API key."
}
```

## API Client Examples

### Python Example

Here is a simple Python class to interact with the chatbot API.

```python
import requests
import json

class ChatbotClient:
    """A simple Python client for the Intelligent Chatbot API."""
    def __init__(self, api_key, base_url="http://localhost:8080"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }

    def send_message(self, message: str):
        """Sends a message to the chatbot and returns the response.

        Args:
            message (str): The message to send to the chatbot.

        Returns:
            dict: The JSON response from the API, or None on error.
        """
        url = f"{self.base_url}/chat"
        payload = {"message": message}
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(payload))
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

# Example usage:
# client = ChatbotClient(api_key="YOUR_API_KEY")
# response = client.send_message("Hello there!")
# if response:
#     print(f"Bot says: {response['response']}")
```

### JavaScript (Fetch API) Example

Here is a simple JavaScript example using the Fetch API.

```javascript
class ChatbotAPI {
    constructor(apiKey, baseUrl = 'http://localhost:8080') {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
        this.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': this.apiKey
        };
    }

    async sendMessage(message) {
        const url = `${this.baseUrl}/chat`;
        const payload = { message };

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error("Error sending message:", error);
            return null;
        }
    }
}

// Example usage:
// const client = new ChatbotAPI('YOUR_API_KEY');
// client.sendMessage('Tell me a fun fact').then(data => {
//     if (data) {
//         console.log('Bot says:', data.response);
//     }
// });
```