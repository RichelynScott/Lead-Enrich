import os
import time
from typing import List, Optional
from dotenv import load_dotenv
from crewai import Crew, Process

from .models.schemas import (
    EmailContext, EnrichmentField, EnrichmentResult, FieldType,
    DiscoveryResult, CompanyProfileResult, FundingResult, 
    TechStackResult, MetricsResult, GeneralResult,
    CSVRow, CSVProcessingResult
)
from .agents.discovery_agent import create_discovery_agent
from .agents.company_profile_agent import create_company_profile_agent
from .agents.funding_agent import create_funding_agent
from .agents.tech_stack_agent import create_tech_stack_agent
from .agents.metrics_agent import create_metrics_agent
from .agents.general_agent import create_general_agent
from .tasks.enrichment_tasks import (
    create_discovery_task, create_company_profile_task, create_funding_task,
    create_tech_stack_task, create_metrics_task, create_general_task
)

load_dotenv()

class LeadEnricher:
    """Main class for enriching email data using CrewAI multiagent framework."""
    
    def __init__(self):
        """Initialize the Lead Enricher with required API keys."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        if not self.firecrawl_api_key:
            raise ValueError("FIRECRAWL_API_KEY environment variable is required")
    
    def _extract_domain_from_email(self, email: str) -> str:
        """Extract domain from email address."""
        return email.split('@')[1].lower()
    
    def _categorize_fields(self, fields: List[EnrichmentField]) -> dict:
        """Categorize fields by agent type."""
        categorized = {
            FieldType.DISCOVERY: [],
            FieldType.COMPANY_PROFILE: [],
            FieldType.FUNDING: [],
            FieldType.TECH_STACK: [],
            FieldType.METRICS: [],
            FieldType.GENERAL: []
        }
        
        for field in fields:
            categorized[field.type].append(field)
        
        return categorized
    
    def _build_context_string(self, results: dict) -> str:
        """Build context string from previous agent results."""
        context_parts = []
        
        if results.get('discovery'):
            discovery = results['discovery']
            context_parts.append(f"Company: {discovery.company_name}")
            if discovery.website:
                context_parts.append(f"Website: {discovery.website}")
            if discovery.description:
                context_parts.append(f"Description: {discovery.description}")
        
        if results.get('company_profile'):
            profile = results['company_profile']
            if profile.industry:
                context_parts.append(f"Industry: {profile.industry}")
            if profile.company_size:
                context_parts.append(f"Size: {profile.company_size}")
        
        return "\n".join(context_parts)
    
    async def enrich_email(self, email: str, fields: List[EnrichmentField]) -> EnrichmentResult:
        """
        Enrich an email with company data using the specified fields.
        
        Args:
            email: Email address to enrich
            fields: List of fields to extract
            
        Returns:
            EnrichmentResult with extracted data
        """
        start_time = time.time()
        domain = self._extract_domain_from_email(email)
        
        email_context = EmailContext(
            email=email,
            domain=domain,
            fields=fields
        )
        
        categorized_fields = self._categorize_fields(fields)
        results = {}
        errors = []
        
        try:
            if categorized_fields[FieldType.DISCOVERY] or any(categorized_fields.values()):
                discovery_agent = create_discovery_agent()
                discovery_task = create_discovery_task(email_context)
                
                discovery_crew = Crew(
                    agents=[discovery_agent],
                    tasks=[discovery_task],
                    process=Process.sequential,
                    verbose=True
                )
                
                discovery_result = discovery_crew.kickoff()
                results['discovery'] = discovery_result
            
            context = self._build_context_string(results)
            
            if categorized_fields[FieldType.COMPANY_PROFILE]:
                profile_agent = create_company_profile_agent()
                profile_task = create_company_profile_task(email_context, context)
                
                profile_crew = Crew(
                    agents=[profile_agent],
                    tasks=[profile_task],
                    process=Process.sequential,
                    verbose=True
                )
                
                profile_result = profile_crew.kickoff()
                results['company_profile'] = profile_result
                context = self._build_context_string(results)
            
            if categorized_fields[FieldType.FUNDING]:
                funding_agent = create_funding_agent()
                funding_task = create_funding_task(email_context, context)
                
                funding_crew = Crew(
                    agents=[funding_agent],
                    tasks=[funding_task],
                    process=Process.sequential,
                    verbose=True
                )
                
                funding_result = funding_crew.kickoff()
                results['funding'] = funding_result
                context = self._build_context_string(results)
            
            if categorized_fields[FieldType.TECH_STACK]:
                tech_agent = create_tech_stack_agent()
                tech_task = create_tech_stack_task(email_context, context)
                
                tech_crew = Crew(
                    agents=[tech_agent],
                    tasks=[tech_task],
                    process=Process.sequential,
                    verbose=True
                )
                
                tech_result = tech_crew.kickoff()
                results['tech_stack'] = tech_result
                context = self._build_context_string(results)
            
            if categorized_fields[FieldType.METRICS]:
                metrics_agent = create_metrics_agent()
                metrics_task = create_metrics_task(email_context, context)
                
                metrics_crew = Crew(
                    agents=[metrics_agent],
                    tasks=[metrics_task],
                    process=Process.sequential,
                    verbose=True
                )
                
                metrics_result = metrics_crew.kickoff()
                results['metrics'] = metrics_result
                context = self._build_context_string(results)
            
            if categorized_fields[FieldType.GENERAL]:
                general_agent = create_general_agent()
                general_task = create_general_task(email_context, categorized_fields[FieldType.GENERAL], context)
                
                general_crew = Crew(
                    agents=[general_agent],
                    tasks=[general_task],
                    process=Process.sequential,
                    verbose=True
                )
                
                general_result = general_crew.kickoff()
                results['general'] = general_result
        
        except Exception as e:
            errors.append(f"Error during enrichment: {str(e)}")
        
        confidence_scores = []
        for result in results.values():
            if hasattr(result, 'confidence_score'):
                confidence_scores.append(result.confidence_score)
        
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        processing_time = time.time() - start_time
        
        return EnrichmentResult(
            email=email,
            domain=domain,
            discovery=results.get('discovery'),
            company_profile=results.get('company_profile'),
            funding=results.get('funding'),
            tech_stack=results.get('tech_stack'),
            metrics=results.get('metrics'),
            general=results.get('general'),
            overall_confidence=overall_confidence,
            processing_time=processing_time,
            errors=errors
        )
    
    def enrich_email_sync(self, email: str, fields: List[EnrichmentField]) -> EnrichmentResult:
        """
        Synchronous version of enrich_email for easier usage.
        
        Args:
            email: Email address to enrich
            fields: List of fields to extract
            
        Returns:
            EnrichmentResult with extracted data
        """
        import asyncio
        return asyncio.run(self.enrich_email(email, fields))
    
    def _detect_missing_fields(self, csv_row: CSVRow) -> List[EnrichmentField]:
        """Detect which fields are missing from CSV row and need enrichment."""
        missing_fields = []
        
        if not csv_row.company_name or not csv_row.website:
            missing_fields.append(EnrichmentField(
                name="company_basics",
                type=FieldType.DISCOVERY,
                description="Basic company information including name and website",
                required=True
            ))
        
        if not csv_row.industry or not csv_row.company_size:
            missing_fields.append(EnrichmentField(
                name="company_profile",
                type=FieldType.COMPANY_PROFILE,
                description="Company profile including industry and size",
                required=True
            ))
        
        missing_fields.append(EnrichmentField(
            name="funding_info",
            type=FieldType.FUNDING,
            description="Company funding and investment information",
            required=False
        ))
        
        missing_fields.append(EnrichmentField(
            name="tech_stack",
            type=FieldType.TECH_STACK,
            description="Technology stack and development tools",
            required=False
        ))
        
        missing_fields.append(EnrichmentField(
            name="business_metrics",
            type=FieldType.METRICS,
            description="Business metrics and performance data",
            required=False
        ))
        
        return missing_fields
    
    def _save_csv_results(self, results: List[EnrichmentResult], output_path: str):
        """Save enrichment results to CSV file."""
        import pandas as pd
        
        rows = []
        for result in results:
            row = {
                'email': result.email,
                'domain': result.domain,
                'overall_confidence': result.overall_confidence,
                'processing_time': result.processing_time,
                'errors': '; '.join(result.errors) if result.errors else ''
            }
            
            if result.discovery:
                row.update({
                    'company_name': result.discovery.company_name,
                    'website': result.discovery.website,
                    'description': result.discovery.description,
                    'discovery_confidence': result.discovery.confidence_score
                })
            
            if result.company_profile:
                row.update({
                    'industry': result.company_profile.industry,
                    'company_size': result.company_profile.company_size,
                    'headquarters': result.company_profile.headquarters,
                    'founded_year': result.company_profile.founded_year,
                    'profile_confidence': result.company_profile.confidence_score
                })
            
            if result.funding:
                row.update({
                    'total_funding': result.funding.total_funding,
                    'last_funding_round': result.funding.last_funding_round,
                    'last_funding_amount': result.funding.last_funding_amount,
                    'funding_confidence': result.funding.confidence_score
                })
            
            if result.tech_stack:
                row.update({
                    'technologies': '; '.join(result.tech_stack.technologies),
                    'programming_languages': '; '.join(result.tech_stack.programming_languages),
                    'tech_confidence': result.tech_stack.confidence_score
                })
            
            if result.metrics:
                row.update({
                    'revenue': result.metrics.revenue,
                    'employee_count': result.metrics.employee_count,
                    'growth_rate': result.metrics.growth_rate,
                    'metrics_confidence': result.metrics.confidence_score
                })
            
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
    
    def enrich_csv(self, csv_file_path: str, output_path: Optional[str] = None) -> CSVProcessingResult:
        """Process CSV file and enrich missing company data."""
        import pandas as pd
        
        try:
            df = pd.read_csv(csv_file_path)
            results = []
            errors = []
            successful_count = 0
            
            for index, row in df.iterrows():
                try:
                    csv_row = CSVRow(
                        email=row.get('email', ''),
                        company_name=row.get('company_name'),
                        website=row.get('website'),
                        industry=row.get('industry'),
                        company_size=row.get('company_size'),
                        headquarters=row.get('headquarters'),
                        raw_data=row.to_dict()
                    )
                    
                    if not csv_row.email:
                        errors.append(f"Row {index}: Missing email address")
                        continue
                    
                    missing_fields = self._detect_missing_fields(csv_row)
                    if missing_fields:
                        result = self.enrich_email_sync(csv_row.email, missing_fields)
                        results.append(result)
                        if not result.errors:
                            successful_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {index}: {str(e)}")
            
            if output_path:
                self._save_csv_results(results, output_path)
            
            return CSVProcessingResult(
                total_rows=len(df),
                processed_rows=len(results),
                successful_enrichments=successful_count,
                failed_enrichments=len(results) - successful_count,
                results=results,
                errors=errors
            )
            
        except Exception as e:
            raise ValueError(f"Error processing CSV file: {str(e)}")
    
    async def enrich_csv_async(self, csv_file_path: str, output_path: Optional[str] = None) -> CSVProcessingResult:
        """Asynchronous version of CSV processing."""
        import pandas as pd
        
        try:
            df = pd.read_csv(csv_file_path)
            results = []
            errors = []
            successful_count = 0
            
            for index, row in df.iterrows():
                try:
                    csv_row = CSVRow(
                        email=row.get('email', ''),
                        company_name=row.get('company_name'),
                        website=row.get('website'),
                        industry=row.get('industry'),
                        company_size=row.get('company_size'),
                        headquarters=row.get('headquarters'),
                        raw_data=row.to_dict()
                    )
                    
                    if not csv_row.email:
                        errors.append(f"Row {index}: Missing email address")
                        continue
                    
                    missing_fields = self._detect_missing_fields(csv_row)
                    if missing_fields:
                        result = await self.enrich_email(csv_row.email, missing_fields)
                        results.append(result)
                        if not result.errors:
                            successful_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {index}: {str(e)}")
            
            if output_path:
                self._save_csv_results(results, output_path)
            
            return CSVProcessingResult(
                total_rows=len(df),
                processed_rows=len(results),
                successful_enrichments=successful_count,
                failed_enrichments=len(results) - successful_count,
                results=results,
                errors=errors
            )
            
        except Exception as e:
            raise ValueError(f"Error processing CSV file: {str(e)}")
