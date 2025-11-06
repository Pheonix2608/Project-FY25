# Intelligent Chatbot - User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [GUI Interface](#gui-interface)
5. [Chat Features](#chat-features)
6. [Model Training](#model-training)
7. [Session Management](#session-management)
8. [API Integration](#api-integration)
9. [Configuration](#configuration)
10. [Troubleshooting](#troubleshooting)

## Introduction

The Intelligent Chatbot is a versatile conversational AI application featuring:
- Modern GUI with theme support
- Intent-based response system
- Context-aware conversations
- API access for remote integration
- Session management for conversation history
- Model retraining capabilities

### System Requirements
- Python 3.12 or higher
- 4GB RAM minimum (8GB recommended)
- Windows/Linux/MacOS support
- Internet connection for NLTK data download

## Installation

### Standard Installation

1. Clone the repository:
```bash
git clone https://github.com/Pheonix2608/Project-FY25.git
cd Project-FY25
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Download NLTK data:
```python
import nltk
nltk.download('wordnet')
nltk.download('punkt')
```

### Docker Installation

1. Build the Docker image:
```bash
docker build -t chatbot .
```

2. Run the container:
```bash
docker run -p 8000:8000 chatbot
```

## Getting Started

1. Launch the application:
```bash
python main.py
```

2. The GUI will open with:
   - Chat interface
   - Theme toggle button
   - Model control panel
   - Session management options

3. Type a message and press Enter or click Send to start chatting

## GUI Interface

### Main Window Elements
- **Chat Area**: Displays conversation history
- **Input Field**: Type messages here
- **Send Button**: Click to send message
- **Theme Toggle**: Switch between light/dark themes
- **Menu Bar**: Access additional features

### Control Panel
- **Retrain Model**: Retrain the intent classifier
- **Save Session**: Save current conversation
- **Load Session**: Load previous conversations
- **Clear Chat**: Clear current conversation
- **API Key**: Generate/manage API keys

## Chat Features

### Basic Interaction
- Type messages in the input field
- Press Enter or click Send
- View bot responses in chat area
- Emojis and basic formatting supported

### Supported Intents
1. **Greeting**: Hello, Hi, Hey
2. **Goodbye**: Bye, See you, Goodbye
3. **Thanks**: Thank you, Thanks
4. **Help**: Help, How to, What can you do
5. **About**: Tell me about yourself, What are you
6. **Joke**: Tell me a joke, Say something funny
7. **Status**: How are you, What's up
8. **And more...**: Additional domain-specific intents

### Context Awareness
- Bot remembers previous interactions
- Maintains conversation context
- Provides relevant follow-up responses

## Model Training

### Retraining Process
1. Click "Retrain Model" in control panel
2. Wait for training completion notification
3. Model will automatically reload

### Custom Training Data
1. Navigate to `data/intents/` directory
2. Create/edit JSON files with patterns and responses
3. Format example:
```json
{
  "tag": "greeting",
  "patterns": ["Hi", "Hello", "Hey there"],
  "responses": ["Hello!", "Hi there!", "Greetings!"]
}
```
4. Retrain model to apply changes

## Session Management

### Saving Sessions
1. Click "Save Session" in control panel
2. Session saved with timestamp
3. Stored in `data/sessions/` directory

### Loading Sessions
1. Click "Load Session"
2. Select session from list
3. Previous conversation restored

### Session Files
- JSON format
- Contains full conversation history
- Includes timestamps and metadata
- Portable between installations

## API Integration

### API Key Management
1. Generate API key via GUI
2. Store securely
3. Required for all API requests

### HTTP API Endpoints
- Base URL: `http://localhost:8080`

#### Chat Endpoint
- **URL**: `/chat`
- **Method**: POST
- **Headers**: 
  - `Content-Type: application/json`
  - `X-API-Key: <your-api-key>`
- **Body**:
```json
{
  "message": "Your message here"
}
```
- **Response**:
```json
{
  "user_id": "user123",
  "response": "Bot response here"
}
```

### API Usage Example
```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"message": "Hello"}'
```

## Configuration

### config.py Settings
```python
MODEL_TYPE = "svm"  # or "bert"
LOG_LEVEL = "INFO"
CONTEXT_WINDOW_SIZE = 5
```

### Environment Variables
- `MODEL_TYPE`: Select model (svm/bert)
- `LOG_LEVEL`: Logging detail
- `API_HOST`: API server host
- `API_PORT`: API server port

### Model Selection
- **SVM**: Faster, lighter, ~33% accuracy
- **BERT**: Slower, better accuracy, GPU recommended

## Troubleshooting

### Common Issues

#### Log File Permission Errors
- Close applications using log file
- Check folder permissions
- Use correct user permissions

#### Model Loading Errors
- System will auto-retrain
- Check model file permissions
- Verify training data format

#### NLTK Data Missing
```python
import nltk
nltk.download('wordnet')
nltk.download('punkt')
```

#### Performance Issues
- Add more training data
- Switch to BERT model
- Check system resources
- Monitor log files

### Error Messages

#### "Model files not found"
- Auto-retraining will begin
- Check model directory structure
- Verify file permissions

#### "Failed to save session"
- Check disk space
- Verify write permissions
- Try different filename

#### "API key invalid"
- Regenerate API key
- Check key format
- Verify key in headers

### Getting Help
1. Check logs in `logs/app.log`
2. Review IMPROVEMENTS.md
3. Submit issues on GitHub
4. Contact support team

## Advanced Topics

### Custom Model Training
- Edit training parameters
- Add custom intents
- Implement data augmentation
- Fine-tune model settings

### API Integration Best Practices
- Implement rate limiting
- Handle errors gracefully
- Monitor API usage
- Secure key storage

### Performance Optimization
- Use BERT for accuracy
- SVM for speed
- Optimize training data
- Monitor resource usage
