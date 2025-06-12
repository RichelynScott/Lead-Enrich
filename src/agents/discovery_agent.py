from crewai import Agent
from ..tools.hybrid_scraping_tools import HybridScrapeTool, HybridSearchTool

def create_discovery_agent() -> Agent:
    """Create the Discovery Agent responsible for extracting foundational company information."""
    
    scrape_tool = HybridScrapeTool()
    search_tool = HybridSearchTool()
    
    return Agent(
        role="Company Discovery Specialist",
        goal="Extract foundational company information from email domains with high accuracy and confidence",
        backstory="""You are an expert at discovering and extracting basic company information from email addresses. 
        You specialize in finding company names, websites, descriptions, and basic details through systematic research 
        and verification across multiple sources.""",
        tools=[scrape_tool, search_tool],
        verbose=True,
        allow_delegation=False
    )
