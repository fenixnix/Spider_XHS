# Agent Guidelines for Spider_XHS

This document provides guidelines for AI agents working on the Spider_XHS project (小红书数据采集解决方案).

## Project Overview

Spider_XHS is a Xiaohongshu (Little Red Book) data scraping solution with multiple entry points:
- **CLI**: `python main.py` - Traditional scraping workflow
- **FastAPI**: `uvicorn app.main:app --reload` - REST API server at `/docs`
- **Gradio UI**: `python gradio_app.py` - Web interface

## Dependencies

```bash
pip install -r requirements.txt
npm install  # For crypto-js and jsdom
```

## Code Style Guidelines

### Imports
Organize imports in three groups with blank lines between:
1. Standard library (`import os`, `import json`)
2. Third-party packages (`from loguru import logger`, `import requests`)
3. Local modules (`from apis.xhs_pc_apis import XHS_Apis`)

### Naming Conventions
- **Classes**: PascalCase (`XHS_Apis`, `Data_Spider`)
- **Functions/variables**: snake_case (`spider_note`, `note_list`)
- **Constants**: UPPER_SNAKE_CASE where appropriate
- Use descriptive Chinese comments for complex logic (following existing codebase patterns)

### Type Hints
Use type hints for function parameters and return types:
```python
def spider_note(self, note_url: str, cookies_str: str, proxies: dict = None) -> tuple[bool, str, dict]:
```

### Error Handling
- Wrap API calls in try/except blocks
- Return tuples: `(success: bool, msg: str, data: any)`
- Use `loguru.logger` for all logging
- Convert exceptions to strings: `msg = str(e)`

```python
try:
    success, msg, res_json = self.xhs_apis.get_note_info(...)
    if success:
        # process data
except Exception as e:
    success = False
    msg = str(e)
logger.info(f'爬取笔记信息 {note_url}: {success}, msg: {msg}')
return success, msg, data
```

### API Patterns
All XHS API methods follow this signature:
```python
def method_name(self, cookies_str: str, proxies: dict = None) -> tuple[bool, str, dict]:
```

Use `generate_request_params()` from `xhs_utils.xhs_util` for request signing.

### Response Formats
- Return `success` (bool) and `msg` (str) from all API methods
- Data is returned as the third element of the tuple
- Log operations with `logger.info()` using Chinese messages

## Directory Structure

```
Spider_XHS/
├── main.py           # CLI entry point
├── gradio_app.py     # Gradio UI
├── apis/
│   ├── xhs_pc_apis.py      # Xiaohongshu PC API
│   └── xhs_creator_apis.py # Creator platform API
├── xhs_utils/
│   ├── common_util.py      # Initialization, paths
│   ├── data_util.py        # Data processing, downloads
│   ├── cookie_util.py      # Cookie handling
│   ├── xhs_util.py        # Request signing, headers
│   ├── xhs_signature.py    # X-s header signatures
│   └── xhs_creator_util.py # Creator utilities
├── app/
│   ├── main.py            # FastAPI app
│   ├── api/               # API routes
│   ├── dependencies.py    # Dependencies injection
│   └── schemas/           # Pydantic schemas
├── datas/                # Output (media, excel)
├── static/              # Static files
└── requirements.txt     # Python deps
```

## Common Operations

### Adding New API Endpoints
1. Add method to appropriate API class in `apis/`
2. Use `generate_request_params()` for request signing
3. Follow return tuple pattern: `(success, msg, data)`
4. Add error handling with try/except
5. Log with `logger.info()`

### Modifying Data Processing
Update `xhs_utils/data_util.py` for:
- `handle_note_info()` - Transform raw note data
- `download_note()` - Media file downloads
- `save_to_xlsx()` - Excel export

### Environment Configuration
- Use `.env` for cookies and secrets
- Load via `python-dotenv`: `load_dotenv()`
- Get values: `os.getenv('COOKIES')`

## Key Technologies
- **requests**: HTTP client
- **loguru**: Structured logging
- **pycryptodome**: Encryption for API signatures
- **openpyxl**: Excel output
- **fastapi/uvicorn**: REST API server
- **gradio**: Web UI framework
- **crypto-js/jsdom**: Node.js utilities for request signing

## Testing

There is no formal test suite. Test changes manually:
1. Update cookies in `.env`
2. Run entry point and verify output in `datas/` directory
3. Check logs for errors
4. Verify Excel/media outputs are correct
