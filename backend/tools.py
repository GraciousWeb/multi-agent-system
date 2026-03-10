import os
from typing import List, Optional, Literal
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv(override=True)

tavily_api_key=os.environ.get("TAVILY_API_KEY")
if not tavily_api_key:
    raise RuntimeError("Missing TAVILY_API_KEY in environment variables.")

tavily_client = TavilyClient(api_key=tavily_api_key)


REGIONAL_DOMAINS = {
    "NG": ["cbn.gov.ng", "sec.gov.ng", "nairametrics.com", "techcabal.com"],
    "US": ["sec.gov", "federalreserve.gov", "techcrunch.com", "reuters.com"],
    "UK": ["fca.org.uk", "gov.uk", "finextra.com", "ft.com"],
    "EU": ["europa.eu", "esma.europa.eu", "sifted.eu", "eba.europa.eu", "ec.europa.eu"],
    "GLOBAL": ["bloomberg.com", "crunchbase.com", "worldbank.org", "reuters.com", "ft.com", "finextra.com", "fintechnews.org", "bis.org", "fsb.org", "techcabal.com"]
}

class FintechSearchInput(BaseModel):
    query: str = Field(description="The specific search query related to fintech events")
    market: Literal["US", "UK", "EU", "NG", "GLOBAL"] = Field(description="The target market")
    category: Literal["funding", "regulation", "general"] = Field(default="general")

class ExtractInput(BaseModel):
    urls: List[str] = Field(description="List of URLs to extract full content from")


@tool("fintech_search", args_schema=FintechSearchInput)
def fintech_search(query: str, market: str, category: str = "general"):
    """
    Search for fintech funding and regulatory news with regional precision.
    This will be used for scouting fresh, verified intel.
    """
    include_domains = REGIONAL_DOMAINS.get(market.upper(), REGIONAL_DOMAINS["GLOBAL"])
    search = TavilySearch(
        max_results=10,
        search_depth="advanced",
        include_domains=include_domains,
        topic="finance" if category != "general" else "general"
    )
    
    return search.invoke(query)

@tool("extract_full_content")
def extract_full_content(urls: List[str]):
    """
    Takes a list of URLs and returns the full cleaned markdown content.
    Used when a search snippet isn't enough to verify a funding round or a law.
    """

    extraction = tavily_client.extract(urls=urls)
    return [res.get("raw_content", "") for res in extraction.get("results", [])]

fintech_tools = [fintech_search, extract_full_content]