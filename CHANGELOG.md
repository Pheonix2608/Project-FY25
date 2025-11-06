## [1.3.0] - 2025-09-11
### Added
- Google fallback integration for chatbot responses
- Async Google search module with caching and rate-limiting
- Configurable max results and cache duration for Google search
- Structured logging for query source and fallback usage
- GUI notice for Google fallback responses
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Data augmentation techniques
- Advanced GUI features (typing indicators, timestamps)
- Unit and integration tests
- Performance monitoring and analytics
- API deployment with FastAPI
- CI/CD integration via GitHub Actions

### Documentation & Workflow
- Added `.github/copilot-instructions.md` for AI agent guidance
- Clarified Admin Panel launch workflow in `ReadME.md`

---

## [1.4.0] - 2025-09-16
### Added
- **Admin Panel**: A new, comprehensive admin panel built with PyQt6.
  - **Chat Tester Tab**: A full-featured chat interface for testing the bot, with session management, model selection, theme toggling, and chat export.
  - **API Key Management Tab**: A CRUD interface for managing API keys.
  - **API Session Viewer Tab**: A log viewer for monitoring API usage, with filtering capabilities.
  - **Settings Tab**: A tab for configuring the chatbot, including model retraining and feature toggles.
- **Background Model Training**: The model can now be retrained in a background thread from the admin panel without interrupting the application.
- **API Session Logging**: All API requests are now logged to `data/api_sessions.json`.
- **Unit Tests**: Added a `pytest` test suite with initial tests for the text preprocessing module.
- **Personal Profile**: A placeholder "Profile" feature in the Chat Tester tab.

### Changed
- **GUI Refactoring**: The old `chatbot_gui.py` has been refactored into a modular admin panel with separate files for each tab under the `admin/` directory.
- **API Response**: The `/chat` API endpoint now returns a richer JSON object, including the predicted intent and confidence score.
- **Intent Handling**: The `ResponseHandler` now uses the Google Search fallback for low-confidence predictions when the feature is enabled.
- **Web Frontend**: The web frontend has been updated to display the intent and confidence score and to show a "typing" indicator.

### Fixed
- A syntax error in the `BertIntentClassifier`'s `load_model` method.
- An incorrect `wordnet` dependency in `requirements.txt`.
- NLTK data download issues in the test environment.

## [1.3.0] - 2025-08-07

### Added
- **Modular BERT classifier** (`bert_classifier.py`) using Hugging Face Transformers
- **Dynamic model switching** (SVM/BERT) via `config.py` or environment variables
- **Environment-aware `Config` class** with `load_from_env()` support
- **Dataset inspection CLI** (`tools/data_stats.py`) for pattern stats and imbalance warnings
- **Training report logging** including accuracy and classification report for both models

### Changed
- Refactored `intent_classifier.py` to act as a factory delegating to SVM or BERT
- Extracted BERT logic from monolithic structure to separate class
- Reused vectorizer path (`vectorizer.pkl`) for label map in BERT classifier
- Streamlined preprocessing and ensured compatibility with both SVM and BERT

### Improved
- Fully compatible retraining from GUI for both SVM and BERT
- Better logging with loss per epoch, evaluation report, and device info
- Smarter model loading fallback — retrains if model file is missing or corrupted

### Security
- Improved model and file error handling
- Safe tokenization and confidence filtering for BERT inference
- Validated intent prediction to avoid index out-of-bounds on malformed inputs

### Performance
- Enabled GPU acceleration for BERT (auto-detection)
- More efficient training with PyTorch DataLoader batching
- Faster switching and execution via unified intent interface

---

## [1.2.0] - 2025-08-04

### Added
- **Dataset expansion script** for improving model accuracy
- **4 new intents**: weather, time, music, news
- **Confidence scoring** for better intent classification
- **Improved SVM parameters** with RBF kernel and better hyperparameters
- **Enhanced TF-IDF vectorizer** with n-grams (1-2) and optimized parameters
- **Stratified sampling** for better class representation in training
- **Fallback mechanism** for low-confidence predictions

### Fixed
- Missing `json` import in `model/intent_classifier.py` causing NameError
- Log file rotation permission errors on Windows by adding delay=True
- Scikit-learn version compatibility warnings
- Model loading error handling
- Improved error handling throughout the application

### Changed
- **Expanded dataset from 13 to 22 intents** (69% increase)
- **Increased training patterns from ~100 to 780 patterns** (680% increase)
- **Enhanced TF-IDF vectorizer** with n-grams and better parameters
- **Improved SVM model** with RBF kernel and probability estimation
- **Added confidence threshold** for better intent classification
- Improved error handling in model loading
- Enhanced logging configuration with better file handling
- Better GUI theme implementation
- Added comprehensive project documentation

### Security
- Added proper error handling for file operations
- Implemented safe model loading with fallback to retraining
- Enhanced input validation and sanitization

### Performance
- **Expected accuracy improvement** from 33% to significantly higher
- **Better generalization** with diverse patterns and n-gram features
- **Improved robustness** with confidence scoring and fallback handling
- **Enhanced user experience** with more intents and better responses

---

## [1.1.0] - 2025-08-04

### Added
- PyQt6-based graphical user interface
- Intent classification with SVM model
- Text preprocessing pipeline
- Context-aware conversation handling
- Logging system with daily rotation
- Theme switching capability
- Conversation history management

### Technical Details
- Model accuracy: ~33% (needs improvement)
- Support for 13 different intents
- TF-IDF vectorization for text processing
- NLTK integration for text preprocessing
