from bs4 import BeautifulSoup
import requests
from itertools import islice

def fetch_url(query, limit = 3):
    """
    Searches a local SearXNG instance and returns a list of result dictionaries.

    Args:
        query (str): The search term.
        limit (int): The maximum number of results to return, default = 3
    Returns:
        list: A list of dictionaries, where each dictionary contains data for one search result
              (e.g., 'title', 'url', 'content'). Returns an empty list on failure.
    """
    search_url = "http://localhost:8080/search"
    params = {'q': query, 'format': 'json', 'language': 'en'}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(search_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get('results', [])[:(limit)]
    except requests.exceptions.RequestException as e:
        print(f"SearXNG Search Error: {e}")
        return []

def extract_content_from_url(url):
    """
    Fetches the HTML from a URL and extracts the readable text content,
    stripping away scripts, styles, and navigation elements.

    Args:
        url (str): The URL of the webpage to scrape.

    Returns:
        str: The extracted text content of the webpage.
             Returns an error message string if the request fails or times out.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
            element.extract()

        text = soup.get_text(separator=' ', strip=True)
        return text

    except requests.exceptions.Timeout:
        return "[Error: Request timed out]"
    except requests.exceptions.RequestException as e:
        return f"[Error: Failed to fetch ({e})]"
    except Exception as e:
        return f"[Error: Failed to parse ({e})]"
