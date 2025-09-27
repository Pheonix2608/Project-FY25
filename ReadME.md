# Intelligent Chatbot

Welcome to the Intelligent Chatbot project! This is a sophisticated, modular, and extensible chatbot built with Python. It features a powerful backend supporting multiple NLP models, a secure API, and a full-featured PyQt6-based Admin Panel for easy management and testing.

This document serves as a comprehensive guide for developers looking to understand, run, and contribute to the project.

## Key Features

### Core Engine
- **Pluggable Intent Classifiers**: Easily switch between a classic `SVM` model and a modern `BERT`-based model via a simple configuration change.
- **Context Awareness**: A built-in `ContextHandler` maintains a sliding window of conversation history, enabling more natural, multi-turn dialogues.
- **Named Entity Recognition (NER)**: Utilizes spaCy to extract entities like names, dates, and locations from user input, allowing for more personalized and dynamic responses.
- **Google Search Fallback**: If the chatbot is unsure how to respond, it can be configured to perform a Google search to find a relevant answer.
- **Data Augmentation**: Includes scripts to automatically augment your training data, helping to improve model robustness with minimal effort.

### Admin Panel (PyQt6)
- **Chat Tester**: A real-time interface to test conversations with the bot, complete with session management (create, load, delete), model switching, and theme toggling.
- **API Key Management**: A full CRUD (Create, Read, Update, Delete) interface for managing API keys, allowing you to control access to the chatbot's API.
- **API Session Viewer**: A live log viewer that displays all requests made to the API, with the ability to filter by user ID.
- **Settings Dashboard**: Tweak application behavior on the fly, including model retraining, feature toggles (like Google Search), and UI theme changes.
- **System Monitoring**: Includes tabs for viewing live application logs and system statistics.

### API & Deployment
- **RESTful API**: A secure and scalable HTTP API built with FastAPI for interacting with the chatbot from any client application.
- **Secure by Default**: API endpoints are protected by a robust API key authentication system.
- **Docker Support**: Comes with a `Dockerfile` for easy containerization and deployment.
- **Centralized Logging**: A robust logging system with daily file rotation ensures that all application events are captured.

## Architecture Overview

The project is designed with a clear separation of concerns, making it easy to maintain and extend:

- `main.py`: The main entry point of the application. It initializes all components, including the models, the API server, and the (optional) admin panel GUI.
- `config.py`: A centralized configuration file. It also supports loading settings from environment variables, which is ideal for production deployments.
- `api/`: Contains the FastAPI server (`server.py`) that exposes the chatbot's functionality via a RESTful API.
- `model/`: The brain of the chatbot. This directory includes the intent classifiers (`intent_classifier.py`), response generation logic (`response_handler.py`), context management (`context_handler.py`), and NER (`ner_extractor.py`).
- `utils/`: A collection of utility modules for tasks like database management, text preprocessing, data loading, and logging.
- `admin/`: The source code for the PyQt6 Admin Panel, with each tab implemented as a separate module in `admin/tabs/`.
- `data/`: Contains all data files, including intent JSON files, saved chat sessions, and the SQLite database.

## Installation

Follow these steps to get the chatbot running on your local machine.

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd Project-FY25
    ```

2.  **Set Up a Virtual Environment (Recommended)**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download NLTK Data**
    Run the following Python script to download the necessary NLTK models:
    ```bash
    python download_nltk_data.py
    ```
    This will download `punkt`, `wordnet`, `stopwords`, and `averaged_perceptron_tagger`.

5.  **Run the Application**
    ```bash
    python main.py
    ```
    This will start the background API server. If you have a desktop environment, it will also launch the PyQt6 Admin Panel.

### Docker Deployment

Alternatively, you can build and run the application using Docker:

```bash
docker build -t intelligent-chatbot .
docker run -p 8080:8080 intelligent-chatbot
```

## Configuration

The application can be configured in two ways:
1.  By editing the `config.py` file directly.
2.  By setting environment variables (which will override the values in `config.py`).

Key configuration options include:
- `MODEL_TYPE`: Set to `'svm'` or `'bert'` to choose the intent classification model.
- `ENABLE_GOOGLE_FALLBACK`: Set to `True` or `False` to enable or disable the Google Search fallback feature.
- `CONFIDENCE_THRESHOLD`: The minimum confidence score required for the model to accept a predicted intent.
- `LOG_LEVEL`: The logging level (e.g., `"INFO"`, `"DEBUG"`).
- `API_HOST` & `API_PORT`: The host and port for the API server.

## Usage

### Admin Panel
If you have a graphical environment, running `python main.py` will launch the Admin Panel, which provides a user-friendly interface for all major functionalities.

### API Documentation

The API server runs by default on `http://localhost:8080`.

**Endpoint**: `POST /chat`
-   **Description**: Send a message to the chatbot and receive a response.
-   **Headers**:
    -   `X-API-Key`: Your generated API key.
-   **Request Body** (JSON):
    ```json
    {
      "message": "Hello, how are you?"
    }
    ```
-   **Example `curl` Request**:
    ```bash
    curl -X POST http://localhost:8080/chat \
         -H "Content-Type: application/json" \
         -H "X-API-Key: YOUR_API_KEY" \
         -d '{"message": "Hello"}'
    ```
-   **Success Response** (200 OK):
    ```json
    {
      "user_id": "user_of_the_key",
      "response": "Hello! How can I assist you today?",
      "intent": "greeting",
      "confidence": 0.98
    }
    ```

API keys can be generated from the **API Key Management** tab in the Admin Panel.

## Development

### Adding New Intents
1.  Create a new `.json` file in the `data/intents/` directory.
2.  Define your intent with a `tag`, a list of `patterns` (example user phrases), and a list of `responses`.
    ```json
    {
      "intents": [
        {
          "tag": "order_status",
          "patterns": [
            "Where is my order?",
            "Can I get a status on my delivery?"
          ],
          "responses": [
            "To check your order status, please provide your order number."
          ]
        }
      ]
    }
    ```
3.  Restart the application and use the **Settings** tab in the Admin Panel to retrain the model. The new intent will be automatically included.

### Running Tests
To run the test suite, use the following command:
```bash
pytest
```

## Contributing

We welcome contributions! Please follow these steps:
1.  Fork the repository.
2.  Create a new feature branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes and commit them (`git commit -m 'Add some feature'`).
4.  Push to the branch (`git push origin feature/your-feature-name`).
5.  Open a Pull Request.
6.  Please update `CHANGELOG.md` and `IMPROVEMENTS.md` with your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Version History

For a detailed history of changes, see `CHANGELOG.md`. For a list of ongoing improvements and bug reports, see `IMPROVEMENTS.md`.