import httpx
from typing import Dict, Any, Optional

class HttpClient:
    """Utility class to handle HTTP requests with retries and error handling"""
    
    def __init__(self, base_url: str = "", headers: Optional[Dict[str, str]] = None, timeout: float = 30.0):
        self.base_url = base_url
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        }
        self.timeout = timeout
    
    async def get_async(self, url: str, params: Optional[Dict[str, Any]] = None, max_retries: int = 3) -> httpx.Response:
        """
        Perform an async GET request with retries
        
        Args:
            url: The URL to request (will be joined with base_url if relative)
            params: Query parameters to include
            max_retries: Maximum number of retry attempts
            
        Returns:
            httpx.Response object
        """
        full_url = url if url.startswith("http") else f"{self.base_url}{url}"
        retry_count = 0
        
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True) as client:
            while retry_count < max_retries:
                try:
                    response = await client.get(full_url, params=params)
                    
                    # Return immediately if successful
                    if response.status_code == 200:
                        return response
                    
                    # If not a 429 (rate limit) or 5xx (server error), don't retry
                    if response.status_code != 429 and not (500 <= response.status_code < 600):
                        return response
                    
                    # Otherwise increment retry and continue
                    retry_count += 1
                    
                except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout) as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise e
            
            # If we reach here, we've exhausted retries
            raise Exception(f"Failed to get response after {max_retries} retries")
