# Developer Guide

## Environment Setup

### Using Conda
```bash
# Create new environment
conda create -n chatbot python=3.12
conda activate chatbot

# Install dependencies
pip install -r requirements.txt

# For GPU support (optional)
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
```

### Using Docker
```bash
# Build image
docker build -t chatbot:latest .

# Run with GPU support
docker run --gpus all -p 8000:8000 chatbot:latest
```

## Project Structure
```
Project-FY25/
├── main.py                 # Entry point
├── config.py              # Configuration
├── data/                  # Training data
│   ├── intents/          # Intent files
│   └── sessions/         # Chat sessions
├── gui/                  # PyQt6 interface
├── model/                # ML components
├── utils/                # Utilities
└── web_frontend/        # Web interface
```

## Configuration Files

### config.py
```python
class Config:
    # Model settings
    MODEL_TYPE = "svm"  # or "bert"
    CONTEXT_WINDOW_SIZE = 5
    
    # API settings
    API_HOST = "0.0.0.0"
    API_PORT = 8080
    
    # Paths
    DATA_PATH = "data/intents/"
    MODEL_PATH = "model/"
    
    # Logging
    LOG_LEVEL = "INFO"
```

### Environment Variables
```bash
# Override config.py settings
export MODEL_TYPE=bert
export API_PORT=9000
export LOG_LEVEL=DEBUG
```

## Training Workflow

### 1. Data Preparation
- Add/edit intent files in `data/intents/`
- Use `tools/data_stats.py` to validate data

### 2. Model Training
```python
# Via GUI
1. Click "Retrain Model" button
2. Wait for completion notification

# Via API
POST /api/train
Header: X-API-Key: <your-key>

# Via Python
from main import ChatbotApp
app = ChatbotApp()
app.retrain_model(background=True)
```

### 3. Model Validation
- Check training logs in `logs/app.log`
- Test with sample queries
- Monitor prediction confidence

## Development Workflow

### 1. Setup Local Environment
```bash
git clone https://github.com/Pheonix2608/Project-FY25.git
cd Project-FY25
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Run Development Server
```bash
# Terminal 1: GUI + API
python main.py

# Terminal 2: Web frontend (optional)
cd web_frontend
python -m http.server 8000
```

### 3. Development Tools
```bash
# Code formatting
black .

# Linting
flake8

# Tests
pytest
```

## Debugging

### GUI Issues
- Check PyQt dependencies
- Enable debug logging
- Monitor `logs/app.log`

### Model Issues
- Verify training data format
- Check model artifacts exist
- Enable GPU if available

### API Issues
- Verify API key in headers
- Check server logs
- Test endpoints with curl

## Performance Optimization

### Model Training
- Use GPU for BERT
- Adjust batch size
- Enable data caching

### API Server
- Enable compression
- Implement rate limiting
- Cache responses

### GUI
- Batch updates
- Lazy loading
- Resource cleanup

## Security Best Practices

### API Keys
- Rotate regularly
- Use strong entropy
- Implement rate limiting

### Data
- Validate inputs
- Sanitize responses
- Secure file permissions

### Deployment
- Use HTTPS
- Update dependencies
- Monitor logs

## Monitoring

### Logs
- Application: `logs/app.log`
- Training: `logs/training.log`
- API: `logs/api.log`

### Metrics
- Model accuracy
- Response times
- Error rates

### Alerts
- Log errors
- Model failures
- API issues

## Troubleshooting Guide

### Common Issues

1. Model Loading Fails
```python
# Check paths
print(app.config.MODEL_PATH)
# Verify files exist
ls model/svm/
```

2. API Connection Failed
```bash
# Test API
curl http://localhost:8080/
# Check logs
tail -f logs/app.log
```

3. GUI Not Responding
```python
# Enable debug
export LOG_LEVEL=DEBUG
# Check Qt
python -c "from PyQt6.QtWidgets import *"
```

### Solutions

1. Model Issues
- Retrain model
- Check data format
- Verify paths

2. API Issues
- Check port
- Verify key
- Review logs

3. GUI Issues
- Update PyQt
- Check resources
- Clear cache
