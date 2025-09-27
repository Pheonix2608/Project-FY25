# Model Training and Retraining Guide

## Overview

This guide explains how to add new training data and retrain the chatbot's intent classification models. The primary and recommended method for retraining is through the application's **Admin Panel**, which provides a user-friendly interface for this task.

## How the Chatbot Learns: Intents

The chatbot understands user requests by classifying them into **intents**. An intent represents a goal or purpose behind a user's message. For example, a user saying "Hello there" has a `greeting` intent.

Intents are defined in `.json` files located in the `data/intents/` directory. The application automatically loads and merges all `.json` files from this directory.

### Intent File Format

Each intent file should contain a list of intent objects. Each object must have the following structure:

```json
{
  "intents": [
    {
      "tag": "your_intent_name",
      "patterns": [
        "A phrase a user might say for this intent.",
        "Another example of what a user might type.",
        "More patterns lead to better accuracy."
      ],
      "responses": [
        "The response the chatbot should give for this intent.",
        "You can provide multiple responses, and the bot will choose one randomly."
      ]
    }
  ]
}
```

-   `tag`: A unique name for the intent (e.g., `goodbye`, `order_status`).
-   `patterns`: A list of example sentences or phrases that correspond to this intent. The more diverse the patterns, the better the model will perform.
-   `responses`: A list of possible responses the chatbot can use when it identifies this intent.

## Adding New Training Data

To teach the chatbot new skills, simply add or edit the `.json` files in the `data/intents/` directory.

1.  **Create a New File**: You can add a new file (e.g., `new_skills.json`) to the `data/intents/` directory to keep your new intents organized.
2.  **Add Your Intent**: Follow the format described above to add your new intent(s) to the file.
3.  **Save the File**: Save your changes.
4.  **Retrain the Model**: Follow the steps in the next section to make your changes live.

## Retraining the Model (Recommended Method)

The easiest way to retrain the model is by using the **Admin Panel**.

1.  **Launch the Application**: Run the application to open the Admin Panel.
    ```bash
    python main.py
    ```
2.  **Navigate to the Settings Tab**: Click on the "Settings" tab.
3.  **Choose a Retraining Option**:
    -   **Retrain Model (Blocking)**: This option will retrain the model in the foreground. The application may be unresponsive until the training is complete. This is suitable for smaller datasets or when you want immediate confirmation.
    -   **Retrain Model (Background)**: This is the **recommended** option for larger datasets. It runs the entire training process in a background thread, allowing you to continue using the application without interruption. You will see a notification in the Chat Tester tab once the training is complete and the new model is "hot-swapped" into the live application.

After the retraining process finishes, the chatbot will be updated with its new knowledge.

## Model Types (SVM vs. BERT)

The application supports two different models for intent classification, which can be selected in `config.py` or via the `MODEL_TYPE` environment variable.

-   **`svm` (Support Vector Machine)**: A classic, fast, and reliable machine learning model. It works well for small to medium-sized datasets and does not require a GPU.
-   **`bert` (BERT)**: A powerful, modern transformer-based model that can achieve higher accuracy, especially with more complex and nuanced data. Training a BERT model is significantly more resource-intensive and will be much faster on a machine with a CUDA-enabled GPU.

When you trigger a retrain, the application will automatically use the model type currently specified in the configuration.