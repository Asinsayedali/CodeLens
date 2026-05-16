# Phase 3: Setup & Testing Guide

## 🚀 Quick Start

### 1. Configure Watsonx.ai Credentials

Create a `.env` file in the `backend/` directory (or update existing):

```env
# Watsonx.ai Configuration (REQUIRED)
WATSONX_API_KEY=your_actual_api_key_here
WATSONX_PROJECT_ID=your_actual_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-13b-chat-v2

# AI Settings
MAX_TOKENS=2048
TEMPERATURE=0.3
```

### 2. Install Dependencies

Backend dependencies are already in `requirements.txt`:
```bash
cd backend
pip install -r requirements.txt
```

Frontend dependencies are already in `package.json`:
```bash
cd frontend
npm install
```

### 3. Start the Services

**Terminal 1 - Backend:**
```bash
cd backend
python -m app.main
# Server runs on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Frontend runs on http://localhost:5173
```

---

## 🧪 Testing the Implementation

### Step 1: Test Watsonx Connection

```bash
curl http://localhost:8000/api/docs/test-connection
```

**Expected Response:**
```json
{
  "status": "connected",
  "model_id": "ibm/granite-13b-chat-v2",
  "project_id": "your_project_id",
  "test_response": "..."
}
```

### Step 2: Analyze a Project

First, analyze a project to have data for documentation:

```bash
curl -X POST http://localhost:8000/api/projects/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/path/to/your/project",
    "name": "My Project"
  }'
```

**Note the project ID from the response.**

### Step 3: Generate Documentation

Generate all documentation sections:

```bash
curl -X POST http://localhost:8000/api/docs/projects/1/generate \
  -H "Content-Type: application/json"
```

Or generate a specific section:

```bash
curl -X POST http://localhost:8000/api/docs/projects/1/generate \
  -H "Content-Type: application/json" \
  -d '{"section": "overview"}'
```

**This will take 30-60 seconds as it calls watsonx.ai multiple times.**

### Step 4: Retrieve Documentation

```bash
curl http://localhost:8000/api/docs/projects/1
```

**Expected Response:**
```json
{
  "project_id": 1,
  "project_name": "My Project",
  "documentation": {
    "overview": "# Project Overview\n\n...",
    "getting_started": "# Getting Started\n\n...",
    "architecture": "# Architecture\n\n...",
    "api": "# API Documentation\n\n..."
  },
  "generated_at": "2024-01-15T10:30:00"
}
```

### Step 5: Test Frontend UI

1. Open browser to `http://localhost:5173`
2. Navigate to the project
3. Click on "Documentation" tab
4. You should see:
   - Sidebar with sections (📋 Overview, 🚀 Getting Started, etc.)
   - Markdown-rendered content
   - Generate/Regenerate buttons

---

## 🔍 Troubleshooting

### Issue: "Watsonx.ai credentials not configured"

**Solution:**
- Verify `.env` file exists in `backend/` directory
- Check `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` are set
- Restart the backend server

### Issue: "Failed to generate text"

**Possible causes:**
1. Invalid API key
2. Invalid project ID
3. Network connectivity issues
4. Rate limiting

**Solution:**
```bash
# Test connection first
curl http://localhost:8000/api/docs/test-connection

# Check the error message in the response
```

### Issue: "Documentation not generated yet"

**Solution:**
- Generate documentation first using POST endpoint
- Check backend logs for generation errors
- Verify project was analyzed successfully

### Issue: Frontend shows loading forever

**Solution:**
1. Check browser console for errors
2. Verify backend is running on port 8000
3. Check CORS settings in `backend/app/main.py`
4. Verify API_BASE_URL in frontend

---

## 📊 API Endpoints Reference

### Documentation Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/docs/test-connection` | Test watsonx.ai connection |
| POST | `/api/docs/projects/{id}/generate` | Generate documentation |
| GET | `/api/docs/projects/{id}` | Get all documentation |
| GET | `/api/docs/projects/{id}/sections/{section}` | Get specific section |
| POST | `/api/docs/projects/{id}/regenerate/{section}` | Regenerate section |
| DELETE | `/api/docs/projects/{id}` | Delete documentation |

