#!/usr/bin/env python3
"""
Test CSV processing functionality without requiring API keys.
"""

import os
import pandas as pd
from src.models.schemas import CSVRow, EnrichmentField, FieldType
from src.lead_enricher import LeadEnricher

def test_csv_row_creation():
    """Test CSVRow model creation."""
    print("Testing CSVRow creation...")
    
    try:
        csv_row = CSVRow(
            email="contact@stripe.com",
            company_name="Stripe",
            website="https://stripe.com",
            industry="Fintech",
            company_size="1000-5000",
            headquarters="San Francisco",
            raw_data={"extra_field": "extra_value"}
        )
        
        assert csv_row.email == "contact@stripe.com"
        assert csv_row.company_name == "Stripe"
        assert csv_row.raw_data["extra_field"] == "extra_value"
        
        print("✓ CSVRow creation successful")
        return True
        
    except Exception as e:
        print(f"❌ CSVRow creation failed: {e}")
        return False

def test_missing_field_detection():
    """Test missing field detection logic."""
    print("Testing missing field detection...")
    
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["FIRECRAWL_API_KEY"] = "test-key"
    
    try:
        enricher = LeadEnricher()
        
        csv_row1 = CSVRow(
            email="contact@example.com",
            company_name="",
            website="",
            industry="Tech",
            company_size="100-500"
        )
        
        missing_fields1 = enricher._detect_missing_fields(csv_row1)
        discovery_fields = [f for f in missing_fields1 if f.type == FieldType.DISCOVERY]
        assert len(discovery_fields) > 0, "Should detect missing discovery fields"
        
        csv_row2 = CSVRow(
            email="hello@stripe.com",
            company_name="Stripe",
            website="https://stripe.com",
            industry="",
            company_size=""
        )
        
        missing_fields2 = enricher._detect_missing_fields(csv_row2)
        profile_fields = [f for f in missing_fields2 if f.type == FieldType.COMPANY_PROFILE]
        assert len(profile_fields) > 0, "Should detect missing profile fields"
        
        print("✓ Missing field detection working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Missing field detection failed: {e}")
        return False

def test_csv_file_creation():
    """Test creating and reading CSV files."""
    print("Testing CSV file operations...")
    
    try:
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
            }
        ]
        
        df = pd.DataFrame(sample_data)
        test_csv_path = 'test_leads.csv'
        df.to_csv(test_csv_path, index=False)
        
        df_read = pd.read_csv(test_csv_path)
        assert len(df_read) == 2, "Should have 2 rows"
        assert 'email' in df_read.columns, "Should have email column"
        
        os.remove(test_csv_path)
        
        print("✓ CSV file operations successful")
        return True
        
    except Exception as e:
        print(f"❌ CSV file operations failed: {e}")
        return False

def main():
    """Run all CSV processing tests."""
    print("🧪 Testing CSV Processing Functionality")
    print("=" * 50)
    
    tests = [
        test_csv_row_creation,
        test_missing_field_detection,
        test_csv_file_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All CSV processing tests passed!")
        print("CSV functionality is ready for use with API keys.")
        return True
    else:
        print("❌ Some tests failed. Check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
