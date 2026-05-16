# Phase 1 Setup Guide - Environment Configuration

This guide explains how to set up the environment variables needed for Phase 1 (Core Analysis Engine).

---

## 📋 Quick Start for Phase 1

**Good News!** For Phase 1, you only need minimal configuration. Most environment variables are optional or have sensible defaults.

### Required Steps

1. **Copy the environment file:**
   ```bash
   cp .env.example backend/.env
   ```

2. **That's it!** Phase 1 will work with default values.

---

## 🔧 Environment Variables Explained

### For Phase 1 (Current Phase)

#### ✅ **Already Configured (No Action Needed)**

These have sensible defaults and work out of the box:

```env
# Database - Uses local SQLite file
DATABASE_URL=sqlite:///./codelens.db

# Server Configuration
API_HOST=127.0.0.1
API_PORT=8000
FRONTEND_URL=http://localhost:5173

# Analysis Settings
MAX_FILE_SIZE_MB=10
SUPPORTED_LANGUAGES=python,javascript,typescript
ANALYSIS_TIMEOUT_SECONDS=300
MAX_WORKERS=4

# Debug Mode
DEBUG=false
```

#### 🔓 **Optional for Phase 1**

**GitHub Token** (Only needed for private repositories):
```env
GITHUB_TOKEN=your_github_token_here
```

**When to set:** Only if you want to analyze private GitHub repositories.

**How to get:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name (e.g., "CodeLens")
4. Select scopes: `repo` (for private repos) or leave empty (for public repos)
5. Click "Generate token"
6. Copy the token and paste it in your `.env` file

---

### For Future Phases (Not Needed Yet)

#### ⏳ **Watsonx.ai Configuration** (Phase 3+)

These are only needed for AI-powered documentation and Q&A features in Phase 3:

```env
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-13b-chat-v2
```

**When needed:** Phase 3 (AI Integration & Documentation)

**How to get:**
1. Sign up for IBM Cloud: https://cloud.ibm.com/registration
2. Create a watsonx.ai instance: https://cloud.ibm.com/catalog/services/watsonx-ai
3. Get your API key:
   - Go to https://cloud.ibm.com/iam/apikeys
   - Click "Create an IBM Cloud API key"
   - Copy the API key
4. Get your Project ID:
   - Go to your watsonx.ai instance
   - Create or select a project
   - Copy the Project ID from the project settings

**Cost:** IBM offers a free tier for watsonx.ai with limited usage.

---

## 🚀 Complete Setup Instructions for Phase 1

### Step 1: Create Environment File

```bash
cd backend
cp ../.env.example .env
```

### Step 2: Edit .env (Optional)

Open `backend/.env` and modify only if needed:

```env
# For private GitHub repos (optional)
GITHUB_TOKEN=ghp_your_token_here

# Change port if 8000 is in use (optional)
API_PORT=8001

# Enable debug mode for development (optional)
DEBUG=true
```

### Step 3: Initialize Database

```bash
# Make sure you're in the backend directory
cd backend

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# Initialize database
python -c "from app.database import init_db; init_db()"
# OR
codelens init
```

### Step 4: Test the Setup

```bash
# Test CLI
codelens --help
codelens version

# Test API server
codelens serve
# OR
uvicorn app.main:app --reload --port 8000
```

Visit http://localhost:8000 - you should see:
```json
{
  "name": "CodeLens",
  "version": "0.1.0",
  "status": "running"
}
```

---

## 📝 Minimal .env for Phase 1

Here's the absolute minimum you need in `backend/.env`:

```env
# Database (default is fine)
DATABASE_URL=sqlite:///./codelens.db

# Server (defaults are fine)
API_HOST=127.0.0.1
API_PORT=8000

# Optional: Only if analyzing private GitHub repos
# GITHUB_TOKEN=your_token_here
```

**That's it!** Everything else has defaults.

---

## 🧪 Testing Your Setup

### Test 1: Analyze a Public GitHub Repository

```bash
codelens analyze https://github.com/pallets/click
```

Expected output:
```
🔍 Starting analysis of: https://github.com/pallets/click
📥 Step 1: Preparing repository...
📂 Step 2: Scanning repository...
   Found X files (Y lines)
...
🎉 Analysis complete!
```

### Test 2: Analyze a Local Directory

```bash
codelens analyze ./backend
```

### Test 3: List Projects

```bash
codelens list
```

### Test 4: Test API

```bash
# List projects
curl http://localhost:8000/api/projects

# Get graph data (replace 1 with your project ID)
curl http://localhost:8000/api/projects/1/graph
```

---

## 🐛 Troubleshooting

### Issue: "Module not found" errors

**Solution:** Make sure dependencies are installed:
```bash
cd backend
pip install -r requirements.txt
```

### Issue: "Database not found"

**Solution:** Initialize the database:
```bash
codelens init
```

### Issue: "Port already in use"

**Solution:** Change the port in `.env`:
```env
API_PORT=8001
```

Then use:
```bash
codelens serve --port 8001
```

### Issue: "Failed to clone repository"

**Solutions:**
1. Check your internet connection
2. Verify the GitHub URL is correct
3. For private repos, add your GitHub token to `.env`

### Issue: "Permission denied" when cloning

**Solution:** Add GitHub token to `.env`:
```env
GITHUB_TOKEN=ghp_your_token_here
```

---

## 📊 What Works in Phase 1

✅ **Working Features:**
- Analyze local repositories
- Analyze public GitHub repositories
- Analyze private GitHub repositories (with token)
- Extract Python code structure
- Extract JavaScript/TypeScript code structure
- Build dependency graphs
- Store results in database
- List all projects
- Delete projects
- REST API endpoints
- CLI commands

❌ **Not Yet Implemented:**
- Graph visualization (Phase 2)
- AI-powered documentation (Phase 3)
- Q&A interface (Phase 4)
- Tech debt detection (Phase 5)

---

## 🔐 Security Notes

1. **Never commit `.env` files** - They're already in `.gitignore`
2. **Keep tokens private** - Don't share your GitHub or API tokens
3. **Use environment variables** - Don't hardcode credentials in code
4. **Rotate tokens regularly** - Generate new tokens periodically

---

## 📚 Additional Resources

- **GitHub Token Guide:** https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
- **IBM Watsonx.ai:** https://www.ibm.com/watsonx (for Phase 3+)
- **SQLite Documentation:** https://www.sqlite.org/docs.html

---

## ✅ Checklist

Before running Phase 1:

- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created in `backend/` directory
- [ ] Database initialized (`codelens init`)
- [ ] CLI working (`codelens --help`)
- [ ] Server starts (`codelens serve`)

Optional:
- [ ] GitHub token added (for private repos)
- [ ] Custom port configured (if needed)

---

## 🎯 Summary

**For Phase 1, you need:**
1. ✅ Copy `.env.example` to `backend/.env`
2. ✅ Install dependencies
3. ✅ Initialize database
4. ✅ (Optional) Add GitHub token for private repos

**You DON'T need yet:**
- ❌ Watsonx.ai credentials (Phase 3+)
- ❌ Any other external services

**Ready to go!** 🚀

```bash
codelens analyze /path/to/your/repo