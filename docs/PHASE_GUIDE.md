# CodeLens - Phase Implementation Guide

Quick reference for implementing each phase of the CodeLens project.

---

## 📋 Phase Overview

| Phase | Focus | Duration | Key Deliverables |
|-------|-------|----------|------------------|
| **Phase 0** | Foundation & Setup | Week 1 | Project structure, environment, basic infrastructure |
| **Phase 1** | Core Analysis Engine | Weeks 2-3 | Repository parsing, AST analysis, dependency extraction |
| **Phase 2** | Graph Visualization | Week 4 | Interactive dependency graph, web UI |
| **Phase 3** | AI & Documentation | Weeks 5-6 | Watsonx.ai integration, auto-generated docs |
| **Phase 4** | Q&A Interface | Week 7 | RAG system, chat interface |
| **Phase 5** | Tech Debt Detection | Week 8 | Code quality analysis, improvement cards |
| **Phase 6** | Integration & Polish | Week 9 | Complete features, error handling, UX |
| **Phase 7** | Testing & Optimization | Week 10 | Tests, performance, deployment |

---

## 🎯 Phase 0: Foundation & Setup

### Checklist
- [ ] Create complete folder structure
- [ ] Set up Python virtual environment
- [ ] Install all backend dependencies
- [ ] Create SQLite database schema
- [ ] Implement basic CLI with `--help`
- [ ] Set up FastAPI server skeleton
- [ ] Initialize React project with Vite
- [ ] Create `.env` configuration file
- [ ] Initialize Git repository
- [ ] Write initial README

### Commands to Run
```bash
# Create virtual environment
cd CodeLens/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app.database import init_db; init_db()"

# Test CLI
python -m cli.main --help

# Test FastAPI
uvicorn app.main:app --reload

# Set up frontend
cd ../frontend
npm install
npm run dev
```

### Success Criteria
✅ All folders exist  
✅ `pip install` completes without errors  
✅ CLI shows help message  
✅ FastAPI server starts on port 8000  
✅ React dev server starts on port 5173  
✅ Database file created with all tables  

---

## 🎯 Phase 1: Core Analysis Engine

### Checklist
- [ ] Implement `repo_parser.py` - clone repos
- [ ] Build `ast_analyzer.py` for Python
- [ ] Build `ast_analyzer.py` for JavaScript/TypeScript
- [ ] Create `dependency_analyzer.py`
- [ ] Implement `graph_builder.py`
- [ ] Add progress tracking to CLI
- [ ] Store results in database
- [ ] Test with sample repositories

### Key Files to Create
- `backend/app/services/repo_parser.py`
- `backend/app/services/ast_analyzer.py`
- `backend/app/services/dependency_analyzer.py`
- `backend/app/services/graph_builder.py`
- `backend/cli/commands/analyze.py`

### Test Command
```bash
codelens analyze /path/to/test/repo
codelens analyze https://github.com/user/small-repo
```

### Success Criteria
✅ Can clone GitHub repos  
✅ Detects Python and JS/TS files correctly  
✅ Extracts imports and function definitions  
✅ Builds graph with nodes and edges  
✅ Stores analysis in database  
✅ CLI shows progress bar  

---

## 🎯 Phase 2: Graph Visualization

### Checklist
- [ ] Create graph API endpoints
- [ ] Implement graph serialization
- [ ] Set up React Flow
- [ ] Build `DependencyGraph.tsx` component
- [ ] Add node click handlers
- [ ] Implement zoom/pan controls
- [ ] Add search and filter
- [ ] Create node details panel
- [ ] Style nodes by type
- [ ] Add graph legend

### Key Files to Create
- `backend/app/api/graph.py`
- `frontend/src/components/Graph/DependencyGraph.tsx`
- `frontend/src/components/Graph/NodeDetails.tsx`
- `frontend/src/components/Graph/GraphControls.tsx`

### API Endpoints
- `GET /api/projects/{id}/graph` - Get graph data
- `GET /api/projects/{id}/graph/node/{node_id}` - Get node details

### Success Criteria
✅ API returns graph in correct format  
✅ Graph renders smoothly  
✅ Can interact with nodes  
✅ Zoom and pan work  
✅ Search finds nodes  
✅ Different node types have different colors  

---

## 🎯 Phase 3: AI Integration & Documentation

### Checklist
- [ ] Set up watsonx.ai authentication
- [ ] Create `watsonx_client.py`
- [ ] Implement prompt templates
- [ ] Build `doc_generator.py`
- [ ] Generate project overview
- [ ] Generate module explanations
- [ ] Create getting started guide
- [ ] Build documentation API
- [ ] Create `DocViewer.tsx` component
- [ ] Add markdown rendering

### Key Files to Create
- `backend/app/services/watsonx_client.py`
- `backend/app/services/doc_generator.py`
- `backend/app/api/docs.py`
- `frontend/src/components/Documentation/DocViewer.tsx`

### Environment Variables Needed
```env
WATSONX_API_KEY=your_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-13b-chat-v2
```

### Success Criteria
✅ Successfully connects to watsonx.ai  
✅ Generates coherent documentation  
✅ Covers all major modules  
✅ Documentation is helpful for onboarding  
✅ UI displays docs with navigation  

---

## 🎯 Phase 4: Q&A Interface

### Checklist
- [ ] Generate code embeddings
- [ ] Store embeddings in database
- [ ] Implement semantic search
- [ ] Build `qa_engine.py` with RAG
- [ ] Create Q&A API endpoints
- [ ] Build `ChatInterface.tsx`
- [ ] Add suggested questions
- [ ] Display code snippets in responses
- [ ] Implement conversation history

