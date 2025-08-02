# 🤖 Chatbot Desktop Application

An intelligent desktop chatbot application built with **Python**, **PyQt6**, and a **BERT-based intent classifier**. Designed for seamless human-like conversation, the chatbot features a sleek GUI, conversational memory, theme toggling, and an easy retraining mechanism. Ideal for learners and developers looking to dive into modern NLP applications.

---

## 🚀 Features

* **🔍 Intent Classification** — Utilizes a BERT-based model to identify user intents (e.g., greetings, questions, jokes).
* **🧠 Contextual Memory** — Maintains short-term conversational memory for more relevant responses.
* **🖼️ Modern GUI** — Built with PyQt6 featuring a clean chat interface, input field, and control buttons.
* **🎨 Light/Dark Theme** — Supports theme switching for a personalized user experience.
* **💾 Chat History** — Save and reload conversations anytime.
* **🧪 On-Demand Retraining** — Update your chatbot’s intelligence from the GUI itself.
* **📋 Developer Logging** — Custom `dev_log.py` module to log performance, changes, and runtime exceptions.

---

## ⚙️ Getting Started

### ✅ Prerequisites

* Python 3.8+
* A pre-trained model (auto-trained on first run if missing)

### 🔧 Installation

```bash
# Clone the repo
git clone https://github.com/your_username/your_project.git
cd your_project

# Set up a virtual environment
python -m venv venv

# Activate it
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

Ensure that your `intents.json` file has valid and structured training data.

---

## 🧱 Project Structure

```bash
your_project/
├── main.py                   # App entry point
├── config.py                 # Global settings
├── dev_log.py                # Custom developer logger
├── data/
│   ├── intents.json          # Training data
│   └── conversation_history.json  # Saved chat history
├── gui/
│   └── chatbot_gui.py        # PyQt6 GUI
├── model/
│   ├── intent_classifier.py  # Model train/predict logic
│   ├── response_handler.py   # Response generation logic
│   ├── context_handler.py    # Context tracking
│   └── model.pkl             # Trained BERT model
└── utils/
    ├── logger.py             # Logger setup
    └── preprocessing.py      # NLP preprocessing
```

---

## 🧪 How to Use

1. Activate your virtual environment.
2. Run the app:

```bash
python main.py
```

3. If no model exists, it trains automatically using `intents.json`.
4. Chat away with the bot using the GUI!

---

## 🔧 Customization

Want to add your own flavor?

* **Add Intents** — Modify `data/intents.json` to add new intent tags with patterns and responses.
* **Update Training Data** — Expand existing intents with more varied phrases.
* **Retrain Easily** — Use the "Retrain Model" button in the GUI.

---

## 📚 Dependencies

* [PyQt6](https://pypi.org/project/PyQt6/)
* [Transformers](https://huggingface.co/transformers/)
* [Torch](https://pytorch.org/)
* [Scikit-learn](https://scikit-learn.org/)
* [NLTK](https://www.nltk.org/)

---

## 🪪 License

This project is open-source under the MIT License. Feel free to fork, modify, and distribute with attribution.

---

## 🙌 Credits

Crafted with ❤️ by Final Year Engineering Students — Aaryan, Hrishi, Bhavay K., Bhavya K.

Project Guide: *Er. Amit Tewari*, Associate Professor, Dept. of CSE, Arya College of Engineering & I.T.

---

Got suggestions or want to contribute? [Open an issue](https://github.com/your_username/your_project/issues) or send a PR!
