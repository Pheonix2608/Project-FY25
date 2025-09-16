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
    """
    A class to handle the generation of chatbot responses based on intents.
    """
    def __init__(self, data, config):
        """
        Initializes the response handler with the data.
        
        Args:
            data (dict): The data loaded from `intents.json`.
            config (Config): The configuration object.
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

    def get_response(self, intent_tag, confidence, context):
        """
        Retrieves a random response for a given intent tag.
        
        Args:
            intent_tag (str): The predicted intent tag from the classifier.
            confidence (float): The confidence score of the prediction.
            context (list): A list of recent queries and responses.
            
        Returns:
            str: A randomly selected response string.
        """
        logger.info(f"Getting response for intent '{intent_tag}' with confidence {confidence:.2f} and context: {context}")
        
        # ----- Hooks for advanced generation (future) -----
        if self.config.ENABLE_GENERATIVE_RESPONSE:
            # This is a placeholder for a generative model response.
            # A real implementation would require an asynchronous call to an API or a local model.
            # Example using a placeholder function:
            # return self._generate_llm_response(intent_tag, context)
            pass
        
        if intent_tag in ("unknown", "no_match"):
            logger.warning(f"Unknown intent detected. Logging query for retraining.")
            self._log_unmatched_query(context[-1]['text'] if context else "unknown_query")
            if self.config.ENABLE_GOOGLE_FALLBACK:
                logger.info("Unknown intent, falling back to Google Search.")
                return self.google_fallback(context)
            else:
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

    def google_fallback(self, context):
        """Performs a Google search and returns the results."""
        logger.info({
            'event': 'response_source',
            'source': 'google_fallback'
        })
        user_query = context[-1]['text'] if context else ""
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
            return structured_response
        except Exception as e:
            logger.error({
                'event': 'google_fallback_error',
                'query': user_query,
                'error': str(e)
            })
            return random.choice(self.default_responses)

    async def _get_google_results_with_retry(self, query, retries=2):
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
        """
        Merge Google results into a structured response string.
        """
        if not results:
            return "Sorry, I couldn't find an answer online."
        notice = "(Google Fallback Results)\n"
        merged = notice + f"Top results for '{query}':\n" + "\n".join(f"- {r}" for r in results)
        return merged

    def _log_unmatched_query(self, query):
        """
        Logs a user query that didn't match a known intent.
        
        Args:
            query (str): The user's input string.
        """
        logger.warning(f"UNMATCHED_QUERY: '{query}'")

    def _generate_llm_response(self, intent, context):
        """
        Placeholder for a future LLM-based response generation.
        This would typically be an asynchronous call in a separate thread
        to prevent the GUI from freezing.
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
