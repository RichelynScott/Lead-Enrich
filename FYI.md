# Lead-Enrich Development Log

## Overview
An open-source AI-powered data enrichment tool transforming email lists into rich datasets.

## Technical Decisions
- **Dependency Pinning**: Added `httpx==0.27.2` to `requirements.txt` and `requirements-minimal.txt` to resolve OpenAI client initialization error (`Client.__init__() got an unexpected keyword argument 'proxies'`) caused by incompatibility between `openai` SDK and newer `httpx` versions.

## Error Log
- **2025-06-13 – Startup Failure**: Python backend failed on startup with `TypeError: Client.__init__() got an unexpected keyword argument 'proxies'`.
  - **Resolution**: Pin `httpx` to `0.27.2`, the last version supporting the deprecated `proxies` argument which the current OpenAI SDK uses.

## Future Improvements
- Monitor OpenAI Python SDK releases for removal of deprecated usage and update dependency pin once official fix is released. 