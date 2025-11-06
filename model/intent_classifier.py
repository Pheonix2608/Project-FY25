# ==============================================================================
# model/intent_classifier.py
# Intent classification module with a factory pattern for different models.
# ==============================================================================
import pickle
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import os

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification
from torch.optim import AdamW # Import AdamW directly from PyTorch

from utils.logger import get_logger
from utils.data_loader import load_all_intents

logger = get_logger(__name__)

class IntentClassifier:
    """
    Factory class to create and manage intent classifiers.
    """
    def __init__(self, config):
        self.config = config
        self.model_type = config.MODEL_TYPE
        # Ensure model artifacts are stored under per-model subfolders
        try:
            base_models_dir = getattr(self.config, 'MODELS_DIR', os.path.join(os.path.dirname(__file__), 'model'))
            if self.model_type == 'svm':
                self.config.MODEL_FILE_PATH = os.path.join(base_models_dir, 'svm', 'intent_classifier.pkl')
                self.config.VECTORIZER_FILE_PATH = os.path.join(base_models_dir, 'svm', 'vectorizer.pkl')
            elif self.model_type == 'bert':
                self.config.MODEL_FILE_PATH = os.path.join(base_models_dir, 'bert', 'intent_classifier.pkl')
                self.config.VECTORIZER_FILE_PATH = os.path.join(base_models_dir, 'bert', 'vectorizer.pkl')
        except Exception:
            pass
        
        if self.model_type == 'svm':
            self.classifier = SVMIntentClassifier(config)
        elif self.model_type == 'bert':
            self.classifier = BertIntentClassifier(config)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

    def train_model(self, data, preprocessor):
        self.classifier.train_model(data, preprocessor)

    def load_model(self):
        self.classifier.load_model()
    
    def predict_intent(self, preprocessed_tokens):
        return self.classifier.predict_intent(preprocessed_tokens)


