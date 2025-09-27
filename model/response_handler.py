# ==============================================================================
# model/response_handler.py
# A class for handling chatbot responses.
# ==============================================================================
import random
import json
import os
import requests # assuming requests is available

from utils.logger import get_logger

logger = get_logger(__name__)

class ResponseHandler:
    """Handles the generation of chatbot responses based on intents.

    This class selects an appropriate response for a given intent,
    manages fallbacks (like Google Search), and can incorporate
    personalization based on extracted entities.
    """
    def __init__(self, data, config):
        """Initializes the ResponseHandler.

        Args:
            data (dict): The loaded intent data, typically from JSON files.
            config (Config): The application's configuration object.
        """
        self.config = config
        self.intents = data['intents']
        # Store default responses separately and exclude from main response map
        default_intent = next((i for i in self.intents if i.get('tag') == 'default'), None)
        self.default_responses = (default_intent or {}).get('responses', ["I'm not sure what to say."])
        self.response_map = {
            intent['tag']: intent.get('responses', [])
            for intent in self.intents
            if intent.get('tag') != 'default'
        }
        logger.info("Response handler initialized with rules-based responses.")

    def get_response(self, intent_tag, confidence, context, entities=None):
        """Retrieves a response for a given intent.

        This method selects a response based on the intent tag. It can
        personalize responses using NER entities and trigger a Google
        Search fallback if the intent is unknown or has no defined response.

        Args:
            intent_tag (str): The predicted intent tag.
            confidence (float): The confidence score of the prediction.
            context (list): The history of the conversation.
            entities (list, optional): Extracted named entities. Defaults to None.

        Returns:
            str: A response string.
        """
        logger.info(f"Getting response for intent '{intent_tag}' with confidence {confidence:.2f}, context: {context}, and entities: {entities}")
        
        # ----- Hooks for advanced generation (future) -----
        if self.config.ENABLE_GENERATIVE_RESPONSE:
            # This is a placeholder for a generative model response.
            pass
        
        # Personalize response if a person's name is detected
        if entities:
            for entity in entities:
                if entity['label'] == 'PERSON':
                    person_name = entity['text']
                    # Example of using the name in a greeting
                    if intent_tag == 'greeting':
                         return f"Hello {person_name}! How can I help you today?"

        if intent_tag in ("unknown", "no_match"):
            logger.warning(f"Unknown intent detected. Returning default response.")
            self._log_unmatched_query(context[-1]['text'] if context else "unknown_query")
            return random.choice(self.default_responses)
        
        # Handle explicit default tag without warning
        if intent_tag == 'default':
            return random.choice(self.default_responses)

        responses = self.response_map.get(intent_tag)
        if responses:
            logger.info({
                'event': 'response_source',
                'source': 'local',
                'intent_tag': intent_tag,
                'response': responses
            })
            return random.choice(responses)

        # If no local response, fallback to Google
        if self.config.ENABLE_GOOGLE_FALLBACK:
            return self.google_fallback(context)

        logger.warning({
            'event': 'response_source',
            'source': 'default',
            'intent_tag': intent_tag
        })
        return random.choice(self.default_responses)

    def google_fallback(self, query: str):
        """Performs a Google search as a fallback action.

        Args:
            query (str): The user query to search for.

        Returns:
            str: A formatted string of search results or a default message
                if the search fails.
        """
        logger.info({
            'event': 'response_source',
            'source': 'google_fallback'
        })
        user_query = query
        import asyncio
        from utils.web_search import query_google
        loop = asyncio.get_event_loop()
        try:
            google_results = loop.run_until_complete(self._get_google_results_with_retry(user_query))
            structured_response = self._merge_google_results(user_query, google_results)
            logger.info({
                'event': 'google_fallback_response',
                'query': user_query,
                'results': google_results
            })
            confirmation = "(This answer was sourced from Google Search because no matching intent was found.)"
            return f"{structured_response}\n\n{confirmation}"
        except Exception as e:
            logger.error({
                'event': 'google_fallback_error',
                'query': user_query,
                'error': str(e)
            })
            return random.choice(self.default_responses)

    async def _get_google_results_with_retry(self, query, retries=2):
        """Attempts to perform a Google search with retries.

        Args:
            query (str): The search query.
            retries (int): The number of times to retry on failure.

        Returns:
            list: A list of search result strings.

        Raises:
            Exception: If all search attempts fail.
        """
        for attempt in range(retries + 1):
            try:
                from utils.web_search import query_google
                return await query_google(query)
            except Exception as e:
                logger.warning(f"Google search attempt {attempt+1} failed: {e}")
                import asyncio
                await asyncio.sleep(1)
        raise Exception("All Google search attempts failed.")

    def _merge_google_results(self, query, results):
        """Merges Google search results into a formatted string.

        Args:
            query (str): The original search query.
            results (list): A list of search result strings.

        Returns:
            str: A formatted string containing the search results.
        """
        if not results:
            return "Sorry, I couldn't find an answer online."
        notice = "(Google Fallback Results)\n"
        merged = notice + f"Top results for '{query}':\n" + "\n".join(f"- {r}" for r in results)
        return merged

    def _log_unmatched_query(self, query):
        """Logs a user query that did not match any known intent.

        Args:
            query (str): The user's input string.
        """
        logger.warning(f"UNMATCHED_QUERY: '{query}'")

    def _generate_llm_response(self, intent, context):
        """A placeholder for future LLM-based response generation.

        This method is intended to be a hook for integrating a large language
        model for more dynamic and context-aware responses.

        Args:
            intent (str): The detected intent.
            context (list): The conversation history.
        """
        # Example: call to an LLM API or a local model
        # prompt = f"The user's intent is '{intent}'. Conversation history: {context}. Respond appropriately."
        # try:
        #     # The following is a placeholder for a real API call.
        #     # In a production app, you would use an async library like `httpx`
        #     # and a proper API key management system.
        #     # from gemini_api_client import generate_response
        #     # response = generate_response(prompt)
        #     # return response
        # except Exception as e:
        #     logger.error(f"LLM API call failed: {e}")
        #     return "I am having trouble with my generative model at the moment."
        pass
