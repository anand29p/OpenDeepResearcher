import os
import aiohttp
from typing import Optional

class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"

    async def chat_completion(self, session, messages: list, model: str = "anthropic/claude-3.5-haiku"):
        async with session.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Referer": "https://github.com/OpenDeepResearcher",
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": 0.7
            }
        ) as response:
            response.raise_for_status()
            result = await response.json()
            if "error" in result:
                raise Exception(f"API Error: {result['error']['message']}")
            return result["choices"][0]["message"]["content"]

class SerpAPIClient:
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_API_KEY")

    async def search(self, session, query: str, num_results: int = 5) -> list:
        async with session.get(
            "https://serpapi.com/search",
            params={
                "q": query,
                "api_key": self.api_key,
                "num": num_results
            }
        ) as response:
            results = await response.json()
            return [r.get("link") for r in results.get("organic_results", []) if r.get("link")]

class JinaClient:
    def __init__(self):
        self.api_key = os.getenv("JINA_API_KEY")
        self.base_url = "https://r.jina.ai"

    async def fetch_content(self, session, url: str) -> Optional[str]:
        try:
            async with session.get(
                f"{self.base_url}/{url}",
                headers={"Authorization": f"Bearer {self.api_key}"}
            ) as response:
                return await response.text()
        except:
            return None