class SVMIntentClassifier:
    """
    A class for training, testing, and predicting intents using a scikit-learn classifier.
    """
    def __init__(self, config):
        self.config = config
        self.model = None
        self.vectorizer = None
        self.intents = []
        logger.info("SVM intent classifier initialized.")

    def train_model(self, data, preprocessor):
        logger.info("Starting SVM model training process...")
        patterns = []
        labels = []
        for intent in data['intents']:
            # Skip default fallback intent from training/labels
            if intent.get('tag') == 'default':
                continue
            if intent['patterns']:
                for pattern in intent['patterns']:
                    patterns.append(" ".join(preprocessor.preprocess(pattern)))
                    labels.append(intent['tag'])
        
        if not patterns:
            logger.error("No training patterns found. Cannot train model.")
            return

        self.intents = sorted(list(set(labels)))
        
        # Improved TF-IDF vectorizer with better parameters
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
            stop_words='english'
        )
        
        # Use stratified split to ensure all classes are represented
        X_train, X_test, y_train, y_test = train_test_split(
            patterns, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        X_train_vec = self.vectorizer.fit_transform(X_train)
        
        # Improved SVM with better parameters
        self.model = SVC(
            kernel='rbf',
            C=1.0,
            gamma='scale',
            probability=True,
            random_state=42
        )
        self.model.fit(X_train_vec, y_train)
        
        X_test_vec = self.vectorizer.transform(X_test)
        y_pred = self.model.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"SVM Model training complete. Accuracy on test data: {accuracy:.2f}")
        logger.info("Classification Report:\n" + classification_report(y_test, y_pred, zero_division=0))

        try:
            # Ensure models directory exists
            os.makedirs(os.path.dirname(self.config.MODEL_FILE_PATH), exist_ok=True)
            with open(self.config.MODEL_FILE_PATH, 'wb') as f:
                pickle.dump(self.model, f)
            with open(self.config.VECTORIZER_FILE_PATH, 'wb') as f:
                pickle.dump(self.vectorizer, f)
            logger.info("SVM model and vectorizer saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save model files: {e}", exc_info=True)

    def load_model(self):
        logger.info("Loading SVM model from disk...")
        try:
            with open(self.config.MODEL_FILE_PATH, 'rb') as f:
                self.model = pickle.load(f)
            with open(self.config.VECTORIZER_FILE_PATH, 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            # Load intents from directory to ensure merged set
            intents_dir = getattr(self.config, 'INTENTS_DIR', None)
            if intents_dir and os.path.isdir(intents_dir):
                data = load_all_intents(intents_dir)
            else:
                # Fallback to legacy single file
                with open(self.config.DATA_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            self.intents = sorted([intent['tag'] for intent in data['intents'] if intent.get('tag') != 'default'])
            
            logger.info("SVM model and vectorizer loaded successfully.")
            return True
        except (FileNotFoundError, pickle.UnpicklingError) as e:
            logger.error(f"Error loading SVM model files: {e}")
            return False

    def predict_intent(self, preprocessed_tokens):
        if not self.model or not self.vectorizer:
            logger.error("SVM model is not loaded. Cannot predict.")
            return 'unknown', 0.0
        
        text = " ".join(preprocessed_tokens)
        if not text.strip():
            return 'default', 1.0

        vectorized_text = self.vectorizer.transform([text])
        
        # Get prediction and confidence score
        predicted_intent = self.model.predict(vectorized_text)[0]
        confidence_scores = self.model.predict_proba(vectorized_text)[0]
        max_confidence = float(np.max(confidence_scores))
        
        logger.info(f"Predicted intent (SVM): '{predicted_intent}' with confidence: {max_confidence:.3f}")
        
        # Use configured confidence threshold for matching
        if max_confidence < self.config.CONFIDENCE_THRESHOLD:
            logger.info(f"Low confidence ({max_confidence:.3f}), below threshold {self.config.CONFIDENCE_THRESHOLD}, returning 'no_match'")
            return 'no_match', max_confidence
        
        return predicted_intent, max_confidence

class BertIntentClassifier:
    """
    A class for training and predicting intents using a PyTorch and BERT model.
    """
    def __init__(self, config):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = BertTokenizer.from_pretrained(config.BERT_MODEL_PATH)
        self.model = None
        self.label_map = None
        self.intents = []
        logger.info(f"BERT intent classifier initialized on device: {self.device}")

    def train_model(self, data, preprocessor):
        logger.info("Starting BERT model training process...")
        patterns = []
        labels = []
        for intent in data['intents']:
            # Skip default fallback intent from training/labels
            if intent.get('tag') == 'default':
                continue
            if intent['patterns']:
                for pattern in intent['patterns']:
                    patterns.append(pattern) # BERT can handle raw text
                    labels.append(intent['tag'])
        
        if not patterns:
            logger.error("No training patterns found. Cannot train model.")
            return

        self.intents = sorted(list(set(labels)))
        self.label_map = {tag: i for i, tag in enumerate(self.intents)}
        
        # Prepare dataset
        X_train, X_test, y_train, y_test = train_test_split(
            patterns, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        train_dataset = IntentDataset(X_train, y_train, self.tokenizer, self.label_map)
        test_dataset = IntentDataset(X_test, y_test, self.tokenizer, self.label_map)
        
        train_loader = DataLoader(train_dataset, batch_size=self.config.BERT_BATCH_SIZE, shuffle=True)
        
        # Initialize BERT model
        self.model = BertForSequenceClassification.from_pretrained(
            self.config.BERT_MODEL_PATH, num_labels=len(self.intents)
        )
        self.model.to(self.device)
        
        optimizer = AdamW(self.model.parameters(), lr=self.config.BERT_LEARNING_RATE)
        
        # Training loop
        self.model.train()
        for epoch in range(self.config.BERT_EPOCHS):
            for batch in train_loader:
                optimizer.zero_grad()
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(input_ids, attention_mask=attention_mask, labels=labels)
                loss = outputs.loss
                loss.backward()
                optimizer.step()
            logger.info(f"Epoch {epoch+1}/{self.config.BERT_EPOCHS}, Loss: {loss.item():.4f}")

        # Evaluation (optional)
        self.model.eval()
        true_labels = []
        predictions = []
        test_loader = DataLoader(test_dataset, batch_size=self.config.BERT_BATCH_SIZE)
        with torch.no_grad():
            for batch in test_loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(input_ids, attention_mask=attention_mask)
                logits = outputs.logits
                preds = torch.argmax(logits, dim=1).cpu().numpy()
                
                true_labels.extend(labels.cpu().numpy())
                predictions.extend(preds)

        accuracy = accuracy_score(true_labels, predictions)
        logger.info(f"BERT Model training complete. Accuracy on test data: {accuracy:.2f}")
        logger.info("Classification Report:\n" + classification_report(true_labels, predictions, zero_division=0))

        # Save model
        try:
            # Ensure models directory exists (BERT folder when MODEL_TYPE=bert)
            os.makedirs(os.path.dirname(self.config.MODEL_FILE_PATH), exist_ok=True)
            torch.save(self.model.state_dict(), self.config.MODEL_FILE_PATH)
            with open(self.config.VECTORIZER_FILE_PATH, 'wb') as f: # Re-using vectorizer path for label_map
                pickle.dump(self.label_map, f)
            logger.info("BERT model and label map saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save BERT model files: {e}", exc_info=True)


    def load_model(self):
        logger.info("Loading BERT model from disk...")
        try:
            intents_dir = getattr(self.config, 'INTENTS_DIR', None)
            if intents_dir and os.path.isdir(intents_dir):
                data = load_all_intents(intents_dir)
            else:
                with open(self.config.DATA_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            self.intents = sorted([intent['tag'] for intent in data['intents'] if intent.get('tag') != 'default'])
            self.label_map = {tag: i for i, tag in enumerate(self.intents)}

            self.model = BertForSequenceClassification.from_pretrained(
                self.config.BERT_MODEL_PATH, num_labels=len(self.intents)
            )
            self.model.load_state_dict(torch.load(self.config.MODEL_FILE_PATH))
            self.model.to(self.device)
            self.model.eval()
            logger.info("BERT model loaded successfully.")
            return True
        except (FileNotFoundError, pickle.UnpicklingError) as e:
            logger.error(f"Error loading BERT model files: {e}")
            return False

    def predict_intent(self, preprocessed_tokens):
        if not self.model:
            logger.error("BERT model is not loaded. Cannot predict.")
            return 'unknown', 0.0
        
        text = " ".join(preprocessed_tokens)
        if not text.strip():
            return 'default', 1.0

        encoding = self.tokenizer.encode_plus(
            text,
            truncation=True,
            padding='max_length',
            max_length=64,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        
        with torch.no_grad():
            outputs = self.model(input_ids, attention_mask=attention_mask)
            logits = outputs.logits

        probabilities = torch.softmax(logits, dim=1)
        max_confidence, prediction = torch.max(probabilities, dim=1)
        max_confidence = max_confidence.item()
        prediction = prediction.item()

        predicted_intent = self.intents[prediction]
        logger.info(f"Predicted intent (BERT): '{predicted_intent}' with confidence: {max_confidence:.3f}")

        if max_confidence < self.config.CONFIDENCE_THRESHOLD:
            logger.info(f"Low confidence ({max_confidence:.3f}), below threshold {self.config.CONFIDENCE_THRESHOLD}, returning 'no_match'")
            return 'no_match', max_confidence

        return predicted_intent, max_confidence

class IntentDataset(Dataset):
    """
    A custom PyTorch Dataset for intent classification.
    """
    def __init__(self, texts, labels, tokenizer, label_map):
        self.texts = texts
        self.labels = [label_map[label] for label in labels]
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        
        encoding = self.tokenizer.encode_plus(
            text,
            truncation=True,
            padding='max_length',
            max_length=64,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }
