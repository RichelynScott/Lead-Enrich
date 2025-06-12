#!/usr/bin/env python3
"""
Test Crawl4AI integration and fallback functionality.
"""

import os
import asyncio
from src.tools.hybrid_scraping_tools import HybridScrapeTool, HybridSearchTool

def test_hybrid_scrape_tool():
    """Test the hybrid scraping tool."""
    print("Testing HybridScrapeTool...")
    
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["FIRECRAWL_API_KEY"] = "test-key"
    
    try:
        tool = HybridScrapeTool()
        print("✓ HybridScrapeTool initialized successfully")
        
        result = tool._run("https://example.com")
        if result and len(result) > 0:
            print("✓ Scraping test successful")
            print(f"  Result length: {len(result)} characters")
            return True
        else:
            print("❌ Scraping returned empty result")
            return False
            
    except Exception as e:
        print(f"❌ HybridScrapeTool test failed: {e}")
        return False

def test_hybrid_search_tool():
    """Test the hybrid search tool."""
    print("Testing HybridSearchTool...")
    
    try:
        tool = HybridSearchTool()
        print("✓ HybridSearchTool initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ HybridSearchTool test failed: {e}")
        return False

async def test_crawl4ai_direct():
    """Test Crawl4AI directly."""
    print("Testing Crawl4AI directly...")
    
    try:
        from crawl4ai import AsyncWebCrawler
        
        async with AsyncWebCrawler(verbose=False) as crawler:
            result = await crawler.arun(url="https://example.com")
            if result and result.markdown:
                print("✓ Direct Crawl4AI test successful")
                print(f"  Markdown length: {len(result.markdown)} characters")
                return True
            else:
                print("❌ Direct Crawl4AI test returned empty result")
                return False
                
    except Exception as e:
        print(f"❌ Direct Crawl4AI test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🧪 Testing Crawl4AI Integration")
    print("=" * 50)
    
    tests = [
        test_hybrid_scrape_tool,
        test_hybrid_search_tool,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("Testing direct Crawl4AI...")
    if asyncio.run(test_crawl4ai_direct()):
        passed += 1
    total += 1
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All Crawl4AI integration tests passed!")
        return True
    else:
        print("❌ Some tests failed. Check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
