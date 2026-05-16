# 🔍 Grasp - Intelligent Repository Analysis Platform

> **Accelerate codebase understanding with AI-powered analysis, interactive visualizations, and intelligent documentation**

Grasp is a powerful tool that helps developers quickly understand unfamiliar codebases through automated analysis, interactive dependency visualization, and AI-powered documentation generation.

---

## 🎯 Why CodeLens?

### For New Team Members
- **Fast Onboarding:** Understand architecture in hours, not weeks
- **Interactive Learning:** Explore code relationships visually through dependency graphs
- **AI Documentation:** Get comprehensive, auto-generated documentation

### For Senior Developers
- **Audit Unfamiliar Repos:** Quickly assess code quality and architecture
- **Understand Dependencies:** See how modules connect and interact
- **Analyze Structure:** Deep dive into code organization and patterns

### For Development Teams
- **Living Documentation:** Auto-generated docs that stay up-to-date
- **Knowledge Sharing:** Capture architectural decisions automatically
- **Visual Analysis:** Interactive graphs for better understanding

---

## ✨ Implemented Features

### 1. 📊 Interactive Dependency Graph
- **Visual Mapping:** Complete visualization of module relationships
- **Interactive Exploration:** Click nodes to see detailed information
- **Multiple Layouts:** Hierarchical and force-directed graph layouts
- **Advanced Filtering:** Filter by node type, search by name
- **Custom Node Types:** Distinct styling for files, classes, and functions
- **Real-time Statistics:** Node and edge counts, graph metrics
- **AI Assistant:** Generate code snippets and explanations

### 2. 🔍 Core Analysis Engine
- **Multi-Language Support:** Python, JavaScript, and TypeScript
- **AST Analysis:** Deep code structure extraction
- **Dependency Extraction:** Automatic import and call relationship mapping
- **Graph Building:** Hierarchical graph structure with importance scoring
- **Repository Parsing:** Support for both local paths and GitHub URLs

### 3. 📝 AI-Powered Documentation
- **Watsonx.ai Integration:** IBM Granite models for intelligent documentation
- **Multiple Sections:** Overview, Getting Started, Architecture, API docs
- **Markdown Rendering:** Beautiful, professional documentation viewer
- **Section Regeneration:** Update specific sections without regenerating all
- **Context-Aware:** Documentation based on actual code analysis

### 4. 💻 CLI Tool
- **Project Analysis:** Analyze local and remote repositories
- **Project Management:** List, view, and delete analyzed projects
- **Progress Tracking:** Real-time analysis progress with Rich formatting
- **Easy Integration:** Simple commands for all operations

### 5. 🌐 Web Dashboard
- **Modern UI:** React 18 with TypeScript and Tailwind CSS
- **Responsive Design:** Works seamlessly on all screen sizes
- **Real-time Updates:** Live data fetching and updates
- **Professional Styling:** Polished, production-ready interface

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git
- IBM watsonx.ai account (for AI documentation features and node explanation features)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/grasp.git
cd grasp

# Set up backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .

# Set up frontend
cd ../frontend
npm install

# Configure environment
cp .env.example .env
# Edit .env with your watsonx.ai credentials
```

### Configuration

Create a `.env` file in the project root:

```env inside backend folder
# Watsonx.ai Configuration
WATSONX_API_KEY=<Your-API-KEY>
WATSONX_PROJECT_ID=<Your-PROJECT-ID>
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-4-h-small
WATSONX_EMBEDDING_MODEL_ID=ibm/granite-embedding-278m-multilingual
WATSONX_ANSWERING_MODEL_ID=meta-llama/llama-3-3-70b-instruct
```

```env inside front end folder
VITE_API_URL=http://localhost:8000
```
### Usage

#### CLI Commands

```bash
cd backend && source venv/bin/activate

python cli/main.py version          # Show version
python cli/main.py list             # List all projects
python cli/main.py init             # Initialize DB
python cli/main.py analyze /path/to/repo --name "My Project"
python cli/main.py analyze https://github.com/user/repo
python cli/main.py delete <project_id>
python cli/main.py serve --port 8001

```

#### Web Dashboard

1. Start the backend server:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

2. Start the frontend:
```bash
cd frontend
npm run dev
```

3. Open your browser to `http://localhost:5173`

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERFACES                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐              ┌──────────────────────────┐ │
│  │  CLI Tool    │              │   Web Dashboard          │ │
│  │              │              │                          │ │
│  │ • analyze    │              │  ┌────────┐  ┌────────┐ │ │
│  │ • list       │              │  │ Graph  │  │  Docs  │ │ │
│  │ • delete     │              │  │ Viewer │  │ Viewer │ │ │
│  │ • serve      │              │  └────────┘  └────────┘ │ │
│  └──────────────┘              └──────────────────────────┘ │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                  API ENDPOINTS                          │ │
│  │  /projects  /graph  /docs                              │ │
│  └────────────────────────────────────────────────────────┘ │
│                          │                                    │
│                          ▼                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                 CORE SERVICES                           │ │
│  │                                                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │ │
│  │  │ Repo Parser  │  │ AST Analyzer │  │ Dependency   │ │ │
│  │  │              │  │              │  │ Analyzer     │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │ │
│  │                                                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │ │
│  │  │ Graph        │  │ Graph        │  │ Doc          │ │ │
│  │  │ Builder      │  │ Serializer   │  │ Generator    │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │ │
│  │                                                          │ │
│  │  ┌────────────────────────────────────────────────────┐ │ │
│  │  │         Watsonx.ai Client (IBM Granite)           │ │ │
│  │  └────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    SQLITE DATABASE                           │
├─────────────────────────────────────────────────────────────┤
│  • Projects  • Graph Nodes/Edges  • Documentation           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Backend
- **Framework:** FastAPI 0.104.1
- **Database:** SQLite with SQLAlchemy 2.0.23
- **CLI:** Typer 0.9.0 with Rich 13.7.0
- **Code Analysis:** Python AST, tree-sitter
- **AI:** IBM watsonx.ai (Granite models & Llama models)
- **Testing:** pytest

