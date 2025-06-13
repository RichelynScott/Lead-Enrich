import { NextRequest, NextResponse } from 'next/server';
import type { EnrichmentRequest } from '@/lib/types';

export const runtime = 'nodejs';

const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'http://127.0.0.1:8000';

export async function POST(request: NextRequest) {
  try {
    const body: EnrichmentRequest = await request.json();
    const { rows, fields, emailColumn, nameColumn } = body;

    if (!rows || rows.length === 0) {
      return NextResponse.json(
        { error: 'No rows provided' },
        { status: 400 }
      );
    }

    if (!fields || fields.length === 0) {
      return NextResponse.json(
        { error: 'No fields provided' },
        { status: 400 }
      );
    }

    if (!emailColumn) {
      return NextResponse.json(
        { error: 'Email column is required' },
        { status: 400 }
      );
    }

    // Check if Python backend is available
    try {
      const healthResponse = await fetch(`${PYTHON_BACKEND_URL}/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (!healthResponse.ok) {
        throw new Error('Python backend not available');
      }
    } catch (error) {
      return NextResponse.json(
        { 
          error: 'Python backend not available. Please start the Python server with: python -m uvicorn src.api_server:app --reload --port 8000',
          details: 'Run this command in your project root to start the advanced CrewAI backend'
        },
        { status: 503 }
      );
    }

    // Forward request to Python backend
    const pythonResponse = await fetch(`${PYTHON_BACKEND_URL}/enrich/csv`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        csv_data: rows,
        fields: fields,
        email_column: emailColumn,
        enhanced_mode: true  // Use enhanced processing
      })
    });

    if (!pythonResponse.ok) {
      const errorData = await pythonResponse.json();
      return NextResponse.json(
        { error: 'Python backend error', details: errorData },
        { status: pythonResponse.status }
      );
    }

    // Stream the response from Python backend
    const encoder = new TextEncoder();
    const decoder = new TextDecoder();
    
    const stream = new ReadableStream({
      async start(controller) {
        try {
          const reader = pythonResponse.body?.getReader();
          if (!reader) {
            throw new Error('No response body');
          }

          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            // Forward the stream data
            controller.enqueue(value);
          }
          
          controller.close();
        } catch (error) {
          controller.error(error);
        }
      }
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*',
      },
    });

  } catch (error) {
    console.error('[PYTHON-ENRICH] Error:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}