### ===============================
### 1. model/bert_classifier.py
### ===============================

import torch
import pickle
import json
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification, AdamW
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from utils.logger import get_logger

logger = get_logger(__name__)

class BertIntentClassifier:
    def __init__(self, config):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = BertTokenizer.from_pretrained(config.BERT_MODEL_PATH)
        self.model = None
        self.label_map = None
        self.intents = []
        logger.info(f"BERT classifier initialized on device: {self.device}")

    def train_model(self, data, preprocessor=None):
        patterns, labels = [], []
        for intent in data['intents']:
            for pattern in intent['patterns']:
                patterns.append(pattern)
                labels.append(intent['tag'])

        self.intents = sorted(set(labels))
        self.label_map = {tag: i for i, tag in enumerate(self.intents)}

        X_train, X_test, y_train, y_test = train_test_split(
            patterns, labels, test_size=0.2, random_state=42, stratify=labels
        )

        train_dataset = IntentDataset(X_train, y_train, self.tokenizer, self.label_map)
        test_dataset = IntentDataset(X_test, y_test, self.tokenizer, self.label_map)
        train_loader = DataLoader(train_dataset, batch_size=self.config.BERT_BATCH_SIZE, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=self.config.BERT_BATCH_SIZE)

        self.model = BertForSequenceClassification.from_pretrained(
            self.config.BERT_MODEL_PATH, num_labels=len(self.intents))
        self.model.to(self.device)

        optimizer = AdamW(self.model.parameters(), lr=self.config.BERT_LEARNING_RATE)

        self.model.train()
        for epoch in range(self.config.BERT_EPOCHS):
            for batch in train_loader:
                optimizer.zero_grad()
                inputs = {k: v.to(self.device) for k, v in batch.items()}
                outputs = self.model(**inputs)
                outputs.loss.backward()
                optimizer.step()
            logger.info(f"Epoch {epoch+1}: Loss = {outputs.loss.item():.4f}")

        self.model.eval()
        true, preds = [], []
        with torch.no_grad():
            for batch in test_loader:
                inputs = {k: v.to(self.device) for k, v in batch.items() if k != 'labels'}
                labels = batch['labels'].to(self.device)
                logits = self.model(**inputs).logits
                pred = torch.argmax(logits, dim=1)
                true.extend(labels.cpu().numpy())
                preds.extend(pred.cpu().numpy())

        acc = accuracy_score(true, preds)
        logger.info(f"BERT accuracy: {acc:.2f}")
        logger.info(classification_report(true, preds))

        import os
        os.makedirs(os.path.dirname(self.config.MODEL_FILE_PATH), exist_ok=True)
        torch.save(self.model.state_dict(), self.config.MODEL_FILE_PATH)
        with open(self.config.VECTORIZER_FILE_PATH, 'wb') as f:
            pickle.dump(self.label_map, f)

    def load_model(self):
        with open(self.config.DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.intents = sorted(intent['tag'] for intent in data['intents'])
            self.label_map = {tag: i for i, tag in enumerate(self.intents)}

        self.model = BertForSequenceClassification.from_pretrained(
            self.config.BERT_MODEL_PATH, num_labels=len(self.intents))
        self.model.load_state_dict(torch.load(self.config.MODEL_FILE_PATH))
        self.model.to(self.device)
        self.model.eval()

    def predict_intent(self, preprocessed_tokens):
        text = " ".join(preprocessed_tokens)
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=64)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            logits = self.model(**inputs).logits
        prediction = torch.argmax(logits, dim=1).item()
        return self.intents[prediction]

class IntentDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, label_map):
        self.texts = texts
        self.labels = [label_map[label] for label in labels]
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.texts[idx], truncation=True, padding='max_length', max_length=64, return_tensors='pt'
        )
        return {
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'labels': torch.tensor(self.labels[idx], dtype=torch.long)
        }

