# Model Training and Retraining Guide

## Overview
This document explains how to train and retrain the chatbot models (SVM and BERT), data formats, recommended hardware, and the background retraining workflow implemented in `main.py`.

## Data Format
- Training data is stored in `data/intents/` as JSON files. Each intent file should follow the pattern:
```json
{
  "tag": "greeting",
  "patterns": ["Hi", "Hello", "Hey there"],
  "responses": ["Hello!", "Hi there!"],
  "context_set": "optional"
}
```

## Training SVM Model (local)
1. Ensure dependencies are installed:
```bash
pip install -r requirements.txt
```
2. Run the training script (TODO: add training script path if exists):
```bash
python -m model.intent_classifier --train --data-dir data/intents/ --out-dir model/svm
```

## Training BERT Model (local, GPU recommended)
1. Install PyTorch with CUDA support. Example for CUDA 11.8:
```bash
pip install torch --extra-index-url https://download.pytorch.org/whl/cu118
pip install transformers
```
2. Run the BERT training script (TODO: script path):
```bash
python -m model.bert_classifier --train --data-dir data/intents/ --out-dir model/bert --epochs 3 --batch-size 16
```

## Background Retraining (zero downtime)
- The application exposes `ChatbotApp.retrain_model(background=True)` which runs retraining in a background thread and hot-swaps the model on completion.
- Logs indicate start, progress, completion, and errors.

## Retraining Best Practices
- Keep a copy of previous model artifacts (model/svm and model/bert) before replacing.
- Validate new model on a held-out test set before hot-swap in critical systems.
- Use small batches for quick incremental updates.

## Monitoring and Logs
- Training progress and errors are logged to `logs/app.log`.
- For long jobs, prefer running training in a terminal and monitoring GPU usage with `nvidia-smi`.

## TODO
- Insert exact script commands if training scripts are provided in the repository.
- Add validation and fine-tuning instructions.
