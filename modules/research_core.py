import asyncio
from typing import List, Dict
from .api_clients import OpenRouterClient, SerpAPIClient, JinaClient

class ResearchCore:
    def __init__(self):
        self.llm = OpenRouterClient()
        self.search = SerpAPIClient()
        self.jina = JinaClient()
        
    async def get_initial_queries(self, session, user_query: str) -> List[str]:
        system_prompt = "Generate 3-5 precise Google search queries to research this topic."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        result = await self.llm.chat_completion(session, messages)
        return [line.strip("- ") for line in result.split("\n") if line.strip()]

    async def get_new_search_queries(self, session, user_query: str, existing_queries: List[str], contexts: List[str]) -> List[str]:
        system_prompt = """Analyze if we need additional searches. Respond with either:
        - <done> if no more searches needed
        - 2-3 new search queries in bullet points"""
        
        context_str = "\n".join(contexts[-3:])
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Original query: {user_query}\nExisting searches: {existing_queries}\nRecent contexts:\n{context_str}"}
        ]
        result = await self.llm.chat_completion(session, messages)
        return [] if "<done>" in result else [line.strip("- ") for line in result.split("\n") if line.strip()]

    async def analyze_content(self, session, url: str, content: str, query: str) -> str:
        system_prompt = f"Extract relevant insights about {query} from this content. Focus on key facts and data points."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Content from {url}:\n\n{content[:5000]}"}
        ]
        return await self.llm.chat_completion(session, messages)

    async def generate_report(self, session, user_query: str, contexts: List[str]) -> str:
        system_prompt = "Synthesize a comprehensive report with sections and data points."
        context_str = "\n\n".join(contexts)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Research query: {user_query}\nCollected data:\n{context_str}"}
        ]
        return await self.llm.chat_completion(session, messages)

    async def research_loop(self, session, user_query: str) -> str:
        all_queries = await self.get_initial_queries(session, user_query)
        contexts = []
        
        async def process_query(query: str):
            urls = await self.search.search(session, query)
            for url in urls[:3]:
                content = await self.jina.fetch_content(session, url)
                if content:
                    analysis = await self.analyze_content(session, url, content, query)
                    contexts.append(f"## {query}\n**Source:** {url}\n{analysis}")

        iteration = 1
        while iteration <= 3:
            await asyncio.gather(*[process_query(q) for q in all_queries])
            
            new_queries = await self.get_new_search_queries(
                session, user_query, all_queries, contexts
            )
            if not new_queries:
                break
                
            all_queries.extend(new_queries)
            iteration += 1

        return await self.generate_report(session, user_query, contexts)
