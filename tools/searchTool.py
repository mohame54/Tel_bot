from .base import BaseTool
import requests
from typing import List, Optional, Dict
from bs4 import BeautifulSoup
from . import (
    SEARCH_DOC,
    add_docstring
)


class SearchTool(BaseTool):
    def __init__(
        self,
        max_num_chars: Optional[int] = None,
        tool_name: Optional[str] = None,
        description="Searching",
    ):
        super(SearchTool, self).__init__(description)   
        self.max_num_chars = max_num_chars
        self.tool_name = "search_tool" if tool_name is None else tool_name

    def _scrape_link(self, url: str) -> str:
        
        headers = {
          "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        paragraphs = soup.find_all('p')
        content = " ".join([para.get_text() for para in paragraphs])
        if self.max_num_chars is not None:
            content = content[:self.max_num_chars]
        return content
    

    def _search(self, query: str) -> List[Dict[str, str]]:

        url = f"https://duckduckgo.com/html/?q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
            }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        results = []
        for result in soup.find_all("a", {"class": "result__url"}):
            title = result.get_text()
            link = result['href']
            if link.startswith('/'):
                link = 'https://duckduckgo.com' + link
            results.append({"title": title, "link": link})
            
        return results
    
    @add_docstring(SEARCH_DOC)
    def __call__(
        self,
        query:str,
        num_top_results: Optional[int] = 2,
        content_length: Optional[int] = 50,
    ) -> List[Dict[str, str]]:
        search_results = self._search(query=query)
        summarized_results: List[Dict[str, str]] = []
        search_results = search_results[:num_top_results]
        for result in search_results:  
            content = self._scrape_link(url=result["link"])
            # Filter the links which have the content length bigger than content_length
            if len(content.strip()) <= content_length:
                continue
            summarized_results.append(
                {
                    "title": result["title"],
                    "link": result["link"],
                    "content": content
                }
            )       
        return summarized_results
    