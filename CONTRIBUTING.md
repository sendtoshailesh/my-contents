# 🤝 Contributing Guide

This document provides guidelines for contributing to Personal AI Content Studio MVP.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Architecture Overview](#architecture-overview)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Common Tasks](#common-tasks)

---

## 🎯 Code of Conduct

- **Be Respectful**: Treat all contributors with respect
- **Be Clear**: Write clear commit messages and PR descriptions
- **Be Thorough**: Test your changes before submitting
- **Be Responsive**: Review and respond to feedback promptly

---

## 🏗️ Architecture Overview

### Three-Tier Architecture

```
Frontend (Streamlit)
    ↓ HTTP
Backend API (FastAPI)
    ↓ SQL
Database (SQLite)
```

### Component Layers

```
frontend/              # User-facing UI
├── pages/            # Multi-page app
└── components/       # Reusable widgets

backend/api/          # HTTP routes & schemas
backend/agents/       # LLM agent logic
backend/models/       # Data models & ORM
backend/utils/        # Helpers & logging
backend/orchestration/ # Workflow coordination

services/             # Business logic
├── framework_engine.py
├── llm_service.py
└── search_service.py
```

### Data Flow

1. **User Input** (Frontend) → 2. **API Route** (Backend) → 3. **Agent Logic** → 4. **Database** → 5. **Response** (Frontend)

---

## 🛠️ Development Workflow

### 1. Setup Development Environment

```bash
# Clone repository
cd /Users/shaileshmishra/my-docs/my-proj/my-contents

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify setup
python -c "import backend.main; print('✅ Setup complete')"
```

### 2. Create Feature Branch

```bash
# Create branch from main
git checkout -b feature/your-feature-name

# Branch naming conventions:
# - feature/new-feature-name
# - fix/bug-description
# - refactor/area-name
# - docs/documentation-area
```

### 3. Develop & Test

```bash
# Make changes, then test
pytest tests/ -v

# Run specific test
pytest tests/test_agents.py::TestClass::test_method -v

# Check formatting
flake8 backend/ --max-line-length=100
```

### 4. Commit Changes

```bash
# Stage changes
git add .

# Commit with clear message
git commit -m "feat(agents): add error handling to content_agent.py

- Add try/except blocks to generate_content()
- Log warnings for step processing errors
- Improve error messages for debugging"
```

### 5. Push & Create PR

```bash
git push origin feature/your-feature-name
# Then create PR from GitHub interface
```

---

## 📝 Code Standards

### Python Style

- **Line Length**: Max 100 characters
- **Indentation**: 4 spaces
- **Naming**: snake_case for functions/variables, PascalCase for classes

### Formatting

```bash
# Format code with black
black backend/ frontend/ services/

# Lint with flake8
flake8 backend/ --max-line-length=100

# Type check with mypy
mypy backend/ --ignore-missing-imports
```

### Docstrings

All functions should have docstrings:

```python
def generate_content(
    self,
    outline: Dict,
    framework_choice: str,
    include_code: bool = False
) -> Dict:
    """
    Generate content draft using framework structure.
    
    Args:
        outline: Dictionary with content_angle, target_audience, primary_intent, sections
        framework_choice: Selected framework ID
        include_code: Whether to include code snippets
    
    Returns:
        Dictionary with body_text, code_snippets, visual_plan, warnings
    
    Raises:
        RuntimeError: If content generation fails
    """
```

### Error Handling

Always use try/except with logging:

```python
try:
    result = do_something()
    logger.info(f"✅ Operation successful")
    return result
except ValueError as e:
    logger.error(f"❌ Invalid input: {e}")
    raise ValueError(f"Operation failed: {str(e)}")
except Exception as e:
    logger.error(f"❌ Unexpected error: {e}", exc_info=True)
    raise RuntimeError(f"Operation failed: {str(e)}")
```

### Logging Conventions

```python
logger.info(f"✅ Success message")        # Completed operations
logger.warning(f"⚠️  Warning message")     # Potential issues
logger.error(f"❌ Error message")          # Failed operations
logger.debug(f"🔍 Debug details")          # Diagnostic info
```

---

## 🧪 Testing Guidelines

### Test Structure

```python
# tests/test_agents.py
import pytest
from backend.agents.content_agent import ContentAgent

class TestContentAgent:
    """Test suite for ContentAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance for tests."""
        return ContentAgent()
    
    def test_generate_content_basic(self, agent):
        """Test basic content generation."""
        outline = {
            "content_angle": "Test Topic",
            "sections": [{"title": "Section 1"}]
        }
        
        result = agent.generate_content(
            outline=outline,
            framework_choice="TED Talk",
            framework_structure=[],
            visual_plan=[]
        )
        
        assert result is not None
        assert "body_text" in result
        assert result["framework_choice"] == "TED Talk"
    
    def test_generate_content_with_errors(self, agent):
        """Test error handling in content generation."""
        with pytest.raises(RuntimeError):
            agent.generate_content(
                outline=None,  # Invalid input
                framework_choice="test",
                framework_structure=[],
                visual_plan=[]
            )
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=backend --cov=services tests/

# Run specific module
pytest tests/test_agents.py -v

# Run with markers
pytest tests/ -m integration -v
```

---

## 🔄 Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines (flake8 passes)
- [ ] Code is formatted with black
- [ ] Unit tests pass (`pytest tests/ -v`)
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No debugging code left in
- [ ] No API keys/secrets in code

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Performance improvement
- [ ] Documentation
- [ ] Refactoring

## Related Issue
Closes #123

## Testing
- [ ] Added new tests
- [ ] Updated existing tests
- [ ] All tests pass

## Screenshots (if applicable)
Include UI changes screenshots

## Notes
Any additional context or concerns
```

### Review Process

1. Automated checks run (linting, tests)
2. Code review by maintainer
3. Feedback addressed in follow-up commits
4. Approval and merge

---

## 📋 Common Tasks

### Adding a New API Endpoint

```python
# backend/api/routes.py

@router.post("/sessions/{id}/my-endpoint")
async def my_new_endpoint(session_id: str, request: MyRequest):
    """Description of endpoint."""
    try:
        db = get_db_session()
        
        # ... implementation ...
        
        logger.info(f"✅ Operation completed")
        return {"success": True, "data": result}
        
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
```

### Adding a Frontend Page

```python
# frontend/pages/4_New_Page.py
import streamlit as st
from backend.utils.logger import frontend_logger

# Configure page
st.set_page_config(
    page_title="Page Title",
    page_icon="emoji",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title("🎨 Content Studio")
page = st.sidebar.radio(
    "Navigate",
    ["Home", "New Session", "History", "Settings"],
    index=3
)

# Implementation ...

st.divider()
st.markdown("Footer info")
```

### Adding Database Migration

```python
# Modify backend/models/models.py

class NewTable(Base):
    """New table description."""
    __tablename__ = "new_table"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    session_id = Column(String, ForeignKey('sessions.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="new_tables")
```

Then in backend/main.py startup, tables are auto-created.

### Adding Configure Feature

1. **Backend**: Create API endpoint
2. **Models**: Add data model
3. **Services**: Implement logic
4. **Frontend**: Add UI controls
5. **Tests**: Write unit tests
6. **Docs**: Update README

---

## 🚀 Deployment Checklist

Before deploying to production:

- [ ] All tests pass
- [ ] Code reviewed and approved
- [ ] Logging is comprehensive
- [ ] Error handling is complete
- [ ] Database migrations are tested
- [ ] API endpoints are documented
- [ ] UI is tested in all browsers
- [ ] Performance is acceptable
- [ ] Security review done
- [ ] Backup/recovery tested

---

## 🐛 Debugging Tips

### View Backend Logs

```bash
tail -f ~/.content-studio/app.log
```

### View Frontend Logs  

```bash
tail -f ~/.content-studio/streamlit.log
```

### Database Inspection

```bash
# Connect to SQLite database
sqlite3 ~/.content-studio/sessions.db

# List tables
.tables

# Query sessions
SELECT id, topic, status, created_at FROM sessions LIMIT 5;
```

### API Testing

```bash
# Test endpoint with curl
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"topic": "Test Topic"}'

# Or use Python requests
python -c "
import requests
r = requests.post('http://localhost:8000/api/sessions',
  json={'topic': 'Test'})
print(r.json())
"
```

---

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Python Best Practices](https://pep8.org/)

---

## 📞 Questions?

- Review existing code in `/backend`, `/frontend`, `/services`
- Check test files in `/tests` for examples
- Look at `/specs` for architectural details
- Review `/docs` for service documentation

---

**Happy Contributing!** 🚀
