"""
utils/web_search.py
Async Google Search module for chatbot fallback.
"""
import asyncio
import aiohttp
import time
from typing import List, Dict
from utils.logger import get_logger
from config import Config

logger = get_logger(__name__)

# Simple in-memory cache
_cache: Dict[str, Dict] = {}

async def query_google(query: str) -> List[str]:
    """
    Asynchronously query Google Search API or placeholder for top text snippets.
    Implements caching, rate-limiting, and error handling.
    Args:
        query (str): The search query string.
    Returns:
        List[str]: List of top text snippets from Google search results.
    """
    cache_key = query.lower().strip()
    now = time.time()
    # Check cache
    cached = _cache.get(cache_key)
    if cached and now - cached['timestamp'] < Config.GOOGLE_CACHE_DURATION:
        logger.info({
            'event': 'google_cache_hit',
            'query': query,
            'source': 'cache',
            'results_count': len(cached['results'])
        })
        return cached['results']

    # Rate limiting: allow 1 request per second
    if hasattr(query_google, '_last_call'):
        elapsed = now - getattr(query_google, '_last_call')
        if elapsed < 1.0:
            await asyncio.sleep(1.0 - elapsed)
    query_google._last_call = time.time()

    # Placeholder for Google API call
    try:
        # Replace this block with actual Google API integration
        async with aiohttp.ClientSession() as session:
            # Example: Simulate network call
            await asyncio.sleep(0.5)
            # Simulated results
            results = [
                f"Google result {i+1} for '{query}'"
                for i in range(Config.GOOGLE_MAX_RESULTS)
            ]
        # Cache results
        _cache[cache_key] = {'results': results, 'timestamp': time.time()}
        logger.info({
            'event': 'google_search',
            'query': query,
            'source': 'google_api',
            'results_count': len(results)
        })
        return results
    except Exception as e:
        logger.error({
            'event': 'google_search_error',
            'query': query,
            'error': str(e)
        })
        return ["Sorry, I couldn't fetch results from Google at the moment."]
