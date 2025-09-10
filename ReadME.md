# Intelligent Chatbot

A Python-based conversational AI chatbot with a PyQt6 graphical user interface, featuring intent classification using machine learning models.

## Features

- **PyQt6 GUI**: Modern, responsive user interface with light/dark theme support
- **Intent Classification**: SVM and BERT-based models for understanding user intent
- **Context Awareness**: Maintains conversation context for more natural interactions
- **Text Preprocessing**: Advanced NLP preprocessing using NLTK
- **Conversation History**: Save and load conversation history
- **Model Retraining**: On-the-fly model retraining capability
- **Logging System**: Comprehensive logging with daily rotation

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Prototype
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

## Usage

Run the application:
```bash
python main.py
```

### GUI Features

- **Send Message**: Type your message and press Enter or click Send
- **Retrain Model**: Click to retrain the intent classification model
- **Save History**: Save current conversation to file
- **Load History**: Load previous conversation from file
- **Toggle Theme**: Switch between light and dark themes

## Project Structure

```
Prototype/
├── main.py                 # Main application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── CHANGELOG.md          # Project changelog
├── README.md             # This file
├── conversations.json    # Conversation history
├── data/
│   └── intents.json     # Training data for intents
├── gui/
│   └── chatbot_gui.py   # PyQt6 GUI implementation
├── model/
│   ├── intent_classifier.py  # Intent classification models
│   ├── response_handler.py   # Response generation
│   ├── context_handler.py    # Conversation context management
│   ├── intent_classifier.pkl # Trained SVM model
│   └── vectorizer.pkl        # TF-IDF vectorizer
├── utils/
│   ├── logger.py         # Logging configuration
│   └── preprocessing.py  # Text preprocessing utilities
└── logs/
    └── app.log          # Application logs
```

## Configuration

Edit `config.py` to customize:

- Model type (SVM or BERT)
- GUI appearance and themes
- Logging settings
- Context window size
- Preprocessing options

## Model Performance

Current model accuracy: ~33%

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

1. Edit `data/intents.json`
2. Add new intent with patterns and responses
3. Retrain the model using the GUI

### Model Improvements

- Increase training data variety
- Fine-tune hyperparameters
- Implement data augmentation
- Add more sophisticated NLP features

## Troubleshooting

### Common Issues

1. **Log File Permission Errors**: Close any applications that might be using the log file
2. **Model Loading Errors**: The system will automatically retrain if loading fails
3. **NLTK Data Missing**: Run the NLTK download commands in the installation section

### Performance Issues

- Model accuracy is currently low due to limited training data
- Consider adding more diverse training examples
- Implement cross-validation for better model evaluation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Update the CHANGELOG.md
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.
