# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- BERT model implementation for enhanced accuracy
- Data augmentation techniques
- Cross-validation for better performance metrics
- Advanced GUI features (typing indicators, timestamps)
- Unit and integration tests
- Performance monitoring and analytics

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