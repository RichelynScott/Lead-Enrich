# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Frontend Development
```bash
npm install              # Install dependencies
npm run dev             # Start development server with Turbopack
npm run build           # Build for production
npm run start           # Start production server
npm run lint            # Run ESLint
```

### Python Backend Development
```bash
pip install -r requirements.txt        # Install Python dependencies
python tests/test_basic_imports.py     # Test basic functionality
python tests/test_enhanced_csv_processing.py  # Test CSV processing
python tests/test_simple_enrichment.py # Test enrichment pipeline
python examples/example.py             # Basic enrichment example
python examples/example_enhanced_csv.py # Enhanced CSV example
```

### Integration Commands
```bash
# Start Python backend server (for advanced features)
python start_python_backend.py
# OR manually:
python -m uvicorn src.api_server:app --reload --port 8000

# In another terminal, start frontend
npm run dev

# Access integrated system at http://localhost:3000/fire-enrich
```

### Environment Setup
- Frontend: Copy `.env.example` to `.env.local` and configure API keys
- Python: Copy `.env.example` to `.env` and configure API keys
- Required: `FIRECRAWL_API_KEY`, `OPENAI_API_KEY`

## Architecture Overview

### Dual-Stack Architecture
This is a hybrid Next.js/Python application with **two backend options**:

1. **TypeScript Backend (Default)**: Built-in Next.js API routes with agent-based enrichment
2. **Python Backend (Advanced)**: CrewAI multi-agent system with enhanced features

### Backend Integration
The frontend automatically detects Python backend availability and provides a toggle:
- **TypeScript**: Uses `/api/enrich` route with TypeScript agents
- **Python**: Uses `/api/enrich-python` route that proxies to `http://127.0.0.1:8000`
- **Auto-detection**: Frontend checks `http://127.0.0.1:8000/health` every 30 seconds
- **User Choice**: Toggle in UI to select backend (Python backend must be running)

### Core Frontend Architecture

**API Routes Pattern**: `/app/api/[action]/route.ts`
- `enrich/route.ts`: Main enrichment pipeline with SSE streaming
- `scrape/route.ts`: Web scraping endpoint
- `generate-fields/route.ts`: Dynamic field generation

**Agent Orchestration**: `/lib/agent-architecture/`
```
orchestrator.ts -> routes fields to specialized agents
agents/[agent-name].ts -> individual agent implementations
core/agent-base.ts -> base class with handoff system
```

**Specialized Agents**:
- Discovery Agent: Company identification and basic info
- Company Profile Agent: Industry classification, business model
- Funding Agent: Investment history and financial data
- Tech Stack Agent: Technology analysis and stack detection
- Metrics Agent: Business metrics and performance data
- General Agent: Custom field extraction

### Python Multi-Agent System

**Core Class**: `src/lead_enricher.py` - LeadEnricher
- Uses CrewAI framework for sequential agent orchestration
- Supports both basic enrichment and enhanced CSV processing
- Handles decision maker validation and email research

**Agent Structure**: `src/agents/[agent_name]_agent.py`
- Each agent specializes in specific data extraction
- Agents work sequentially, building context for next agent
- Uses Pydantic schemas for type safety

**Processing Modes**:
- `enrich_email_sync()`: Individual email enrichment
- `enrich_csv()`: Basic CSV batch processing
- `process_lead_csv()`: Enhanced lead processing with validation

### Configuration System

**Unlimited Mode**: `app/fire-enrich/config.ts`
- Automatically enabled in development
- Controls CSV limits, request sizes, field counts
- Set `FIRE_ENRICH_UNLIMITED=true` for production unlimited mode

**Rate Limiting**: Built-in protection with 1-second delays between rows

### Data Flow Architecture

1. **CSV Upload** -> Field mapping and validation
2. **Agent Routing** -> Fields categorized by type (funding, tech, metrics)
3. **Sequential Processing** -> Agents execute in dependency order
4. **Real-time Streaming** -> Results streamed via SSE to frontend
5. **Source Attribution** -> All data linked to source URLs

### Key Patterns

**Field Routing Logic** (orchestrator.ts):
- "fund|invest" keywords -> Funding Agent
- "tech|stack" keywords -> Tech Stack Agent  
- "employee|revenue" keywords -> Metrics Agent
- "industry|headquarter" keywords -> Company Profile Agent
- Everything else -> General Agent

**Skip List System**: `lib/utils/skip-list.ts`
- Automatically skips personal email providers (Gmail, Yahoo, etc.)
- Configurable via `app/fire-enrich/skip-list.txt`

**Error Handling**: 
- Graceful degradation with confidence scores
- Source URL tracking for transparency
- Retry logic with exponential backoff

### Type Safety

**Frontend**: TypeScript with Zod schemas
- `lib/types/index.ts`: Core type definitions
- Agent input/output schemas defined per agent
- Runtime validation for API boundaries

**Python**: Pydantic models
- `src/models/schemas.py`: All data models
- Strict validation for agent inputs/outputs
- Type hints throughout codebase

### Testing Strategy

**Python Tests**: Sequential validation
1. Import tests -> Basic functionality -> CSV processing
2. Run in order to validate complete pipeline
3. Each test builds on previous functionality

**Frontend**: Next.js built-in linting and type checking

### Performance Considerations

- Concurrent processing with rate limiting
- Smart caching of search results 
- Deduplication of search queries
- Memory management for large CSV files
- SSE for real-time progress without blocking

### Extension Points

**Adding New Agents**:
1. Create agent file in `lib/agent-architecture/agents/`
2. Extend `BaseAgent` class with Zod schemas
3. Add routing logic to orchestrator
4. Update type definitions

**Custom Field Types**:
- Modify agent schemas to include new fields
- General Agent handles unrecognized fields automatically
- Field routing can be extended in orchestrator

### Dependencies

**Critical Frontend Dependencies**:
- `@mendable/firecrawl-js`: Web scraping service
- `openai`: GPT-4 integration
- `zod`: Runtime type validation
- `@radix-ui/*`: UI component library

**Critical Python Dependencies**:
- `crewai[tools]`: Multi-agent framework
- `firecrawl-py`: Python Firecrawl client
- `selenium`: Browser automation
- `pandas`: CSV processing