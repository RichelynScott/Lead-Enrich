#!/usr/bin/env python3
"""
Simplified FastAPI server for Fire Enrich Python backend (without CrewAI dependency conflicts).
This version provides the basic integration without the full CrewAI multiagent system.
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
import openai
from dotenv import load_dotenv

load_dotenv()

class EnrichmentRequest(BaseModel):
    email: str
    fields: List[Dict[str, Any]]


class CSVEnrichmentRequest(BaseModel):
    csv_data: List[Dict[str, Any]]
    fields: List[Dict[str, Any]]
    email_column: str
    enhanced_mode: bool = False


class SimpleEnricher:
    """Simplified enricher without CrewAI dependencies."""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        if not self.firecrawl_api_key:
            raise ValueError("FIRECRAWL_API_KEY environment variable is required")
        
        try:
            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        except TypeError:
            # Fallback for older OpenAI versions
            self.openai_client = openai.OpenAI(
                api_key=self.openai_api_key,
                timeout=30.0
            )
    
    def enrich_email_simple(self, email: str, fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simple email enrichment using OpenAI directly."""
        domain = email.split('@')[1].lower()
        
        # Create field descriptions
        field_descriptions = []
        for field in fields:
            field_descriptions.append(f"- {field.get('name', '')}: {field.get('description', '')}")
        
        prompt = f"""
        Extract information about the company with domain: {domain}
        
        Please provide the following information if available:
        {chr(10).join(field_descriptions)}
        
        Return the response as a JSON object with the field names as keys.
        If information is not available, use null for that field.
        Include a confidence_score (0-1) for each field.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a business intelligence assistant that extracts company information. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                result_data = json.loads(result_text)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                result_data = {field.get('name', f'field_{i}'): None for i, field in enumerate(fields)}
            
            return {
                "email": email,
                "domain": domain,
                "data": result_data,
                "confidence_score": 0.7,  # Default confidence
                "processing_time": 2.0,   # Placeholder
                "errors": [],
                "source": "simple_openai_enrichment"
            }
            
        except Exception as e:
            return {
                "email": email,
                "domain": domain,
                "data": {field.get('name', f'field_{i}'): None for i, field in enumerate(fields)},
                "confidence_score": 0.0,
                "processing_time": 0.0,
                "errors": [str(e)],
                "source": "error"
            }


# Global enricher instance
enricher: Optional[SimpleEnricher] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the enricher on startup."""
    global enricher
    try:
        enricher = SimpleEnricher()
        print("✅ Simple Python backend initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Python backend: {e}")
        raise
    yield


app = FastAPI(
    title="Fire Enrich Simple Python Backend",
    description="Simplified enrichment system without CrewAI dependencies",
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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "backend": "python-simple",
        "version": "1.0.0",
        "enricher_ready": enricher is not None,
        "message": "Simplified backend without CrewAI (to avoid dependency conflicts)"
    }


@app.post("/enrich/single")
async def enrich_single_email(request: EnrichmentRequest) -> Dict[str, Any]:
    """Enrich a single email using the simple Python backend."""
    if not enricher:
        raise HTTPException(status_code=500, detail="Enricher not initialized")
    
    try:
        result = enricher.enrich_email_simple(request.email, request.fields)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enrichment failed: {str(e)}")


@app.post("/enrich/csv")
async def enrich_csv_data(request: CSVEnrichmentRequest, background_tasks: BackgroundTasks):
    """Enrich CSV data using the simple Python backend with streaming response."""
    if not enricher:
        raise HTTPException(status_code=500, detail="Enricher not initialized")
    
    async def generate_enrichment_stream():
        """Generate SSE stream for CSV enrichment."""
        try:
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
                    
                    # Process this row
                    result = enricher.enrich_email_simple(email, request.fields)
                    
                    # Convert result to frontend format
                    enriched_data = {
                        "email": result["email"],
                        "domain": result["domain"],
                        **result["data"],
                        "confidence_score": result["confidence_score"],
                        "sources": ["Simple OpenAI enrichment"]
                    }
                    
                    # Send enriched row result
                    yield f"data: {json.dumps({'type': 'result', 'row_index': i, 'data': enriched_data})}\n\n"
                    
                except Exception as e:
                    # Send error for this row
                    yield f"data: {json.dumps({'type': 'error', 'row_index': i, 'error': str(e)})}\n\n"
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.5)
            
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


if __name__ == "__main__":
    uvicorn.run(
        "src.api_server_simple:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )