# Tech Stack & Environment Setup

This document outlines the technology stack used in the Intelligent Chatbot project and provides detailed instructions for setting up a local development environment.

## 1. Technology Stack

### Backend
-   **Language**: Python 3.9+
-   **API Framework**: FastAPI - A modern, high-performance web framework for building APIs.
-   **Web Server**: Uvicorn - An ASGI server for running the FastAPI application.

### Natural Language Processing (NLP)
-   **Core NLP Library**: NLTK (Natural Language Toolkit) - Used for fundamental NLP tasks like tokenization, lemmatization, and stopword removal.
-   **Intent Classification (SVM)**: Scikit-learn - A powerful machine learning library used for the SVM model.
-   **Intent Classification (BERT)**:
    -   PyTorch - The deep learning framework used for the BERT model.
    -   Transformers (by Hugging Face) - Provides the pre-trained BERT model and tokenizer.
-   **Named Entity Recognition (NER)**: spaCy - Used for efficient and accurate named entity recognition.

### GUI (Admin Panel)
-   **Framework**: PyQt6 - A comprehensive set of Python bindings for the Qt application framework, used to build the desktop Admin Panel.

### Database
-   **Primary Database**: SQLite - A self-contained, serverless SQL database engine, used by default for its simplicity and ease of setup.
-   **Database Interaction**: The application uses Python's built-in `sqlite3` module.

### Deployment & Tooling
-   **Containerization**: Docker - For creating a consistent, isolated, and portable environment for the application.
-   **Testing**: Pytest - A mature and full-featured testing framework for Python.
-   **Password Hashing**: Passlib - Used for securely hashing and verifying API keys.

## 2. Environment Setup

Follow these steps to set up a local development environment.

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/Project-FY25.git
    cd Project-FY25
    ```

2.  **Create and Activate a Virtual Environment**
    Using a virtual environment is crucial to avoid conflicts with other projects or system-wide Python packages.
    ```bash
    # For Unix/macOS
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies**
    All required Python packages are listed in `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download NLP Models**
    The application requires data from NLTK and a model from spaCy.
    -   **NLTK Data**: Run the provided script to download the necessary packages.
        ```bash
        python download_nltk_data.py
        ```
    -   **spaCy Model**: The NER extractor will automatically download the `en_core_web_sm` model on its first run if it's not found.

5.  **Run the Application**
    You can now run the main application. This will start the API server and, if you are on a system with a graphical interface, launch the Admin Panel.
    ```bash
    python main.py
    ```

## 3. Key Dependencies

The full list of dependencies is in `requirements.txt`. Below are the most important ones:

-   `fastapi`: For the REST API.
-   `uvicorn`: For serving the FastAPI application.
-   `scikit-learn`: For the SVM intent classifier.
-   `torch`: For the BERT intent classifier.
-   `transformers`: For using the pre-trained BERT model.
-   `nltk`: For text preprocessing.
-   `spacy`: For Named Entity Recognition.
-   `PyQt6`: For the Admin Panel GUI.
-   `passlib`: For hashing API keys.
-   `bcrypt`: A dependency of `passlib` for the hashing algorithm.

## 4. Configuration

Application behavior is controlled by the `config.py` file and can be overridden by environment variables. For development, you can directly modify `config.py`. For production, using environment variables is recommended.

**Key Configuration Options:**
-   `MODEL_TYPE`: Switch between `'svm'` and `'bert'`.
-   `ENABLE_GOOGLE_FALLBACK`: `True` or `False` to toggle the Google Search feature.
-   `CONFIDENCE_THRESHOLD`: A float between `0.0` and `1.0` to set the minimum confidence for intent matching.
-   `LOG_LEVEL`: Set to `"DEBUG"` for more verbose logging during development.

Refer to the `deployment_guide.md` for instructions on using a `.env` file with Docker.