### Frontend
- **Framework:** React 18 with TypeScript 5.3
- **Build Tool:** Vite 5.0
- **Graph Visualization:** React Flow
- **Styling:** Tailwind CSS 3.3
- **API Client:** Axios
- **Markdown:** react-markdown

### Supported Languages
- ✅ Python (.py)
- ✅ JavaScript (.js, .jsx)
- ✅ TypeScript (.ts, .tsx)

---

## 📊 Current Implementation Status

### ✅ Phase 0: Foundation & Setup - COMPLETE
- Complete project structure
- Backend infrastructure (FastAPI + SQLite)
- Frontend infrastructure (React + TypeScript)
- CLI tool skeleton
- Configuration management

### ✅ Phase 1: Core Analysis Engine - COMPLETE
- Repository parser (local + GitHub)
- AST analyzers (Python, JavaScript, TypeScript)
- Dependency extraction
- Graph builder
- Database storage
- API endpoints
- CLI commands

### ✅ Phase 2: Graph Visualization - COMPLETE
- React Flow integration
- Interactive graph component
- Custom node types
- Multiple layout algorithms
- Search and filter functionality
- Node details panel
- Graph statistics

### ✅ Phase 3: AI Integration & Documentation - COMPLETE
- Watsonx.ai client integration
- Documentation generator with prompt templates
- Documentation API endpoints
- Beautiful documentation viewer UI
- Markdown rendering
- Section-based regeneration

---

## 📖 API Documentation

### Projects API
- `GET /api/projects` - List all projects
- `GET /api/projects/{id}` - Get project details
- `POST /api/projects/analyze` - Analyze repository
- `DELETE /api/projects/{id}` - Delete project

### Graph API
- `GET /api/projects/{id}/graph` - Get complete graph
- `GET /api/projects/{id}/graph/reactflow` - Get React Flow formatted graph
- `GET /api/projects/{id}/graph/nodes` - Get nodes with filtering
- `GET /api/projects/{id}/graph/node/{node_id}` - Get node details
- `GET /api/projects/{id}/graph/edges` - Get edges with filtering

### Documentation API
- `GET /api/docs/test-connection` - Test watsonx.ai connection
- `POST /api/docs/projects/{id}/generate` - Generate documentation
- `GET /api/docs/projects/{id}` - Get all documentation
- `GET /api/docs/projects/{id}/sections/{section}` - Get specific section
- `POST /api/docs/projects/{id}/regenerate/{section}` - Regenerate section
- `DELETE /api/docs/projects/{id}` - Delete documentation

---

## 🎓 Key Features in Detail

### Interactive Dependency Graph
- **Hierarchical Layout:** Organized top-down view of dependencies
- **Force-Directed Layout:** Physics-based organic layout
- **Node Types:** Files (blue), Classes (green), Functions (purple)
- **Edge Types:** Imports, Contains, Calls relationships
- **Zoom & Pan:** Smooth navigation controls
- **Mini-map:** Overview of entire graph
- **Search:** Find nodes by name
- **Filter:** Show/hide specific node types

### AI Documentation Generation
- **Project Overview:** High-level architecture and purpose
- **Getting Started:** Setup and usage instructions
- **Architecture:** System design and component relationships
- **API Documentation:** Endpoint descriptions and usage
- **Context-Aware:** Based on actual code analysis
- **Regeneration:** Update sections individually

### Code Analysis
- **AST Parsing:** Deep structural analysis
- **Import Resolution:** Track all dependencies
- **Call Graph:** Function call relationships
- **Importance Scoring:** Identify critical components
- **Statistics:** Lines of code, file counts, language distribution

---

## 🔒 Security & Privacy

- **Local Execution:** All analysis runs on your machine
- **Secure Storage:** API keys in environment variables
- **No Data Upload:** Code stays local (except AI API calls for docs)
- **Database:** Local SQLite file
- **GitHub Tokens:** Optional, only for private repos

---

## 🐛 Troubleshooting

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'app'`
```bash
# Solution: Ensure you're in the backend directory and venv is activated
cd backend
source venv/bin/activate
pip install -e .
```

**Issue:** `watsonx.ai authentication failed`
```bash
# Solution: Check your .env file has correct credentials
cat .env | grep WATSONX
```

**Issue:** `Graph not rendering in dashboard`
```bash
# Solution: Check browser console, ensure API is running
curl http://localhost:8000/api/health
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Report Bugs:** Open an issue with details
2. **Suggest Features:** Share your ideas
3. **Submit PRs:** Follow our coding standards
4. **Improve Docs:** Help make documentation better

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **IBM watsonx.ai** for Granite and Llama models
- **FastAPI** for the excellent web framework
- **React Flow** for graph visualization
- **Tree-sitter** for universal code parsing

---

## 📧 Contact

- **Issues:** [GitHub Issues](https://github.com/yourusername/codelens/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/codelens/discussions)

---

**Built with IBM BOB ❤️ for developers who want to understand code faster**

---

*Current Version: 1.0.0 - Phases 0-3 Complete*
