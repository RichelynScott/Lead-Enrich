# Lead Enricher - Python Implementation

A powerful multiagent lead enrichment system built with CrewAI that extracts comprehensive company information from email domains. This is a Python conversion of the original TypeScript fire-enrich project, now using CrewAI's robust multiagent framework with Crawl4AI web scraping.

## 🚀 Features

- **Multiagent Architecture**: 6 specialized AI agents working sequentially
- **Hybrid Web Scraping**: Crawl4AI as primary scraper with Firecrawl fallback for maximum reliability
- **CSV Processing**: Batch process existing data files and enrich missing information
- **Comprehensive Data Extraction**: Company profiles, funding, tech stack, metrics, and more
- **High Confidence Scoring**: Each extraction includes confidence metrics and source tracking
- **Flexible Field Configuration**: Customize what information to extract
- **Async/Sync Support**: Both asynchronous and synchronous operation modes
- **Built on CrewAI**: Leverages CrewAI's powerful multiagent framework

## 🤖 Agent Specialists

1. **Discovery Agent**: Extracts foundational company information (name, website, description)
2. **Company Profile Agent**: Gathers detailed business information (industry, size, leadership)
3. **Funding Agent**: Researches investment and funding history
4. **Tech Stack Agent**: Identifies technologies and development tools used
5. **Metrics Agent**: Collects business metrics and performance data
6. **General Agent**: Handles custom field extraction requirements

## 📋 Requirements

- Python 3.12+
- Firecrawl API key (for fallback scraping)
- OpenAI API key
- Crawl4AI (automatically installed)

## 🛠️ Installation

1. **Clone the repository**:
```bash
git clone https://github.com/RichelynScott/Lead-Enrich.git
cd Lead-Enrich
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env and add your API keys:
# FIRECRAWL_API_KEY=your_firecrawl_api_key_here  # Used as fallback
# OPENAI_API_KEY=your_openai_api_key_here
```

4. **Initialize Crawl4AI** (if not already done):
```bash
crawl4ai-setup
```

## 🎯 Quick Start

### Basic Usage

```python
import asyncio
from src.lead_enricher import LeadEnricher
from src.models.schemas import EmailContext, EnrichmentField, FieldType

async def main():
    # Initialize the enricher
    enricher = LeadEnricher()
    
    # Define what to extract
    email_context = EmailContext(
        email="contact@stripe.com",
        domain="stripe.com",
        fields=[
            EnrichmentField(
                name="company_name",
                type=FieldType.DISCOVERY,
                description="The official name of the company",
                required=True
            ),
            EnrichmentField(
                name="industry",
                type=FieldType.COMPANY_PROFILE,
                description="The industry sector",
                required=True
            )
        ]
    )
    
    # Run enrichment
    result = await enricher.enrich_email_async(email_context)
    
    print(f"Company: {result.discovery.company_name}")
    print(f"Industry: {result.company_profile.industry}")
    print(f"Confidence: {result.overall_confidence:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Synchronous Usage

```python
from src.lead_enricher import LeadEnricher
from src.models.schemas import EmailContext, EnrichmentField, FieldType

enricher = LeadEnricher()
email_context = EmailContext(
    email="hello@openai.com",
    domain="openai.com",
    fields=[
        EnrichmentField(
            name="company_basics",
            type=FieldType.DISCOVERY,
            description="Basic company information",
            required=True
        )
    ]
)

result = enricher.enrich_email(email_context)
print(f"Company: {result.discovery.company_name}")
```

### CSV Processing

```python
from src.lead_enricher import LeadEnricher

enricher = LeadEnricher()

# Process CSV file and enrich missing data
result = enricher.enrich_csv('leads.csv', 'enriched_leads.csv')

print(f"Processed {result.processed_rows} rows")
print(f"Successful enrichments: {result.successful_enrichments}")
```

### Async CSV Processing

```python
import asyncio
from src.lead_enricher import LeadEnricher

async def process_csv():
    enricher = LeadEnricher()
    result = await enricher.enrich_csv_async('leads.csv', 'enriched_leads.csv')
    return result

result = asyncio.run(process_csv())
```

## 📊 Field Types

The system supports various field types that determine which agent handles the extraction:

- `DISCOVERY`: Basic company information (name, website, description)
- `COMPANY_PROFILE`: Detailed business profile (industry, size, leadership)
- `FUNDING`: Investment and funding information
- `TECH_STACK`: Technology stack and development tools
- `METRICS`: Business metrics and performance data
- `GENERAL`: Custom fields handled by the general agent

## 🔧 Configuration

### Environment Variables

```bash
# Required
FIRECRAWL_API_KEY=your_firecrawl_api_key_here  # Used as fallback scraper
OPENAI_API_KEY=your_openai_api_key_here

# Optional
OPENAI_MODEL=gpt-4                    # Default: gpt-4
OPENAI_TEMPERATURE=0.1                # Default: 0.1
FIRECRAWL_TIMEOUT=30000              # Default: 30000ms
```

### CSV File Format

The system can process CSV files with the following columns (all optional except email):

```csv
email,company_name,website,industry,company_size,headquarters
contact@stripe.com,Stripe,https://stripe.com,Fintech,1000-5000,San Francisco
hello@openai.com,,,AI,,
```

The system will automatically detect missing fields and enrich only the data that's needed.

### Custom Field Configuration

```python
custom_fields = [
    EnrichmentField(
        name="sustainability_practices",
        type=FieldType.GENERAL,
        description="Company's environmental and sustainability initiatives",
        required=False
    ),
    EnrichmentField(
        name="recent_news",
        type=FieldType.GENERAL,
        description="Recent news and press releases",
        required=False
    )
]
```

## 📈 Output Structure

The enrichment result includes:

```python
{
    "email": "contact@company.com",
    "domain": "company.com",
    "discovery": {
        "company_name": "Company Name",
        "website": "https://company.com",
        "description": "Company description...",
        "confidence_score": 0.95,
        "source_urls": ["https://..."],
        "extraction_notes": "Additional context..."
    },
    "company_profile": { ... },
    "funding": { ... },
    "tech_stack": { ... },
    "metrics": { ... },
    "general": { ... },
    "overall_confidence": 0.87,
    "processing_time": 45.2,
    "errors": []
}
```

## 🧪 Testing

Run the test suite to verify everything is working:

```bash
# Test imports
python test_import.py

# Test basic functionality
python test_basic_imports.py

# Run individual email example
python example.py

# Run CSV processing example
python example_csv.py
```

## 🔄 Migration from TypeScript

This Python implementation maintains full compatibility with the original TypeScript version while leveraging CrewAI's advanced multiagent capabilities:

### Key Improvements
- **Hybrid Web Scraping**: Crawl4AI primary with Firecrawl fallback for maximum reliability
- **CSV Processing**: Batch process existing data files efficiently
- **Robust Framework**: Built on CrewAI's proven multiagent architecture
- **Better Error Handling**: Enhanced error tracking and recovery
- **Improved Scalability**: More efficient agent coordination
- **Enhanced Logging**: Better visibility into agent operations
- **Type Safety**: Full Pydantic model validation

### API Compatibility
The Python version maintains the same API structure as the TypeScript version, making migration straightforward.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project maintains the same license as the original fire-enrich project.

## 🙏 Acknowledgments

- Original fire-enrich project for the foundational architecture
- CrewAI team for the excellent multiagent framework
- Firecrawl for reliable web scraping capabilities

---

**Note**: This is a Python conversion of the original TypeScript implementation. For the TypeScript version, see the original project files in the `lib/` directory.
