#!/usr/bin/env python3
"""
Example usage of Lead Enricher with CSV processing functionality.
"""

import asyncio
from src.lead_enricher import LeadEnricher
from src.models.schemas import EnrichmentField, FieldType

def main():
    """Demonstrate CSV processing functionality."""
    print("🚀 Lead Enricher - CSV Processing Example")
    print("=" * 50)
    
    enricher = LeadEnricher()
    
    print("Creating sample CSV file...")
    import pandas as pd
    
    sample_data = [
        {
            'email': 'contact@stripe.com',
            'company_name': '',
            'website': '',
            'industry': '',
            'company_size': ''
        },
        {
            'email': 'hello@openai.com',
            'company_name': 'OpenAI',
            'website': 'https://openai.com',
            'industry': '',
            'company_size': ''
        },
        {
            'email': 'info@github.com',
            'company_name': '',
            'website': '',
            'industry': 'Technology',
            'company_size': ''
        }
    ]
    
    df = pd.DataFrame(sample_data)
    df.to_csv('sample_leads.csv', index=False)
    print("✓ Sample CSV created: sample_leads.csv")
    
    print("\nProcessing CSV file...")
    try:
        result = enricher.enrich_csv('sample_leads.csv', 'enriched_leads.csv')
        
        print(f"✓ Processing completed!")
        print(f"  Total rows: {result.total_rows}")
        print(f"  Processed rows: {result.processed_rows}")
        print(f"  Successful enrichments: {result.successful_enrichments}")
        print(f"  Failed enrichments: {result.failed_enrichments}")
        
        if result.errors:
            print(f"  Errors: {len(result.errors)}")
            for error in result.errors[:3]:
                print(f"    - {error}")
        
        print(f"✓ Enriched data saved to: enriched_leads.csv")
        
    except Exception as e:
        print(f"❌ Error processing CSV: {e}")

async def async_example():
    """Demonstrate async CSV processing."""
    print("\n🔄 Async CSV Processing Example")
    print("=" * 50)
    
    enricher = LeadEnricher()
    
    try:
        result = await enricher.enrich_csv_async('sample_leads.csv', 'enriched_leads_async.csv')
        
        print(f"✓ Async processing completed!")
        print(f"  Total rows: {result.total_rows}")
        print(f"  Processed rows: {result.processed_rows}")
        print(f"  Successful enrichments: {result.successful_enrichments}")
        print(f"  Failed enrichments: {result.failed_enrichments}")
        
        print(f"✓ Async enriched data saved to: enriched_leads_async.csv")
        
    except Exception as e:
        print(f"❌ Error in async processing: {e}")

if __name__ == "__main__":
    main()
    asyncio.run(async_example())
