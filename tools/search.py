from langchain_community.tools.tavily_search import TavilySearchResults

def tavily_search(max_results=3):
    return TavilySearchResults(max_results=max_results)