### Section Names

- `overview` - Project Overview
- `getting_started` - Getting Started Guide
- `architecture` - Architecture Documentation
- `api` - API Documentation

---

## 🎯 Expected Behavior

### Documentation Generation Flow:

1. **User clicks "Generate Documentation"**
   - Frontend shows loading spinner
   - Backend receives request
   - Watsonx.ai generates each section sequentially
   - Takes 30-60 seconds total

2. **Documentation is stored**
   - Saved to database in `documentation` table
   - Linked to project via `project_id`
   - Ordered by `order_index`

3. **User views documentation**
   - Sidebar shows available sections
   - Click section to view content
   - Markdown is rendered with styling
   - Can regenerate individual sections

### Section Generation Order:

1. Overview (most important)
2. Getting Started (onboarding)
3. Architecture (technical details)
4. API (if endpoints detected)

---

## 🎨 UI Features

### Sidebar Navigation
- Section icons for visual identification
- Active section highlighting
- Smooth transitions
- "Regenerate All" button at bottom

### Content Area
- Professional markdown rendering
- Syntax-highlighted code blocks
- Styled tables and lists
- Responsive design (max-width: 896px)

### Actions
- Generate All Documentation
- Regenerate Specific Section
- Loading indicators
- Error messages with retry

---

## 📝 Sample Documentation Output

### Overview Section:
```markdown
# Project Overview

## Purpose
This project is a [description based on analysis]...

## Architecture
The system follows a [pattern] architecture with...

## Key Components
- **Component 1**: Handles [responsibility]
- **Component 2**: Manages [responsibility]

## Technology Stack
- Language: Python
- Framework: FastAPI
- Database: SQLite
```

### Getting Started Section:
```markdown
# Getting Started

## Prerequisites
- Python 3.8+
- pip package manager

## Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables

## Running the Project
```bash
python -m app.main
```

## Basic Usage
[Examples based on project analysis]
```

---

## ✅ Verification Checklist

- [ ] Backend server starts without errors
- [ ] Watsonx connection test passes
- [ ] Can analyze a project successfully
- [ ] Documentation generation completes
- [ ] All sections are generated
- [ ] Frontend displays documentation
- [ ] Sidebar navigation works
- [ ] Markdown renders correctly
- [ ] Can regenerate sections
- [ ] Loading states display properly
- [ ] Error handling works

---

## 🚨 Common Errors

### Error: "Import 'ibm_watsonx_ai' could not be resolved"

This is a linter error in the IDE. The package will work at runtime if installed.

**Verify installation:**
```bash
pip list | grep ibm-watsonx-ai
```

### Error: "Connection refused"

Backend is not running or wrong port.

**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, start it
cd backend && python -m app.main
```

### Error: "CORS policy blocked"

Frontend URL not in allowed origins.

**Solution:**
Check `backend/app/main.py` CORS configuration includes your frontend URL.

---

## 🎓 Tips for Best Results

### 1. Project Analysis Quality
- Ensure project is fully analyzed before generating docs
- More code = better documentation
- Include README and comments for context

### 2. Prompt Engineering
- Prompts are in `backend/app/services/doc_generator.py`
- Customize for your specific needs
- Adjust temperature for creativity vs. consistency

### 3. Performance
- Documentation generation is CPU-intensive
- Consider caching generated docs
- Use background tasks for large projects

### 4. Cost Management
- Each section generation = 1 API call
- Monitor watsonx.ai usage
- Consider rate limiting for production

---

## 📚 Additional Resources

- [IBM watsonx.ai Documentation](https://www.ibm.com/docs/en/watsonx-as-a-service)
- [React Markdown Documentation](https://github.com/remarkjs/react-markdown)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## 🎉 Success!

If you've completed all steps and verification, Phase 3 is fully operational!

**Next:** Proceed to Phase 4 - Q&A System with RAG

---

*Made with Bob - Your AI Development Partner*