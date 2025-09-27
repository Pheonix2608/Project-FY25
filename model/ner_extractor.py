# ==============================================================================
# model/ner_extractor.py
# Named Entity Recognition (NER) module to extract entities from text.
# ==============================================================================
import spacy
from spacy.cli import download as spacy_download
from utils.logger import get_logger

logger = get_logger(__name__)

class NERExtractor:
    """Extracts named entities from text using a spaCy model.

    This class provides functionality to load a spaCy model and use it to
    identify and extract named entities like persons, organizations, or dates.
    """
    def __init__(self, model_name="en_core_web_sm"):
        """Initializes the NERExtractor.

        Args:
            model_name (str): The name of the spaCy model to use for NER.
        """
        self.model_name = model_name
        self.nlp = self.load_model()
        logger.info(f"NER Extractor initialized with model: {self.model_name}")

    def load_model(self):
        """Loads the spaCy model, downloading it if necessary.

        Returns:
            spacy.Language: The loaded spaCy language model, or None if
                loading fails.
        """
        try:
            return spacy.load(self.model_name)
        except OSError:
            logger.warning(f"Spacy model '{self.model_name}' not found. Downloading...")
            try:
                spacy_download(self.model_name)
                return spacy.load(self.model_name)
            except Exception as e:
                logger.error(f"Failed to download or load spacy model '{self.model_name}': {e}", exc_info=True)
                return None

    def extract_entities(self, text):
        """Extracts named entities from a given text.

        Args:
            text (str): The input text to process.

        Returns:
            list: A list of dictionaries, where each dictionary represents a
                found entity and contains its text, label, start, and end
                character positions.
        """
        if not self.nlp:
            logger.error("NER model is not loaded. Cannot extract entities.")
            return []

        doc = self.nlp(text)
        entities = []
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            })

        if entities:
            logger.info(f"Extracted entities: {entities}")

        return entities