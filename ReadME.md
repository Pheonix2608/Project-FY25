# Intelligent Chatbot

An intelligent, modular Python chatbot with a PyQt6 GUI, supporting SVM/BERT intent classification, context-aware responses, API key management, and HTTP API server. Easily extensible and production-ready.

## Features

- **PyQt6 GUI**: Modern, responsive user interface with light/dark theme support
- **Intent Classification**: SVM and BERT-based models (switchable via config)
- **Context Awareness**: Maintains conversation context for natural interactions
- **API Key Management**: Secure API access for remote clients
- **HTTP API Server**: Interact with the bot via REST endpoints
- **Conversation History**: Save/load sessions
- **Model Retraining**: On-the-fly retraining from GUI
- **Logging System**: Daily rotation, error tracking
- **Dataset Inspection Tool**: CLI for analyzing training data
- **Docker Support**: Containerized deployment

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
nltk.download('wordnet')
nltk.download('punkt')
```

4. (Optional) Build and run with Docker:
```bash
docker build -t chatbot .
docker run -p 8000:8000 chatbot
```

## Usage


Run the GUI application:
```bash
python main.py
```

#### API Usage
Start the HTTP API server (runs in background with GUI):
Default: `http://localhost:8080`

**Endpoints:**
- `POST /chat` (headers: `X-API-Key`, body: `{ "message": "..." }`)
- Generate API key via GUI or use default for testing

**Example request:**
```bash
curl -X POST http://localhost:8080/chat -H "X-API-Key: <your-key>" -d '{"message": "Hello"}'
```

### GUI Features

- **Send Message**: Type your message and press Enter or click Send
- **Retrain Model**: Click to retrain the intent classification model
- **Save History**: Save current conversation to file
- **Load History**: Load previous conversation from file
- **Toggle Theme**: Switch between light and dark themes

## Project Structure


```
Project-FY25/
├── main.py                 # Main application entry point
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── Dockerfile              # Containerization
├── CHANGELOG.md            # Project changelog
├── README.md               # This file
├── conversations.json      # Conversation history
├── data/
│   ├── intents/           # Training data for intents
│   └── sessions/          # Saved conversation sessions
├── gui/
│   └── chatbot_gui.py     # PyQt6 GUI implementation
├── model/
│   ├── intent_classifier.py   # Intent classification (SVM/BERT)
│   ├── bert_classifier.py     # BERT model logic
│   ├── response_handler.py    # Response generation
│   ├── context_handler.py     # Conversation context management
│   ├── bert/                  # BERT model files
│   └── svm/                   # SVM model files
├── utils/
│   ├── logger.py              # Logging configuration
│   ├── preprocessing.py       # Text preprocessing
│   ├── api_key_manager.py     # API key management
│   └── data_loader.py         # Data loading utilities
├── tools/
│   └── data_stats.py          # Dataset inspection CLI
└── logs/
    └── app.log                # Application logs
```

## Configuration

Edit `config.py` to customize:

- Model type (SVM or BERT)
- GUI appearance and themes
- Logging settings
- Context window size
- Preprocessing options

## Model Performance


Current model accuracy: ~33% (SVM). BERT model and data augmentation planned for higher accuracy.

**Supported Intents:**
- Greeting
- Goodbye
- Thanks
- Name
- About bot
- Help
- Joke
- Creator
- Age
- Status check
- Apology
- Compliment
- Feedback

## Development


### Adding New Intents
1. Add new intent file in `data/intents/` (or edit existing)
2. Add patterns and responses
3. Retrain the model using the GUI

### Model Improvements
- Increase training data variety
- Fine-tune hyperparameters
- Implement data augmentation
- Add more sophisticated NLP features
- Switch to BERT for better performance

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
