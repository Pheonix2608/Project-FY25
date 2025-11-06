# API Documentation

## Overview
The chatbot exposes a RESTful API that allows programmatic interaction with the system. All endpoints require API key authentication and support JSON requests/responses.

## Base URL
```
http://localhost:8080
```

## Authentication
All requests require an API key passed in the `X-API-Key` header.
```bash
X-API-Key: your-api-key-here
```

## Rate Limiting
- 100 requests per minute per API key
- 429 Too Many Requests response when exceeded
- Exponential backoff recommended

## Endpoints

### Health Check
```
GET /
```
Response:
```json
{
    "status": "ok",
    "message": "Chatbot API running",
    "version": "1.0.0"
}
```

### Send Message
```
POST /chat
```
Request:
```json
{
    "message": "Hello",
    "context_id": "optional-session-id"
}
```
Response:
```json
{
    "user_id": "user123",
    "response": "Hi! How can I help you today?",
    "intent": "greeting",
    "confidence": 0.95,
    "context_id": "session-123"
}
```

### Retrain Model
```
POST /train
```
Request:
```json
{
    "model_type": "svm",  // or "bert"
    "background": true
}
```
Response:
```json
{
    "status": "started",
    "job_id": "train_123",
    "estimated_time": "300s"
}
```

### Get Training Status
```
GET /train/status/{job_id}
```
Response:
```json
{
    "status": "completed",
    "progress": 100,
    "metrics": {
        "accuracy": 0.85,
        "f1_score": 0.83
    }
}
```

### List Sessions
```
GET /sessions
```
Response:
```json
{
    "sessions": [
        {
            "id": "session_123",
            "created_at": "2025-09-11T10:00:00Z",
            "message_count": 10
        }
    ]
}
```

### Load Session
```
GET /sessions/{session_id}
```
Response:
```json
{
    "id": "session_123",
    "messages": [
        {
            "role": "user",
            "content": "Hello",
            "timestamp": "2025-09-11T10:00:00Z"
        },
        {
            "role": "bot",
            "content": "Hi there!",
            "timestamp": "2025-09-11T10:00:01Z"
        }
    ]
}
```

## Error Responses

### 400 Bad Request
```json
{
    "error": "Invalid request format",
    "details": "Missing required field: message"
}
```

### 401 Unauthorized
```json
{
    "error": "Authentication failed",
    "details": "Missing or invalid API key"
}
```

### 429 Too Many Requests
```json
{
    "error": "Rate limit exceeded",
    "reset_at": "2025-09-11T10:01:00Z"
}
```

### 500 Internal Server Error
```json
{
    "error": "Internal server error",
    "request_id": "req_123"
}
```

## API Clients

### Python Example
```python
import requests

class ChatbotClient:
    def __init__(self, api_key, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.headers = {"X-API-Key": api_key}
    
    def send_message(self, message, context_id=None):
        data = {"message": message}
        if context_id:
            data["context_id"] = context_id
        
        response = requests.post(
            f"{self.base_url}/chat",
            headers=self.headers,
            json=data
        )
        return response.json()
```

### JavaScript Example
```javascript
class ChatbotAPI {
    constructor(apiKey, baseUrl = 'http://localhost:8080') {
        this.baseUrl = baseUrl;
        this.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': apiKey
        };
    }

    async sendMessage(message, contextId = null) {
        const data = { message };
        if (contextId) data.context_id = contextId;

        const response = await fetch(`${this.baseUrl}/chat`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        return await response.json();
    }
}
```

## Rate Limit Headers
All responses include rate limit information:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1631350860
```

## Webhook Support
The API supports webhooks for asynchronous operations (optional):
```json
{
    "webhook_url": "https://your-server.com/webhook",
    "events": ["training.completed", "error"]
}
```
