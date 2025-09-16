# Web Frontend Development

## Overview
This guide explains how to set up and customize the web frontend for remote chatbot access.

## Project Structure
```
web_frontend/
├── index.html          # Main page
├── style.css          # Styling
├── app.js             # Application logic
└── remote_client/     # API client library
```

## Setup

### 1. Configure API Connection
Edit `app.js`:
```javascript
const API_CONFIG = {
    host: 'localhost',
    port: 8080,
    protocol: 'http'
};

// API key from GUI or admin
const API_KEY = 'your-api-key-here';
```

### 2. Run Development Server
```bash
cd web_frontend
python -m http.server 8000
```

Visit `http://localhost:8000` in browser.

## Customization

### Theme
Edit `style.css`:
```css
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    /* Add custom colors */
}
```

### Layout
Modify components in `index.html`:
```html
<div class="chat-container">
    <div id="messages"></div>
    <div class="input-area">
        <!-- Input components -->
    </div>
</div>
```

## API Integration

### Message Handling
```javascript
async function sendMessage(text) {
    try {
        const response = await fetch('http://localhost:8080/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY
            },
            body: JSON.stringify({ message: text })
        });
        return await response.json();
    } catch (error) {
        console.error('API error:', error);
        throw error;
    }
}
```

### Error Handling
```javascript
function handleError(error) {
    // Show user-friendly error
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = `Error: ${error.message}`;
    errorDiv.style.display = 'block';
    
    // Log for debugging
    console.error('Detailed error:', error);
}
```

## Features

### Message History
- Local storage backup
- Pagination
- Search

### UI Components
- Message bubbles
- Loading indicators
- Error messages
- Settings panel

### Responsive Design
- Mobile-friendly
- Desktop optimization
- Touch support

## Security

### API Key Management
- Secure storage
- Regular rotation
- Error handling

### Input Validation
- Message sanitization
- Length limits
- Rate limiting

## Testing

### Local Testing
```bash
# Start API server
python main.py

# Start web server
cd web_frontend
python -m http.server 8000

# Run tests
npm test  # if using test framework
```

### Browser Support
- Chrome/Firefox/Safari
- Mobile browsers
- Error handling

## Deployment

### Production Setup
1. Build static files
2. Configure server
3. Set production API URL
4. Enable HTTPS

### Server Configuration
```nginx
server {
    listen 80;
    server_name chatbot.example.com;
    
    location / {
        root /var/www/chatbot;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
}
```

## TODO
- Add PWA support
- Implement file sharing
- Add voice input
- Improve accessibility
