#!/usr/bin/env python3
"""
FastAPI server to expose Python backend functionality to Next.js frontend.
"""

import asyncio
import json
import os
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .lead_enricher import LeadEnricher
from .models.schemas import EnrichmentField, FieldType, EnrichmentResult


class EnrichmentRequest(BaseModel):
    email: str
    fields: List[Dict[str, Any]]  # Compatible with frontend field format


class CSVEnrichmentRequest(BaseModel):
    csv_data: List[Dict[str, Any]]
    fields: List[Dict[str, Any]]
    email_column: str
    enhanced_mode: bool = False


class EnrichmentStatus(BaseModel):
    status: str
    progress: float
    current_row: Optional[int] = None
    total_rows: Optional[int] = None
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


# Global enricher instance
enricher: Optional[LeadEnricher] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the enricher on startup."""
    global enricher
    try:
        enricher = LeadEnricher()
        print("✅ Python backend initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Python backend: {e}")
        raise
    yield


app = FastAPI(
    title="Fire Enrich Python Backend",
    description="Advanced multi-agent enrichment system using CrewAI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def convert_frontend_fields_to_enrichment_fields(fields: List[Dict[str, Any]]) -> List[EnrichmentField]:
    """Convert frontend field format to EnrichmentField objects."""
    enrichment_fields = []
    
    for field in fields:
        field_name = field.get('name', '').lower()
        
        # Map field names to types based on content
        if any(keyword in field_name for keyword in ['fund', 'invest', 'capital', 'series']):
            field_type = FieldType.FUNDING
        elif any(keyword in field_name for keyword in ['tech', 'stack', 'language', 'framework']):
            field_type = FieldType.TECH_STACK
        elif any(keyword in field_name for keyword in ['revenue', 'employee', 'size', 'metric']):
            field_type = FieldType.METRICS
        elif any(keyword in field_name for keyword in ['industry', 'headquarter', 'location']):
            field_type = FieldType.COMPANY_PROFILE
        else:
            field_type = FieldType.GENERAL
            
        enrichment_fields.append(
            EnrichmentField(
                name=field.get('name', ''),
                type=field_type,
                description=field.get('description', ''),
                required=field.get('required', False)
            )
        )
    
    return enrichment_fields


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "backend": "python-crewai",
        "version": "1.0.0",
        "enricher_ready": enricher is not None
    }


@app.post("/enrich/single")
async def enrich_single_email(request: EnrichmentRequest) -> Dict[str, Any]:
    """Enrich a single email using the Python backend."""
    if not enricher:
        raise HTTPException(status_code=500, detail="Enricher not initialized")
    
    try:
        fields = convert_frontend_fields_to_enrichment_fields(request.fields)
        result = enricher.enrich_email_sync(request.email, fields)
        
        # Convert to frontend-compatible format
        return {
            "email": result.email,
            "domain": result.domain,
            "data": {
                **(result.discovery.dict() if result.discovery else {}),
                **(result.company_profile.dict() if result.company_profile else {}),
                **(result.funding.dict() if result.funding else {}),
                **(result.tech_stack.dict() if result.tech_stack else {}),
                **(result.metrics.dict() if result.metrics else {}),
                **(result.general.extracted_data if result.general else {}),
            },
            "confidence_score": result.overall_confidence,
            "processing_time": result.processing_time,
            "errors": result.errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enrichment failed: {str(e)}")


@app.post("/enrich/csv")
async def enrich_csv_data(request: CSVEnrichmentRequest, background_tasks: BackgroundTasks):
    """Enrich CSV data using the Python backend with streaming response."""
    if not enricher:
        raise HTTPException(status_code=500, detail="Enricher not initialized")
    
    async def generate_enrichment_stream():
        """Generate SSE stream for CSV enrichment."""
        try:
            fields = convert_frontend_fields_to_enrichment_fields(request.fields)
            total_rows = len(request.csv_data)
            
            # Send initial status
            yield f"data: {json.dumps({'type': 'status', 'status': 'starting', 'total_rows': total_rows})}\n\n"
            
            for i, row in enumerate(request.csv_data):
                email = row.get(request.email_column)
                if not email:
                    continue
                
                try:
                    # Send progress update
                    yield f"data: {json.dumps({'type': 'progress', 'current_row': i + 1, 'total_rows': total_rows})}\n\n"
                    
                    if request.enhanced_mode:
                        # Use enhanced CSV processing for lead data
                        # This would require implementing a streaming version of process_lead_csv
                        result = enricher.enrich_email_sync(email, fields)
                    else:
                        # Use basic enrichment
                        result = enricher.enrich_email_sync(email, fields)
                    
                    # Convert result to frontend format
                    enriched_data = {
                        "email": result.email,
                        "domain": result.domain,
                        **{field.name: getattr(result.discovery, field.name, None) if result.discovery else None for field in fields if result.discovery},
                        **{field.name: getattr(result.company_profile, field.name, None) if result.company_profile else None for field in fields if result.company_profile},
                        **{field.name: getattr(result.funding, field.name, None) if result.funding else None for field in fields if result.funding},
                        **{field.name: getattr(result.tech_stack, field.name, None) if result.tech_stack else None for field in fields if result.tech_stack},
                        **{field.name: getattr(result.metrics, field.name, None) if result.metrics else None for field in fields if result.metrics},
                        **{field.name: result.general.extracted_data.get(field.name) if result.general else None for field in fields},
                        "confidence_score": result.overall_confidence,
                        "sources": []  # Combine all source URLs
                    }
                    
                    # Add all source URLs
                    all_sources = []
                    for agent_result in [result.discovery, result.company_profile, result.funding, result.tech_stack, result.metrics, result.general]:
                        if agent_result and hasattr(agent_result, 'source_urls'):
                            all_sources.extend(agent_result.source_urls)
                    enriched_data["sources"] = list(set(all_sources))
                    
                    # Send enriched row result
                    yield f"data: {json.dumps({'type': 'result', 'row_index': i, 'data': enriched_data})}\n\n"
                    
                except Exception as e:
                    # Send error for this row
                    yield f"data: {json.dumps({'type': 'error', 'row_index': i, 'error': str(e)})}\n\n"
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.1)
            
            # Send completion
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_enrichment_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )


@app.post("/enrich/leads")
async def enrich_leads_csv(csv_file_path: str, output_path: str):
    """Process lead CSV using enhanced processing mode."""
    if not enricher:
        raise HTTPException(status_code=500, detail="Enricher not initialized")
    
    try:
        result = enricher.process_lead_csv(csv_file_path, output_path)
        return {
            "success": True,
            "output_path": output_path,
            "stats": {
                "decision_makers_found": result.decision_makers_found,
                "company_descriptions_created": result.company_descriptions_created,
                "emails_researched": result.emails_researched,
                "processing_time": result.processing_time
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lead processing failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        "src.api_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )