import requests
import time
from typing import Optional

def check_url_endpoint(url: str, timeout: int = 6) -> Optional[dict]:
    """
    Checks a URL endpoint for HTTP response, latency, and textual content.

    Args:
        url: The URL to check.
        timeout: The timeout in seconds for the request. Defaults to 8 seconds.

    Returns:
        A dictionary containing the HTTP response code, latency in seconds,
        and the textual content of the page.
        Returns None if an error occurs.
    """
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        end_time = time.time()
        latency = end_time - start_time

        # Check if the response is text-based (e.g., text/html, text/plain)
        content_type = response.headers.get('Content-Type', '').lower()
        if 'text' in content_type:
            page_content = response.text
        else:
            page_content = "Content is not text-based."

        return {
            "http_response": response.status_code,
            "latency": latency,
            "page": page_content,
        }
    except requests.exceptions.RequestException as e:
        print(f"Error checking URL {url}: {e}")
        return None

