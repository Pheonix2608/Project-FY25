# Quick Start Guide

## Installation in 5 Minutes

### 1. Clone & Install
```bash
# Clone repository
git clone https://github.com/Pheonix2608/Project-FY25.git
cd Project-FY25

# Set up Python environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('wordnet'); nltk.download('punkt')"
```

### 2. Run the Bot
```bash
python main.py
```

### 3. Use the API
```bash
# Get API key from GUI
# Test API
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key-here" \
  -d '{"message": "Hello"}'
```

## Core Features

### GUI Client
- Modern PyQt6 interface
- Theme switching
- Session management
- Model retraining

### API Server
- RESTful endpoints
- API key auth
- Rate limiting
- Error handling

### ML Models
- SVM classifier
- BERT option
- Background training
- Hot model swapping

## Next Steps

### Add Training Data
1. Edit files in `data/intents/`
2. Click "Retrain Model"
3. Test new responses

### Deploy to Server
1. Build Docker image
2. Run container
3. Configure NGINX

### Customize
1. Edit `config.py`
2. Modify themes
3. Add intents

## Links
- [Full Documentation](docs/README.md)
- [API Reference](docs/api_documentation.md)
- [Developer Guide](docs/guides/developer_guide.md)
- [User Guide](docs/guides/user_guide.md)
