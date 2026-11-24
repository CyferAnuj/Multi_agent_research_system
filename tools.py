import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from langchain.tools import tool
from dotenv import load_dotenv

# Load environment variables reliably
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
load_dotenv()  # Fallback to current working directory if different


def get_tavily_client() -> TavilyClient:
    """Retrieve TavilyClient with configured API key."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key or api_key.strip() == "your_tavily_api_key":
        raise ValueError("TAVILY_API_KEY is missing or invalid in your .env file.")
    return TavilyClient(api_key=api_key.strip())


@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic. Returns Titles, URLs and snippets."""
    try:
        client = get_tavily_client()
        results = client.search(query=query, max_results=5)
        raw_items = results.get("results", []) if isinstance(results, dict) else []

        if not raw_items:
            return f"No search results found for query: '{query}'."

        out = []
        for r in raw_items:
            title = r.get("title", "Untitled")
            url = r.get("url", "")
            content = r.get("content", "")[:300]
            out.append(f"Title: {title}\nURL: {url}\nSnippet: {content}\n")

        return "\n----\n".join(out)
    except Exception as e:
        return f"Error executing web search: {str(e)}"


@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        # Strip potential wrapping quotes or brackets from LLM
        clean_url = url.strip().strip("'\"<>[]()")
        if not clean_url.startswith(("http://", "https://")):
            return f"Invalid URL format: '{clean_url}'."

        resp = requests.get(
            clean_url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        # Decompose non-content elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        if not text:
            return f"No readable text content extracted from {clean_url}."

        return text[:3000]
    except Exception as e:
        return f"Could not scrape URL {url}: {str(e)}"
