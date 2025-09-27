# ==============================================================================
# model/intent_classifier.py
# Intent classification module with a factory pattern for different models.
# ==============================================================================
import pickle
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import accuracy_score, classification_report
import os

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification
from torch.optim import AdamW # Import AdamW directly from PyTorch

from utils.logger import get_logger
from utils.data_loader import load_all_intents
from utils.data_augmentation import augment_data

logger = get_logger(__name__)

class IntentClassifier:
    """A factory class for creating and managing intent classifiers.

    This class instantiates a specific classifier (e.g., SVM, BERT) based on
    the application's configuration and delegates tasks like training and
    prediction to the chosen classifier instance.
    """
    def __init__(self, config):
        """Initializes the IntentClassifier factory.

        Args:
            config (Config): The application's configuration object.

        Raises:
            ValueError: If the `MODEL_TYPE` in the config is unknown.
        """
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
        """Delegates model training to the specific classifier instance.

        Args:
            data (dict): The intent data for training.
            preprocessor (TextPreprocessor): The text preprocessor instance.
        """
        self.classifier.train_model(data, preprocessor)

    def load_model(self):
        """Delegates model loading to the specific classifier instance."""
        self.classifier.load_model()
    
    def predict_intent(self, preprocessed_tokens):
        """Delegates intent prediction to the specific classifier instance.

        Args:
            preprocessed_tokens (list): A list of preprocessed tokens.

        Returns:
            tuple: A tuple containing the predicted intent (str) and the
                confidence score (float).
        """
        return self.classifier.predict_intent(preprocessed_tokens)


class SVMIntentClassifier:
    """An intent classifier using a Support Vector Machine (SVM).

    This class handles training, testing, and predicting intents using a
    scikit-learn SVM classifier with a TF-IDF vectorizer.
    """
    def __init__(self, config):
        """Initializes the SVMIntentClassifier.

        Args:
            config (Config): The application's configuration object.
        """
        self.config = config
        self.model = None
        self.vectorizer = None
        self.intents = []
        logger.info("SVM intent classifier initialized.")

    def train_model(self, data, preprocessor):
        """Trains the SVM model.

        This involves vectorizing the text patterns, performing cross-validation,
        and finally training a new model on the entire dataset before saving it.

        Args:
            data (dict): The intent training data.
            preprocessor (TextPreprocessor): The text preprocessor instance.
        """
        logger.info("Starting SVM model training process...")

        if getattr(self.config, 'USE_DATA_AUGMENTATION', False):
            logger.info("Augmenting data...")
            data = augment_data(data)

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
        
        X_vec = self.vectorizer.fit_transform(patterns)
        y_np = np.array(labels)

        # Cross-validation
        n_splits = self.config.CROSS_VALIDATION_FOLDS if hasattr(self.config, 'CROSS_VALIDATION_FOLDS') else 5
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
        
        accuracies = []
        for fold, (train_index, test_index) in enumerate(skf.split(X_vec, y_np)):
            X_train, X_test = X_vec[train_index], X_vec[test_index]
            y_train, y_test = y_np[train_index], y_np[test_index]

            model = SVC(kernel='rbf', C=1.0, gamma='scale', probability=True, random_state=42)
            model.fit(X_train, y_train)

            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            accuracies.append(accuracy)
            logger.info(f"Fold {fold+1}/{n_splits} Accuracy: {accuracy:.2f}")

        logger.info(f"Average Cross-Validation Accuracy: {np.mean(accuracies):.2f}")

        # Retrain on the full dataset
        logger.info("Retraining SVM model on the entire dataset...")
        self.model = SVC(kernel='rbf', C=1.0, gamma='scale', probability=True, random_state=42)
        self.model.fit(X_vec, y_np)

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
        """Loads the SVM model and vectorizer from disk.

        Returns:
            bool: True if the model was loaded successfully, False otherwise.
        """
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
        """Predicts the intent for a list of preprocessed tokens.

        Args:
            preprocessed_tokens (list): The preprocessed text tokens.

        Returns:
            tuple: A tuple containing the predicted intent (str) and the
                confidence score (float).
        """
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
        
        # If confidence is too low, return 'no_match'
        if max_confidence < 0.3:
            logger.info(f"Low confidence ({max_confidence:.3f}), returning 'no_match'")
            return 'no_match', max_confidence

        return predicted_intent, max_confidence

