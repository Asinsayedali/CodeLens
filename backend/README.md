# CodeLens Backend

## Setup Instructions

### 1. Create Virtual Environment

```bash
cd backend
python3 -m venv venv
```

### 2. Activate Virtual Environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install CLI Tool

```bash
pip install -e .
```

This installs the `codelens` command globally in your virtual environment.

### 5. Initialize Database

```bash
python -c "from app.database import init_db; init_db()"
```

Or use the CLI:
```bash
codelens init
```

### 6. Configure Environment

Copy the example environment file:
```bash
cp ../.env.example .env
```

Edit `.env` and add your watsonx.ai credentials.

### 7. Test the Setup

**Test CLI:**
```bash
codelens --help
codelens version
```

**Test FastAPI Server:**
```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000 to see the API.

**Test with CLI serve command:**
```bash
codelens serve
```

## Development

### Running Tests

```bash
pytest
pytest --cov=app --cov-report=html
```

### Code Quality

```bash
# Linting
pylint app/

# Type checking
mypy app/

# Security scanning
bandit -r app/
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── database.py          # Database setup and models
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API routes
│   ├── services/            # Business logic
│   └── utils/               # Utility functions
├── cli/
│   ├── main.py              # CLI entry point
│   └── commands/            # CLI commands
├── tests/                   # Test files
├── requirements.txt         # Python dependencies
└── setup.py                 # Package setup
```

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check

### Future Endpoints (Coming in Phase 1+)
- `POST /api/projects` - Create new project
- `GET /api/projects` - List all projects
- `GET /api/projects/{id}` - Get project details
- `POST /api/projects/{id}/analyze` - Analyze project
- `GET /api/projects/{id}/graph` - Get dependency graph
- `GET /api/projects/{id}/docs` - Get documentation
- `POST /api/projects/{id}/qa` - Ask questions
- `GET /api/projects/{id}/tech-debt` - Get tech debt items

## CLI Commands

### Available Now (Phase 0)
- `codelens --help` - Show help
- `codelens version` - Show version
- `codelens init` - Initialize database
- `codelens serve` - Start web server

### Coming Soon
- `codelens analyze <repo>` - Analyze repository (Phase 1)
- `codelens list` - List projects (Phase 1)
- `codelens export <id>` - Export analysis (Phase 6)
- `codelens delete <id>` - Delete project (Phase 6)

## Troubleshooting

### Import Errors
If you get import errors, make sure:
1. Virtual environment is activated
2. You're in the backend directory
3. Dependencies are installed: `pip install -r requirements.txt`

### Database Errors
If database initialization fails:
```bash
rm codelens.db  # Remove old database
codelens init   # Reinitialize
```

### CLI Not Found
If `codelens` command is not found:
```bash
pip install -e .  # Reinstall in editable mode
```

## Next Steps

Phase 0 is complete! Next:
1. Implement repository parser (Phase 1)
2. Build AST analyzers (Phase 1)
3. Create dependency extractor (Phase 1)
4. Implement graph builder (Phase 1)

See [PROJECT_PLAN.md](../PROJECT_PLAN.md) for details.