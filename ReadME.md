# Intelligent Chatbot

An intelligent, modular Python chatbot with a PyQt6 Admin Panel, supporting SVM/BERT intent classification, context-aware responses, API key management, and an HTTP API server.

## Features

- **PyQt6 Admin Panel**: A comprehensive admin panel with a tabbed interface for managing and testing the chatbot.
  - **Chat Tester**: A full-featured chat interface for testing the bot, with session management, model selection, theme toggling, and chat export.
  - **API Key Management**: A CRUD interface for managing API keys.
  - **API Session Viewer**: A log viewer for monitoring API usage.
  - **Settings**: A tab for configuring the chatbot, including model retraining and feature toggles.
- **Intent Classification**: SVM and BERT-based models (switchable via config).
- **Context Awareness**: Maintains conversation context for natural interactions.
- **Google Search Fallback**: Can be configured to use Google Search for unknown intents.
- **API Key Management**: Secure API access for remote clients.
- **HTTP API Server**: Interact with the bot via REST endpoints. The API returns rich responses with intent and confidence scores.
- **Background Model Training**: The model can be retrained in a background thread without interrupting the application.
- **Logging System**: Daily rotation, error tracking, and API session logging.
- **Docker Support**: Containerized deployment.

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Project-FY25
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download NLTK data:
```python
import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt_tab')
```

4. (Optional) Build and run with Docker:
```bash
docker build -t chatbot .
docker run -p 8080:8080 chatbot
```

## Usage

Run the Admin Panel application:
```bash
python main.py
```

#### API Usage
Start the HTTP API server (runs in background with the Admin Panel):
Default: `http://localhost:8080`

**Endpoints:**
- `POST /chat` (headers: `X-API-Key`, body: `{ "message": "..." }`)
- Generate API keys via the Admin Panel.

**Example request:**
```bash
curl -X POST http://localhost:8080/chat -H "X-API-Key: <your-key>" -d '{"message": "Hello"}'
```

### Admin Panel Features

- **Chat Tester**:
  - Send and receive messages to test the bot.
  - Manage chat sessions (create, load, delete).
  - Switch between `svm` and `bert` models.
  - Toggle between light and dark themes.
  - Export chat history to `.txt` or `.json`.
- **API Key Management**:
  - View all existing API keys.
  - Generate new API keys for different users.
  - Modify the user ID associated with a key.
  - Delete API keys.
- **API Session Viewer**:
  - View a log of all requests made to the API.
  - Filter sessions by user ID.
- **Settings**:
  - Retrain the model (blocking or in the background).
  - Enable/disable the Google Search fallback feature.

## Project Structure

```
Project-FY25/
├── main.py                 # Main application entry point
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── admin/
│   ├── panel.py            # Main Admin Panel window
│   └── tabs/
│       ├── chat_tester_tab.py
│       ├── api_key_management_tab.py
│       ├── api_session_viewer_tab.py
│       └── settings_tab.py
├── data/
│   ├── intents/
│   ├── sessions/
│   └── api_sessions.json
├── model/
│   ├── intent_classifier.py
│   ├── response_handler.py
│   └── ...
├── utils/
│   ├── api_key_manager.py
│   └── ...
└── ...
```

## Configuration

Edit `config.py` to customize:
- Model type (SVM or BERT)
- GUI appearance and themes
- Logging settings
- Context window size
- Google Search fallback (can also be toggled from the Admin Panel)

## Development

### Adding New Intents
1. Add a new intent JSON file in `data/intents/`.
2. Add patterns and responses to the file.
3. Retrain the model using the Admin Panel.

## Troubleshooting


### Common Issues
1. **Log File Permission Errors**: Close any applications that might be using the log file (Windows)
2. **Model Loading Errors**: System auto-retrains if loading fails
3. **NLTK Data Missing**: Run the NLTK download commands in the installation section

### Performance Issues
- Model accuracy is currently low due to limited training data
- Add more diverse training examples
- Implement cross-validation for better model evaluation
- Switch to BERT for improved accuracy

## Contributing


1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Update the CHANGELOG.md and IMPROVEMENTS.md
5. Submit a pull request

## License


This project is licensed under the MIT License - see the LICENSE file for details.

## Version History


See [CHANGELOG.md](CHANGELOG.md) for detailed version history and [IMPROVEMENTS.md](IMPROVEMENTS.md) for ongoing improvements and debug reports.
