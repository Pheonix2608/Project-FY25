"""Data loading utilities for the chatbot."""
import os
import json
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

def load_all_intents(intents_dir: str) -> Dict:
    """Loads and merges all intent JSON files from a directory.

    This function reads all `.json` files in the specified directory,
    merging them into a single dictionary. It handles various JSON
    formats and ensures a default intent is present.

    Args:
        intents_dir (str): The path to the directory containing intent files.

    Returns:
        Dict: A dictionary containing a list of all loaded intents.
            Returns a dictionary with an empty list if an error occurs.
    """
    all_intents = {"intents": []}

    try:
        # Ensure we load other.json last so its default intent is available
        json_files = [f for f in os.listdir(intents_dir) if f.endswith('.json')]
        if 'other.json' in json_files:
            json_files.remove('other.json')
            json_files.append('other.json')

        for filename in json_files:
            filepath = os.path.join(intents_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Accept multiple formats:
                    # 1) { "intents": [ ... ] }
                    # 2) Single intent object { "tag": ..., "responses": [...] }
                    # 3) List of intent objects [ {"tag":...}, ... ]
                    if isinstance(data, dict) and 'intents' in data and isinstance(data['intents'], list):
                        all_intents['intents'].extend(data['intents'])
                        logger.info(f"Loaded intents from {filename}")
                    elif isinstance(data, dict) and data.get('tag') and data.get('responses'):
                        all_intents['intents'].append(data)
                        logger.info(f"Loaded single intent from {filename}: {data.get('tag')}")
                    elif isinstance(data, list):
                        all_intents['intents'].extend([i for i in data if isinstance(i, dict) and i.get('tag')])
                        logger.info(f"Loaded {len(data)} intents from list in {filename}")
                    else:
                        logger.warning(f"Unrecognized intent format in {filename}")
            except json.JSONDecodeError:
                logger.error(f"Error decoding JSON from {filename}")
            except Exception as e:
                logger.error(f"Error loading {filename}: {str(e)}")

        # Ensure default intent exists
        default_intent = next((intent for intent in all_intents['intents'] if intent.get('tag') == 'default'), None)

        if not default_intent:
            logger.warning("No default intent found; creating a minimal fallback.")
            default_intent = {
                "tag": "default",
                "patterns": [],
                "responses": ["I'm not sure how to respond to that."]
            }
            all_intents['intents'].append(default_intent)

        return all_intents

    except Exception as e:
        logger.error(f"Error loading intents: {str(e)}")
        return {"intents": []}
