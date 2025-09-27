# ==============================================================================
# utils/data_augmentation.py
# Data augmentation techniques to expand the training dataset.
# ==============================================================================
import nltk
from nltk.corpus import wordnet
import random

from utils.logger import get_logger

logger = get_logger(__name__)

def get_synonyms(word):
    """Gets synonyms for a word using WordNet.

    Args:
        word (str): The word to find synonyms for.

    Returns:
        list: A list of synonyms for the given word.
    """
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    if word in synonyms:
        synonyms.remove(word)
    return list(synonyms)

def synonym_replacement(sentence, n=1):
    """Performs synonym replacement on a sentence.

    This function randomly replaces words in a sentence with their synonyms.

    Args:
        sentence (str): The input sentence.
        n (int): The number of words to replace with synonyms.

    Returns:
        str: The sentence with words replaced by synonyms.
    """
    words = sentence.split()
    new_words = words.copy()
    random_word_list = list(set([word for word in words if wordnet.synsets(word)]))
    random.shuffle(random_word_list)

    num_replaced = 0
    for random_word in random_word_list:
        synonyms = get_synonyms(random_word)
        if len(synonyms) >= 1:
            synonym = random.choice(list(synonyms))
            new_words = [synonym if word == random_word else word for word in new_words]
            num_replaced += 1
        if num_replaced >= n:
            break

    return ' '.join(new_words)

def augment_data(data, augmentation_factor=1, keep_originals=True):
    """Augments intent data using synonym replacement.

    This function increases the diversity of training data by creating new
    patterns from existing ones.

    Args:
        data (dict): The original intent data.
        augmentation_factor (int): The number of augmented versions to create
            for each original pattern.
        keep_originals (bool): Whether to include the original patterns in the
            augmented dataset.

    Returns:
        dict: The augmented intent data.
    """
    augmented_data = {'intents': []}

    for intent in data['intents']:
        new_intent = intent.copy()
        new_patterns = []

        if keep_originals:
            new_patterns.extend(intent['patterns'])

        for _ in range(augmentation_factor):
            for pattern in intent['patterns']:
                augmented_pattern = synonym_replacement(pattern)
                if augmented_pattern != pattern:
                    new_patterns.append(augmented_pattern)

        new_intent['patterns'] = list(set(new_patterns)) # Remove duplicates
        augmented_data['intents'].append(new_intent)

    logger.info(f"Data augmentation complete. Original patterns: {sum(len(i['patterns']) for i in data['intents'])}, "
                f"Augmented patterns: {sum(len(i['patterns']) for i in augmented_data['intents'])}")

    return augmented_data