from typing import List, Dict, Any, Optional, AsyncGenerator
import aiohttp
import asyncio
import logging
from datetime import datetime, timedelta
import time

class ScryfallAPIError(Exception):
    """Custom exception for Scryfall API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(message)

class RateLimiter:
    """Simple rate limiter to prevent API abuse"""
    def __init__(self, requests_per_second: float = 10):
        self.minimum_interval = 1.0 / requests_per_second
        self.last_request_time = 0

    async def acquire(self):
        """Wait if necessary to maintain rate limit"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.minimum_interval:
            await asyncio.sleep(self.minimum_interval - time_since_last_request)
        self.last_request_time = time.time()

class ScryfallService:
    """
    A service class for interacting with the Scryfall API.
    
    Implements rate limiting and proper error handling according to Scryfall's API guidelines.
    Documentation: https://scryfall.com/docs/api
    """
    
    BASE_URL = "https://api.scryfall.com"
    
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self.session = session
        self.rate_limiter = RateLimiter()
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _make_request(self, endpoint: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
        """
        Make a rate-limited request to the Scryfall API
        
        Args:
            endpoint: API endpoint to call
            method: HTTP method to use
            **kwargs: Additional arguments to pass to the request
            
        Returns:
            Dict containing the API response
            
        Raises:
            ScryfallAPIError: If the API returns an error
        """
        await self.rate_limiter.acquire()
        
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                data = await response.json()
                
                if response.status == 429:  # Too Many Requests
                    retry_after = int(response.headers.get('Retry-After', 1))
                    await asyncio.sleep(retry_after)
                    return await self._make_request(endpoint, method, **kwargs)
                
                if not response.ok:
                    error_message = data.get('details', 'Unknown error occurred')
                    raise ScryfallAPIError(error_message, response.status)
                
                return data
                
        except aiohttp.ClientError as e:
            self.logger.error(f"Network error occurred: {str(e)}")
            raise ScryfallAPIError(f"Network error: {str(e)}")

    async def get_card(self, card_id: str) -> Dict[str, Any]:
        """
        Get a single card by its Scryfall ID
        
        Args:
            card_id: The Scryfall ID of the card
            
        Returns:
            Dict containing the card data
        """
        return await self._make_request(f"cards/{card_id}")

    async def search_cards(self, query: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Search for cards using Scryfall's search syntax.
        Automatically handles pagination.
        
        Args:
            query: The search query using Scryfall's syntax
            
        Yields:
            Dict containing card data for each matching card
        """
        params = {"q": query}
        has_more = True
        
        while has_more:
            data = await self._make_request("cards/search", params=params)
            
            for card in data.get("data", []):
                yield card
            
            has_more = data.get("has_more", False)
            if has_more:
                params["page"] = data.get("next_page")

    async def get_cards_by_set(self, set_code: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Get all cards from a specific set
        
        Args:
            set_code: The three to five-letter set code
            
        Yields:
            Dict containing card data for each card in the set
        """
        query = f"set:{set_code}"
        async for card in self.search_cards(query):
            yield card

    async def get_card_by_name(self, name: str, exact: bool = True) -> Dict[str, Any]:
        """
        Get a card by its name
        
        Args:
            name: The card name to search for
            exact: If True, only exact name matches are returned
            
        Returns:
            Dict containing the card data
        """
        endpoint = "cards/named"
        params = {
            "exact" if exact else "fuzzy": name
        }
        return await self._make_request(endpoint, params=params)
    
    async def get_standard_legal_cards(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Get all Standard-legal cards directly using the search endpoint.
        Automatically handles pagination.
        
        Yields:
            Dict[str, Any]: Card data for each Standard-legal card
        """
        params = {"q": "legal:standard"}
        has_more = True

        while has_more:
            try:
                # Make request with current params
                data = await self._make_request("cards/search", params=params)
                
                # Yield each card in the current page
                for card in data.get("data", []):
                    yield card
                
                # Check if there are more pages
                has_more = data.get("has_more", False)
                if has_more:
                    # Increment the page for the next request
                    params["page"] = params.get("page", 1) + 1
                    
            except Exception as e:
                self.logger.error(f"Error fetching Standard cards: {str(e)}")
                raise    