class BertIntentClassifier:
    """An intent classifier using a pre-trained BERT model.

    This class handles training, loading, and predicting intents from text
    using a BERT model from the Hugging Face transformers library.
    """
    def __init__(self, config):
        """Initializes the BertIntentClassifier.

        Args:
            config (Config): The application's configuration object.
        """
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = BertTokenizer.from_pretrained(config.BERT_MODEL_PATH)
        self.model = None
        self.label_map = None
        self.intents = []
        logger.info(f"BERT intent classifier initialized on device: {self.device}")

    def train_model(self, data, preprocessor):
        """Trains the BERT model.

        This involves preparing the data, performing cross-validation, and
        finally training a new model on the entire dataset before saving it.

        Args:
            data (dict): The intent training data.
            preprocessor (TextPreprocessor): The text preprocessor instance.
                (Note: Not used by BERT as it has its own tokenizer).
        """
        logger.info("Starting BERT model training process...")

        if getattr(self.config, 'USE_DATA_AUGMENTATION', False):
            logger.info("Augmenting data...")
            data = augment_data(data)

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
        
        # Cross-validation for BERT
        n_splits = self.config.CROSS_VALIDATION_FOLDS if hasattr(self.config, 'CROSS_VALIDATION_FOLDS') else 5
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
        
        patterns_np = np.array(patterns)
        labels_np = np.array(labels)
        
        fold_accuracies = []
        for fold, (train_index, test_index) in enumerate(skf.split(patterns_np, labels_np)):
            logger.info(f"--- Fold {fold+1}/{n_splits} ---")
            X_train, X_test = patterns_np[train_index], patterns_np[test_index]
            y_train, y_test = labels_np[train_index], labels_np[test_index]

            train_dataset = IntentDataset(X_train, y_train, self.tokenizer, self.label_map)
            test_dataset = IntentDataset(X_test, y_test, self.tokenizer, self.label_map)

            train_loader = DataLoader(train_dataset, batch_size=self.config.BERT_BATCH_SIZE, shuffle=True)
            test_loader = DataLoader(test_dataset, batch_size=self.config.BERT_BATCH_SIZE)

            model = BertForSequenceClassification.from_pretrained(self.config.BERT_MODEL_PATH, num_labels=len(self.intents))
            model.to(self.device)
            optimizer = AdamW(model.parameters(), lr=self.config.BERT_LEARNING_RATE)

            # Training loop for the fold
            model.train()
            for epoch in range(self.config.BERT_EPOCHS):
                for batch in train_loader:
                    optimizer.zero_grad()
                    input_ids = batch['input_ids'].to(self.device)
                    attention_mask = batch['attention_mask'].to(self.device)
                    labels = batch['labels'].to(self.device)
                    outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
                    loss = outputs.loss
                    loss.backward()
                    optimizer.step()

            # Evaluation for the fold
            model.eval()
            true_labels, predictions = [], []
            with torch.no_grad():
                for batch in test_loader:
                    input_ids = batch['input_ids'].to(self.device)
                    attention_mask = batch['attention_mask'].to(self.device)
                    labels = batch['labels'].to(self.device)
                    outputs = model(input_ids, attention_mask=attention_mask)
                    logits = outputs.logits
                    preds = torch.argmax(logits, dim=1).cpu().numpy()
                    true_labels.extend(labels.cpu().numpy())
                    predictions.extend(preds)

            accuracy = accuracy_score(true_labels, predictions)
            fold_accuracies.append(accuracy)
            logger.info(f"Fold {fold+1} Accuracy: {accuracy:.2f}")

        logger.info(f"Average BERT Cross-Validation Accuracy: {np.mean(fold_accuracies):.2f}")

        # Retrain on the full dataset
        logger.info("Retraining BERT model on the entire dataset...")
        full_dataset = IntentDataset(patterns, labels, self.tokenizer, self.label_map)
        full_loader = DataLoader(full_dataset, batch_size=self.config.BERT_BATCH_SIZE, shuffle=True)
        
        self.model = BertForSequenceClassification.from_pretrained(self.config.BERT_MODEL_PATH, num_labels=len(self.intents))
        self.model.to(self.device)
        optimizer = AdamW(self.model.parameters(), lr=self.config.BERT_LEARNING_RATE)
        
        self.model.train()
        for epoch in range(self.config.BERT_EPOCHS):
            for batch in full_loader:
                optimizer.zero_grad()
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                outputs = self.model(input_ids, attention_mask=attention_mask, labels=labels)
                loss = outputs.loss
                loss.backward()
                optimizer.step()

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
        """Loads the fine-tuned BERT model and label map from disk.

        Returns:
            bool: True if the model was loaded successfully, False otherwise.
        """
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
        """Predicts the intent for a list of preprocessed tokens.

        Args:
            preprocessed_tokens (list): The preprocessed text tokens.

        Returns:
            tuple: A tuple containing the predicted intent (str) and the
                confidence score (float).
        """
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

        if max_confidence < 0.3:
            logger.info(f"Low confidence ({max_confidence:.3f}), returning 'no_match'")
            return 'no_match', max_confidence

        return predicted_intent, max_confidence

class IntentDataset(Dataset):
    """A custom PyTorch Dataset for preparing intent data for BERT.

    This class takes texts and labels and formats them into tensors that
    can be fed into a BERT model.
    """
    def __init__(self, texts, labels, tokenizer, label_map):
        """Initializes the IntentDataset.

        Args:
            texts (list): A list of text patterns.
            labels (list): A list of corresponding intent labels.
            tokenizer: The BERT tokenizer instance.
            label_map (dict): A mapping from string labels to integer indices.
        """
        self.texts = texts
        self.labels = [label_map[label] for label in labels]
        self.tokenizer = tokenizer

    def __len__(self):
        """Returns the total number of samples in the dataset."""
        return len(self.texts)

    def __getitem__(self, idx):
        """Retrieves and formats a sample from the dataset at the given index.

        Args:
            idx (int): The index of the sample to retrieve.

        Returns:
            dict: A dictionary containing the `input_ids`, `attention_mask`,
                and `labels` tensors for the sample.
        """
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
