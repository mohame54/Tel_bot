import abc
from typing import Optional, List, Dict
import requests
from bs4 import BeautifulSoup


class BaseTool(abc.ABCMeta):
    def __init__(self, description:Optional[str]=""):
        self.description = description

    def __str__(self):
        desc = "Tool"
        if self.description != "":
            desc = desc + f"for:{self.description}"
        return desc
    
    def __repr__(self):
        desc = "Tool"
        if self.description != "":
            desc = desc + f"for:{self.description}"
        return desc
    
    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError
    

class SearchTool(BaseTool):
    def __init__(
        self,
        max_num_chars: Optional[int] = None,
        num_top_results: Optional[int] = 2,
        description="Searching",
    ):
        super(SearchTool, self).__init__(description)   
        self.max_num_chars = max_num_chars
        self.num_top_results = num_top_results

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
        for result in soup.find_all("a", {"class": "result__a"}):
            title = result.get_text()
            link = result['href']
            if link.startswith('/'):
                link = 'https://duckduckgo.com' + link
            results.append({"title": title, "link": link})
            
        return results
    
    def __call__(self, query:str) -> List[Dict[str, str]]:
        search_results = self._search(query=query)
        summarized_results = []
        search_results = search_results[:self.num_top_results]
        for result in search_results:  
            content = self._scrape_link(url=result["link"])
            summarized_results.append(
                {
                    "title": result["title"],
                    "link": result["link"],
                    "content": content
                }
            )       
        return summarized_results
    