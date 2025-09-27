# ==============================================================================
# model/ner_extractor.py
# Named Entity Recognition (NER) module to extract entities from text.
# ==============================================================================
import spacy
from spacy.cli import download as spacy_download
from utils.logger import get_logger

logger = get_logger(__name__)

class NERExtractor:
    """
    A class to extract named entities from text using spaCy.
    """
    def __init__(self, model_name="en_core_web_sm"):
        self.model_name = model_name
        self.nlp = self.load_model()
        logger.info(f"NER Extractor initialized with model: {self.model_name}")

    def load_model(self):
        """
        Load the spaCy model, downloading it if it doesn't exist.
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
        """
        Extract named entities from the given text.

        :param text: The input string.
        :return: A list of extracted entities, where each entity is a dictionary.
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