### Key Files to Create
- `backend/app/services/qa_engine.py`
- `backend/app/api/qa.py`
- `frontend/src/components/QA/ChatInterface.tsx`
- `frontend/src/components/QA/MessageList.tsx`

### API Endpoints
- `POST /api/projects/{id}/qa` - Ask question
- `GET /api/projects/{id}/qa/history` - Get history
- `GET /api/projects/{id}/qa/suggestions` - Get suggested questions

### Success Criteria
✅ Can answer "Where is X?"  
✅ Can explain "How does Y work?"  
✅ Retrieves relevant code context  
✅ Responses include code snippets  
✅ Maintains conversation history  

---

## 🎯 Phase 5: Tech Debt Detection

### Checklist
- [ ] Implement complexity calculation
- [ ] Detect code smells
- [ ] Check for code duplication
- [ ] Scan for outdated dependencies
- [ ] Check for security vulnerabilities
- [ ] Calculate priority scores
- [ ] Create tech debt API
- [ ] Build `DebtDashboard.tsx`
- [ ] Create `DebtCard.tsx`
- [ ] Add filtering by severity

### Key Files to Create
- `backend/app/services/tech_debt_detector.py`
- `backend/app/api/tech_debt.py`
- `frontend/src/components/TechDebt/DebtDashboard.tsx`
- `frontend/src/components/TechDebt/DebtCard.tsx`

### Detection Categories
- **Critical:** Security vulnerabilities
- **High:** High complexity, no tests
- **Medium:** Code smells, missing docs
- **Low:** Minor refactoring

### Success Criteria
✅ Detects high-complexity functions  
✅ Identifies code smells  
✅ Flags outdated dependencies  
✅ Prioritizes issues correctly  
✅ UI displays actionable cards  

---

## 🎯 Phase 6: Integration & Polish

### Checklist
- [ ] Complete all CLI commands
- [ ] Add comprehensive error handling
- [ ] Implement loading states
- [ ] Add toast notifications
- [ ] Create unified dashboard
- [ ] Implement project management
- [ ] Add export functionality
- [ ] Write user documentation
- [ ] Add keyboard shortcuts
- [ ] Polish UI/UX

### CLI Commands to Complete
```bash
codelens analyze <repo>
codelens serve [--port 8000]
codelens list
codelens export <project-id> [--format json|pdf]
codelens delete <project-id>
```

### Success Criteria
✅ All features work end-to-end  
✅ Graceful error handling  
✅ Clear loading indicators  
✅ User documentation complete  
✅ Dashboard is intuitive  

---

## 🎯 Phase 7: Testing & Optimization

### Checklist
- [ ] Write unit tests for services
- [ ] Write API integration tests
- [ ] Write CLI tests
- [ ] Test with real repositories
- [ ] Optimize graph rendering
- [ ] Optimize AI API calls (caching)
- [ ] Profile slow operations
- [ ] Fix identified bugs
- [ ] Write deployment guide
- [ ] Create demo video

### Testing Commands
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_services/test_ast_analyzer.py
```

### Success Criteria
✅ Test coverage > 70%  
✅ All tests pass  
✅ Analysis < 5 min for medium repos  
✅ Graph renders smoothly  
✅ No memory leaks  
✅ Deployment guide complete  

---

## 🚀 Quick Start After Each Phase

### After Phase 0
```bash
cd CodeLens/backend
source venv/bin/activate
python -m cli.main --help
```

### After Phase 1
```bash
codelens analyze /path/to/test/repo
# Check database for results
sqlite3 codelens.db "SELECT * FROM projects;"
```

### After Phase 2
```bash
codelens serve
# Open http://localhost:8000
# Navigate to graph view
```

### After Phase 3
```bash
# Analyze a repo
codelens analyze /path/to/repo
# View documentation in dashboard
```

### After Phase 4
```bash
# Open dashboard
# Go to Q&A tab
# Ask: "How does authentication work?"
```

### After Phase 5
```bash
# Open dashboard
# Go to Tech Debt tab
# Review prioritized issues
```

---

## 📊 Progress Tracking

Use this checklist to track overall progress:

- [ ] **Phase 0 Complete** - Foundation ready
- [ ] **Phase 1 Complete** - Can analyze repos
- [ ] **Phase 2 Complete** - Graph visualization works
- [ ] **Phase 3 Complete** - Documentation generated
- [ ] **Phase 4 Complete** - Q&A interface functional
- [ ] **Phase 5 Complete** - Tech debt detection working
- [ ] **Phase 6 Complete** - All features integrated
- [ ] **Phase 7 Complete** - Tested and optimized

---

## 🎓 Resources

- **Project Plan:** [`PROJECT_PLAN.md`](./PROJECT_PLAN.md)
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **React Flow:** https://reactflow.dev/
- **Watsonx.ai:** https://www.ibm.com/watsonx
- **Tree-sitter:** https://tree-sitter.github.io/tree-sitter/

---

## 💡 Tips

1. **Test incrementally** - Don't wait until the end
2. **Use sample repos** - Start with small, simple projects
3. **Check database** - Verify data is stored correctly
4. **Read logs** - Enable debug logging for troubleshooting
5. **Ask for help** - Review documentation and examples

---

## 🔄 Phase Approval Process

After completing each phase:

1. ✅ Complete all checklist items
2. ✅ Verify success criteria
3. ✅ Demo the features
4. ✅ Get approval to proceed
5. ✅ Move to next phase

---

Ready to start? Begin with **Phase 0: Foundation & Setup**!