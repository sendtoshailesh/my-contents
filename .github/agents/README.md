# Agent Repository Index

## 📁 Available Agents

This directory contains reusable agent definitions that can be applied to this project or any future projects.

### 1. **speckit.analyze.agent.md**
**Purpose:** Perform non-destructive cross-artifact consistency and quality analysis

**When to Use:**
- After generating spec.md, plan.md, and tasks.md
- Before implementation begins
- To validate alignment with project constitution
- To catch duplications, ambiguities, underspecification

**Key Features:**
- Constitution authority validation
- Requirement coverage analysis
- Duplication detection
- Ambiguity flagging
- Task-to-requirement mapping

**Usage:**
```
@speckit.analyze [optional context]
```

---

### 2. **testkit.comprehensive.agent.md** ⭐ NEW
**Purpose:** Create comprehensive testing framework with E2E tests, API validation, and mock detection

**When to Use:**
- New project setup (before writing first test)
- Adding testing to existing project
- Replacing inadequate test coverage
- Diagnosing mock vs real API issues
- Establishing testing standards

**Key Features:**
- API key/configuration validation
- End-to-end workflow testing
- Mock vs real API detection (4 strategies)
- Arrange-Act-Assert (AAA) pattern
- Test isolation and independence
- Fail-fast strategy
- Comprehensive assertions
- Detailed reporting with recommendations

**Usage:**
```
@testkit.comprehensive Create comprehensive testing framework

Context:
- Backend: [FastAPI/Flask/Django/Express]
- User Stories: [List main workflows]
- External APIs: [List services requiring API keys]
- Database: [PostgreSQL/MongoDB/SQLite/etc]
```

**Generated Files:**
```
tests/
├── test_api_validation.py        # API key validator
├── test_e2e_comprehensive.py     # E2E test suite
run_tests.py                       # Test orchestrator
TESTING_GUIDE.md                   # Complete documentation
DIAGNOSIS_AND_FIX.md              # Troubleshooting guide
```

**Quick Commands:**
```bash
# Validate API configuration
python3 run_tests.py --validate-only

# Run full test suite
python3 run_tests.py

# Configure missing APIs
python3 scripts/setup_secrets.py
```

---

## 📚 How to Use These Agents

### For This Project (my-contents)

Both agents have already been applied:

**speckit.analyze:**
- Used for spec validation
- Constitution alignment checks
- Requirements coverage

**testkit.comprehensive:**
- ✅ Tests created and ready to use
- ✅ API validation implemented
- ✅ E2E workflows tested
- ✅ Documentation complete

Just run: `python3 run_tests.py`

### For New Projects

1. **Copy agent file(s)** to new project:
   ```bash
   cp .github/agents/testkit.comprehensive.agent.md /path/to/new-project/.github/agents/
   ```

2. **Invoke with context**:
   ```
   @testkit.comprehensive Create testing framework
   
   Context: [Your project details]
   ```

3. **Review and customize** generated files

4. **Run tests** to validate

---

## 🎯 Agent Comparison Matrix

| Feature | speckit.analyze | testkit.comprehensive |
|---------|----------------|----------------------|
| **Phase** | Planning/Design | Development/Testing |
| **Purpose** | Validate specs | Validate implementation |
| **Destructive** | No (read-only) | No (creates new files) |
| **Output** | Analysis report | Test files + reports |
| **Reusable** | ✅ Any spec project | ✅ Any software project |
| **Dependencies** | None (bash scripts) | pytest, httpx |
| **Run Frequency** | After spec changes | After code changes |
| **Exit Criteria** | No CRITICAL issues | All tests pass |

---

## 🔄 Typical Project Workflow

### Phase 1: Specification (Use speckit.analyze)

1. Write spec.md, plan.md
2. Generate tasks.md
3. Run `@speckit.analyze`
4. Fix CRITICAL issues
5. Re-run until clean

### Phase 2: Implementation

1. Implement features
2. Commit code

### Phase 3: Testing (Use testkit.comprehensive)

1. Run `@testkit.comprehensive` (if not done yet)
2. Run `python3 run_tests.py --validate-only`
3. Configure missing API keys
4. Run `python3 run_tests.py`
5. Fix failing tests
6. Verify all pass with real APIs

### Phase 4: Maintenance

- Run tests before commits
- Run tests in CI/CD
- Update tests for new features
- Re-run speckit.analyze for spec changes

---

## 📖 Documentation

### For speckit.analyze
- See agent file: `.github/agents/speckit.analyze.agent.md`
- Constitution reference: `.specify/memory/constitution.md`

### For testkit.comprehensive
- **Agent file**: `.github/agents/testkit.comprehensive.agent.md`
- **Usage guide**: `.github/agents/TESTKIT_USAGE_GUIDE.md` ⭐
- **Testing guide**: `TESTING_GUIDE.md`
- **Troubleshooting**: `DIAGNOSIS_AND_FIX.md`

---

## 🎓 Best Practices

### When Creating New Agents

Follow the established pattern:

1. **YAML Frontmatter**: Brief description
2. **User Input Section**: `$ARGUMENTS` placeholder
3. **Goal**: Clear objective
4. **Operating Constraints**: Boundaries and rules
5. **Execution Steps**: Numbered, detailed steps
6. **Operating Principles**: Guidelines and best practices
7. **Context**: `$ARGUMENTS` at end

### Agent Naming Convention

- Use **noun.verb** pattern: `speckit.analyze`, `testkit.comprehensive`
- Make it **descriptive**: Clear what it does
- Keep it **short**: Easy to remember and type
- Use **lowercase**: Consistent with file naming

### Agent Documentation

Each agent should have:
- ✅ Clear description
- ✅ Detailed execution steps
- ✅ Example usage
- ✅ Expected outputs
- ✅ Success criteria
- ✅ (Optional) Usage guide for complex agents

---

## 🚀 Quick Reference

### speckit.analyze
```bash
# After generating tasks
@speckit.analyze

# With specific focus
@speckit.analyze Focus on API design consistency
```

### testkit.comprehensive
```bash
# For new project
@testkit.comprehensive Create comprehensive testing framework

Context:
- Backend: FastAPI
- Features: Content generation, research, validation
- APIs: Azure OpenAI, Bing Search
```

---

## 📞 Support

- **Questions about agents**: Review agent .md files
- **Usage examples**: Check USAGE_GUIDE files
- **Testing issues**: See TESTING_GUIDE.md and DIAGNOSIS_AND_FIX.md
- **Spec issues**: Review constitution.md

---

## 🎯 Current Status

### This Project (my-contents)

✅ **speckit.analyze**: Available and ready
✅ **testkit.comprehensive**: Applied and working

**Testing Framework Status:**
- ✅ API validation: `tests/test_api_validation.py`
- ✅ E2E tests: `tests/test_e2e_comprehensive.py`
- ✅ Test runner: `run_tests.py`
- ✅ Documentation: `TESTING_GUIDE.md`, `DIAGNOSIS_AND_FIX.md`
- ⚠️  **Action Required**: Configure API keys (run `python3 scripts/setup_secrets.py`)

**Quick Start:**
```bash
# Check configuration status
python3 run_tests.py --validate-only

# Configure API keys
python3 scripts/setup_secrets.py

# Run full test suite
python3 run_tests.py
```

---

**Last Updated:** February 16, 2026
**Agent Count:** 2
**Status:** Production Ready ✅
