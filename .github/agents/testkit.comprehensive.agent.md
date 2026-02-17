---
description: Create comprehensive testing framework with E2E tests, API validation, mock detection, intelligent recommendations, and detailed reporting following software testing best practices.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Goal

Generate a production-grade testing framework that validates entire application workflows, detects mock vs real API usage, validates configuration, and provides **intelligent, context-aware recommendations** for fixing issues. This agent applies industry-standard software testing principles (AAA pattern, test isolation, fail-fast, comprehensive assertions) and includes an **Intelligent Recommendation Engine** that automatically diagnoses failure patterns and provides priority-based, actionable guidance.

**Key Features:**
- ✅ Comprehensive E2E workflow testing
- ✅ Real vs mock API detection (4+ strategies)
- ✅ API configuration validation
- ✅ **Intelligent recommendations** (8 failure patterns detected)
- ✅ **Priority-based guidance** (🔴 CRITICAL → 🟢 LOW → ✅ SUCCESS)
- ✅ **Specific action steps** with exact commands
- ✅ **Root cause analysis** for each failure
- ✅ **Expected outcomes** after fixes

## Operating Constraints

**STRICTLY NON-DESTRUCTIVE**: Do **not** modify existing application code or test files unless explicitly requested. Create new test files in appropriate test directories.

**DEPENDENCY VALIDATION**: Before creating tests, validate that testing dependencies (pytest, httpx, asyncio) are available. If not, provide installation instructions.

**REAL vs MOCK DETECTION**: All tests MUST include mechanisms to detect whether real APIs or mock fallbacks are being used. This is CRITICAL for diagnosing configuration issues.

**INTELLIGENT RECOMMENDATIONS**: The framework MUST include an intelligent recommendation engine that analyzes test results and provides context-aware, priority-based recommendations with specific action steps. This transforms testing from purely diagnostic to prescriptive.

## Execution Steps

### 1. Initialize Testing Context

**Discover project structure:**
- Identify backend framework (FastAPI, Flask, Django, Express, etc.)
- Locate API endpoints and service files
- Find existing test directory structure
- Identify configuration/secrets management approach

**Validate prerequisites:**
- Check for existing test framework (pytest, jest, mocha)
- Verify async support if required (asyncio, async/await)
- Identify HTTP client library (httpx, requests, axios)

**Establish test organization:**
```
tests/
├── test_api_validation.py      # API key/config validator
├── test_e2e_comprehensive.py   # End-to-end workflow tests
├── unit/                       # Unit tests (if needed)
└── integration/                # Integration tests (if needed)
```

### 2. Create API Configuration Validator

Generate `tests/test_api_validation.py` with:

**Purpose:**
- Validate all required API keys/credentials are configured
- Check format and validity of credentials
- Distinguish critical vs optional services
- Provide clear setup instructions when missing

**Structure:**
```python
class ValidationStatus(Enum):
    PASS = "✅ CONFIGURED"
    FAIL = "❌ MISSING"
    WARN = "⚠️  INVALID"

@dataclass
class APIKeyValidation:
    service_name: str
    key_name: str
    status: ValidationStatus
    message: str
    is_critical: bool

class APIKeyValidator:
    def validate_<service>(self) -> APIKeyValidation
    def validate_all(self) -> List[APIKeyValidation]
    def generate_report(self) -> str
    def is_ready_for_testing(self) -> bool
```

**Detection strategies:**
1. Check environment variables
2. Check secrets management service (keyring, vault, etc.)
3. Validate format (API key patterns, URL formats)
4. Mark services as CRITICAL or OPTIONAL

**Report format:**
```
📊 API KEY VALIDATION REPORT
================================================================================

📈 Summary:
   Total Services: N
   ✅ Configured: X
   ❌ Missing: Y
   ⚡ Critical Missing: Z

💡 Recommendations:
   [Actionable setup instructions]
```

### 3. Create End-to-End Testing Agent

Generate `tests/test_e2e_comprehensive.py` with:

**Core Classes:**

```python
class TestStatus(Enum):
    PASS = "✅ PASS"
    FAIL = "❌ FAIL"
    WARN = "⚠️  WARN"
    SKIP = "⏭️  SKIP"
    MOCK = "🤖 MOCK"
    REAL = "🌐 REAL"

class APICallType(Enum):
    REAL_LLM = "Real LLM API"
    REAL_SEARCH = "Real Search API"
    REAL_DATABASE = "Real Database"
    MOCK_FALLBACK = "Mock Fallback"
    NOT_DETECTED = "Not Detected"

@dataclass
class TestResult:
    test_name: str
    status: TestStatus
    api_type: APICallType
    duration: float
    details: str
    assertions_passed: int
    assertions_total: int
    error: Optional[str] = None

class E2ETestingAgent:
    def __init__(self, base_url: str)
    async def detect_api_type(self, response_data, logs) -> APICallType
    async def test_<workflow_step>(self) -> TestResult
    async def run_all_tests(self) -> List[TestResult]
    def generate_report(self) -> str
```

**Mock Detection Strategies:**

Implement MULTIPLE detection methods for reliability:

1. **Log Analysis**: Check for API initialization failures
   ```python
   if "client not initialized" in logs:
       return APICallType.MOCK_FALLBACK
   if "failed after N retries" in logs:
       return APICallType.MOCK_FALLBACK
   ```

2. **Response Quality Analysis**: Real APIs produce richer responses
   ```python
   if len(generated_content) < MIN_THRESHOLD:
       return APICallType.MOCK_FALLBACK
   if section_count < EXPECTED_SECTIONS:
       return APICallType.MOCK_FALLBACK
   ```

3. **Placeholder Detection**: Check for mock indicators
   ```python
   mock_indicators = ["mock", "placeholder", "test data", "TODO"]
   if any(indicator in response_str for indicator in mock_indicators):
       return APICallType.MOCK_FALLBACK
   ```

4. **Validation Metrics**: Real APIs produce meaningful scores
   ```python
   if validation_percentage == 0 and expected > 0:
       return APICallType.MOCK_FALLBACK
   ```

### 4. Implement Test Cases Following AAA Pattern

**Arrange-Act-Assert Structure:**

Every test MUST follow this pattern:

```python
async def test_<functionality>(self) -> TestResult:
    start_time = time.time()
    test_name = "<Test Name>"
    
    try:
        # ARRANGE: Prepare test data and preconditions
        payload = {"key": "value"}
        assertions_passed = 0
        assertions_total = N
        
        # ACT: Execute the functionality being tested
        response = await self.client.post(endpoint, json=payload)
        duration = time.time() - start_time
        
        # ASSERT: Validate results
        assert response.status_code == 200, "Message"
        assertions_passed += 1
        
        assert "expected_field" in response.json(), "Message"
        assertions_passed += 1
        
        # ... more assertions ...
        
        # Detect API type
        api_type = self.detect_api_type(response.json())
        status = TestStatus.PASS if api_type == APICallType.REAL else TestStatus.WARN
        
        return TestResult(
            test_name=test_name,
            status=status,
            api_type=api_type,
            duration=duration,
            details="Success details",
            assertions_passed=assertions_passed,
            assertions_total=assertions_total
        )
        
    except Exception as e:
        duration = time.time() - start_time
        return TestResult(
            test_name=test_name,
            status=TestStatus.FAIL,
            api_type=APICallType.NOT_DETECTED,
            duration=duration,
            details="Failure details",
            assertions_passed=assertions_passed,
            assertions_total=assertions_total,
            error=str(e)
        )
```

**Test Isolation Principles:**

- Each test MUST be independent
- Create new test session/context per test
- No shared state between tests
- Tests can run in any order
- Cleanup resources in finally blocks

**Comprehensive Assertions:**

Each test should validate:
- HTTP status codes (200, 404, 500, etc.)
- Response structure (required fields present)
- Data types (dict, list, string, etc.)
- Data quality (length, format, content)
- Business logic (state transitions, validation rules)
- Performance (duration thresholds if critical)

### 5. Create Quick Test Runner

Generate `run_tests.py` with:

**Purpose:**
- Orchestrate complete test suite
- Implement fail-fast strategy
- Generate consolidated reports
- Provide clear exit codes

**Structure:**

```python
async def run_validation_tests() -> bool:
    """Step 1: Validate API keys - MUST pass for real testing"""
    validator = APIKeyValidator()
    results = validator.validate_all()
    report = validator.generate_report()
    return validator.is_ready_for_testing()

async def run_e2e_tests() -> bool:
    """Step 2: Run comprehensive E2E tests"""
    agent = E2ETestingAgent()
    results = await agent.run_all_tests()
    report = agent.generate_report()
    return all_tests_passed(results)

async def run_all_tests():
    """Fail-fast orchestration"""
    # Step 1: Validate configuration
    if not await run_validation_tests():
        print("❌ Configuration incomplete - cannot proceed")
        return False
    
    # Step 2: Run E2E tests
    return await run_e2e_tests()
```

**Command-line Interface:**

```python
parser = argparse.ArgumentParser()
parser.add_argument("--validate-only", help="Only validate API keys")
parser.add_argument("--e2e-only", help="Only run E2E tests")
parser.add_argument("--verbose", help="Detailed output")
```

### 6. Generate Detailed Reports

**Report Structure (Markdown):**

```markdown
📊 COMPREHENSIVE TEST REPORT
================================================================================

📈 Summary:
   Total Tests: N
   ✅ Passed: X
   ❌ Failed: Y
   ⚠️  Warnings: Z

🔌 API Calls:
   🌐 Real API: X
   🤖 Mock Fallback: Y

⏱️  Performance:
   Total Duration: Xs
   Average Duration: Xs per test

✓ Assertions:
   Passed: X/Y
   Success Rate: Z%

📋 Detailed Results:
────────────────────────────────────────────────────────────────────────────────

1. [STATUS] Test Name
   API Type: [TYPE]
   Duration: Xs
   Assertions: X/Y
   Details: [DETAILS]
   Error: [ERROR if any]

💡 Recommendations:
================================================================================

[Actionable next steps based on results]
```

**Save Reports:**
- `API_KEY_VALIDATION_REPORT.txt`
- `TEST_REPORT.txt`
- `TEST_RESULTS.json` (machine-readable)

### 7. Create Comprehensive Documentation

Generate `TESTING_GUIDE.md` with:

**Sections:**
1. **Overview**: Purpose and principles
2. **Quick Start**: Single command to run tests
3. **Test Suite Components**: What each file does
4. **Understanding Results**: How to interpret output
5. **Setting Up API Keys**: Configuration instructions
6. **Troubleshooting**: Common issues and solutions
7. **Test Reports**: How to read reports
8. **Testing Principles**: AAA, isolation, assertions
9. **Expected Results**: Before/after configuration

**Include Examples:**
- ✅ Success output
- ⚠️ Warning output (mock fallback)
- ❌ Failure output
- Configuration screenshots/steps
- Command variations

### 8. Handle Project-Specific Workflows

**Map application functionality to tests:**

For each user story or workflow step:
1. Create dedicated test method
2. Document what is being tested
3. Define expected behavior
4. Implement mock detection
5. Set appropriate assertions count

**Example Workflow Mapping:**

```python
# US1: User creates session
async def test_us1_session_creation(self) -> TestResult:
    """
    Validates: Session creation, input parsing, initial state
    Mock Detection: Check response quality and timing
    """

# US2: System generates outline
async def test_us2_outline_generation(self) -> TestResult:
    """
    Validates: LLM call, outline structure, section quality
    Mock Detection: Check outline depth, content length, API logs
    """

# US3: User approves outline
async def test_us3_outline_approval(self) -> TestResult:
    """
    Validates: State transition, workflow progression
    Mock Detection: N/A (state management only)
    """
```

### 9. Implement Best Practices Checklist

**Before completing, verify:**

✅ **Test Structure:**
- [ ] All tests follow AAA pattern
- [ ] Tests are isolated (no dependencies)
- [ ] Clear test naming (test_<workflow>_<functionality>)
- [ ] Proper async handling (await, async with)

✅ **Mock Detection:**
- [ ] Multiple detection strategies (4+)
- [ ] Log analysis implemented
- [ ] Response quality checks
- [ ] Validation metric checks
- [ ] Placeholder detection

✅ **Assertions:**
- [ ] HTTP status codes checked
- [ ] Response structure validated
- [ ] Data quality verified
- [ ] Assertion counts tracked
- [ ] Clear error messages

✅ **Reporting:**
- [ ] Summary statistics included
- [ ] Detailed test results
- [ ] Performance metrics
- [ ] Actionable recommendations
- [ ] Reports saved to files

✅ **Documentation:**
- [ ] Quick start guide
- [ ] Troubleshooting section
- [ ] Configuration instructions
- [ ] Expected results documented
- [ ] Examples provided

✅ **Fail-Fast Strategy:**
- [ ] Validates configuration first
- [ ] Stops with clear errors
- [ ] Provides next steps
- [ ] Exit codes set correctly

### 10. Provide Usage Instructions

Output clear getting-started instructions:

```bash
# Quick Validation (30 seconds)
python3 run_tests.py --validate-only

# Full Test Suite (2-3 minutes)
python3 run_tests.py

# Configure API Keys (if needed)
python3 scripts/setup_secrets.py

# View Reports
cat API_KEY_VALIDATION_REPORT.txt
cat TEST_REPORT.txt
```

**Expected Workflow:**

1. **First Run**: `python3 run_tests.py --validate-only`
   - Shows API configuration status
   - Identifies missing credentials

2. **Configure**: Follow setup instructions
   - Run secrets setup script
   - Add API keys
   - Restart services

3. **Verify**: `python3 run_tests.py`
   - All tests should pass
   - Real API calls detected
   - No mock fallbacks

4. **Monitor**: Re-run after changes
   - Validate new features
   - Catch regressions
   - Verify configurations

### 11. Implement Intelligent Recommendation Engine

Generate context-aware recommendations based on test results. The recommendation engine MUST analyze failure patterns and provide specific, actionable next steps.

**Recommendation Logic Structure:**

```python
class RecommendationEngine:
    def analyze_results(self, results: List[TestResult], 
                       validation_results: List[APIKeyValidation]) -> List[str]:
        """Generate context-aware recommendations"""
        
    def categorize_failures(self, results: List[TestResult]) -> Dict[str, List[TestResult]]:
        """Group failures by root cause"""
        
    def prioritize_actions(self, recommendations: List[str]) -> List[str]:
        """Order recommendations by priority"""
```

**Failure Pattern Detection:**

Implement detection for these common scenarios:

**1. API Configuration Issues (CRITICAL Priority):**

Detection:
- All/most tests showing `APICallType.MOCK_FALLBACK`
- API validation shows missing critical keys
- Errors contain "not initialized", "missing credentials"

Recommendation:
```
⚠️  CRITICAL: API keys not configured!

Root Cause: Azure OpenAI client not initialized

Action Required:
  1. Run: python3 scripts/setup_secrets.py
  2. Configure the following services:
     - Azure OpenAI (CRITICAL): API Key + Endpoint URL
     - Bing Search (CRITICAL): API Key
  3. Restart backend: uvicorn backend.main:app --reload --port 8000
  4. Re-run tests: python3 run_tests.py

Why this matters:
  System is using MOCK fallback - no real functionality available.
  You're seeing placeholder data instead of actual AI-generated content.

Expected outcome after fix:
  ✅ Tests show "Real LLM API" instead of "Mock Fallback"
  ✅ Content generation produces real results
  ✅ Validation percentage > 0%
```

**2. Backend Not Running (CRITICAL Priority):**

Detection:
- Connection errors: "Connection refused", "Connection reset"
- HTTP errors: Cannot reach localhost:8000
- All tests fail immediately

Recommendation:
```
❌ CRITICAL: Backend server not running!

Root Cause: Cannot connect to http://localhost:8000

Action Required:
  1. Check if backend is running: curl http://localhost:8000/health
  2. If not running, start it:
     uvicorn backend.main:app --reload --port 8000
  3. Verify it starts without errors
  4. Re-run tests: python3 run_tests.py

Common causes:
  - Backend was never started
  - Backend crashed due to dependency issues
  - Port 8000 already in use by another process

Debug steps:
  - Check logs in terminal where backend was started
  - Verify all dependencies installed: pip install -r requirements.txt
  - Check if port is available: lsof -ti:8000
```

**3. Database Not Initialized (HIGH Priority):**

Detection:
- Database errors: "no such table", "relation does not exist"
- Session/data persistence failures
- Tests pass initially but fail on data retrieval

Recommendation:
```
⚠️  Database not initialized!

Root Cause: Database tables missing

Action Required:
  1. Initialize database: python3 scripts/setup_db.py
  2. Verify tables created successfully
  3. Restart backend: uvicorn backend.main:app --reload --port 8000
  4. Re-run tests: python3 run_tests.py

Why this is needed:
  Application stores session data, outlines, and content in database.
  Without initialized database, data persistence fails.

Expected outcome:
  ✅ Sessions persist across requests
  ✅ Outline/content retrieval works
  ✅ No database errors in logs
```

**4. Partial Mock Fallback (MEDIUM Priority):**

Detection:
- Some tests use real APIs, some use mocks
- Mixed `REAL_LLM` and `MOCK_FALLBACK` results
- Some services configured, others missing

Recommendation:
```
⚠️  Partial configuration detected

Status:
  ✅ Azure OpenAI: Configured (Primary LLM working)
  ❌ Bing Search: Missing (Research validation failing)
  ✅ Anthropic: Configured (Fallback available)

Impact:
  - Content generation: ✅ Working with real AI
  - Research validation: ❌ Always shows 0% (no web search)
  - Platform adaptation: ✅ Working

Action Required (Priority Order):
  1. Configure Bing Search for research validation:
     - Get API key from Azure Portal
     - Run: python3 scripts/setup_secrets.py
     - Select option 2 (Bing Search API)
  2. Restart backend
  3. Re-run tests to verify

Optional improvements:
  - Add OpenAI key for additional fallback
  - Configure Redis for caching (future optimization)
```

**5. Test Logic Errors (MEDIUM Priority):**

Detection:
- Assertions failing on valid responses
- Status codes or structure issues
- No configuration problems detected

Recommendation:
```
⚠️  Test logic errors detected

Failed Tests:
  1. test_us5_content_generation
     - Expected: 6/6 assertions passed
     - Actual: 3/6 assertions passed
     - Issue: Content length check failing
     
Root Cause Analysis:
  Test expects content length > 1000 characters
  Actual response: 456 characters
  
Possible causes:
  a) Test expectation too strict
  b) Content generation producing shorter output
  c) Framework changed but test not updated

Action Required:
  1. Review test expectations in tests/test_e2e_comprehensive.py
  2. Check if content length threshold is appropriate
  3. Verify framework produces expected output length
  4. Update test assertions if expectations changed

Debug tip:
  Add logging to see actual content length:
  print(f"Content length: {len(content)}")
```

**6. Performance Issues (LOW Priority):**

Detection:
- All tests pass but duration exceeds thresholds
- No errors but slow response times
- Timeout warnings

Recommendation:
```
✅ All tests passed - Performance optimization recommended

Performance Metrics:
  Average test duration: 5.2s (threshold: 3.0s)
  Slowest tests:
    1. test_us2_research_validation: 12.3s
    2. test_us5_content_generation: 8.7s
    3. test_us1_topic_extraction: 6.1s

Impact: ⚠️  Tests taking longer than expected

Recommended optimizations:
  1. Enable response caching for repeated requests
  2. Use faster LLM models for testing (gpt-4o-mini vs gpt-4o)
  3. Reduce test input complexity
  4. Consider parallel test execution

Note: This is NOT critical - all functionality working correctly.
```

**7. All Tests Passed (SUCCESS):**

Detection:
- All tests status == PASS
- All API types == REAL (not MOCK)
- No warnings or errors

Recommendation:
```
🎉 SUCCESS: All tests passed!

Test Summary:
  ✅ 7/7 tests passed
  ✅ All using real APIs (no mock fallback)
  ✅ 42/42 assertions passed (100%)
  ✅ Average duration: 2.1s (excellent performance)

Configuration Status:
  ✅ Azure OpenAI configured and working
  ✅ Bing Search configured and working
  ✅ Backend healthy and responsive
  ✅ Database initialized and functioning

Next Steps:
  ✅ System ready for use!
  ✅ You can now start the frontend: streamlit run frontend/Home.py
  ✅ All workflows validated and working with real APIs
  
Maintenance:
  - Re-run tests after code changes
  - Run tests before commits
  - Include tests in CI/CD pipeline
  
No action required - everything working perfectly! 🚀
```

**Recommendation Priority Matrix:**

```python
def prioritize_recommendations(self, issues: List[Issue]) -> List[Recommendation]:
    """
    Priority Order:
    1. CRITICAL: Blocks all functionality
       - Backend not running
       - All API keys missing
       - Database not initialized
       
    2. HIGH: Blocks major features
       - Partial API configuration
       - Critical service missing
       - Authentication failures
       
    3. MEDIUM: Reduces functionality
       - Optional services missing
       - Test assertion errors
       - Single workflow failures
       
    4. LOW: Optimization opportunities
       - Performance issues
       - Code quality suggestions
       - Documentation updates
    """
```

**Implementation Template:**

```python
class RecommendationEngine:
    def generate_recommendations(
        self, 
        test_results: List[TestResult],
        validation_results: List[APIKeyValidation]
    ) -> str:
        """Generate prioritized recommendations"""
        
        # Detect failure patterns
        patterns = self._detect_patterns(test_results, validation_results)
        
        # Generate recommendations for each pattern
        recommendations = []
        
        if patterns.backend_not_running:
            recommendations.append(self._recommend_start_backend())
            
        if patterns.critical_apis_missing:
            recommendations.append(self._recommend_configure_apis(
                missing_apis=patterns.missing_critical_apis
            ))
            
        if patterns.database_errors:
            recommendations.append(self._recommend_init_database())
            
        if patterns.partial_configuration:
            recommendations.append(self._recommend_complete_config(
                configured=patterns.configured_services,
                missing=patterns.missing_services
            ))
            
        if patterns.test_logic_errors:
            recommendations.append(self._recommend_fix_tests(
                failed_tests=patterns.failed_tests
            ))
            
        if patterns.all_passed:
            recommendations.append(self._recommend_success_next_steps())
        
        # Prioritize and format
        return self._format_recommendations(
            self._prioritize(recommendations)
        )
```

**Include in Test Reports:**

Add recommendations section to test reports with:
- Clear priority indicators (🔴 CRITICAL, 🟠 HIGH, 🟡 MEDIUM, 🟢 LOW)
- Numbered action steps
- Expected outcomes after fixes
- Links to documentation
- Debug tips and common solutions

## Operating Principles

### Software Testing Best Practices

**Arrange-Act-Assert (AAA) Pattern:**
- **Arrange**: Setup test data, preconditions, mocks
- **Act**: Execute the functionality under test
- **Assert**: Validate results, side effects, state changes

**Test Isolation:**
- Each test creates its own context/session
- No shared state between tests
- Tests can run in parallel
- Independent failures

**Fail-Fast Strategy:**
- Validate dependencies before running tests
- Stop on critical failures
- Provide clear error messages
- Offer actionable next steps

**Comprehensive Assertions:**
- Multiple validation points per test
- Track assertions passed/total
- Clear assertion messages
- Test success and failure paths

**Mock Detection:**
- Critical for diagnosing configuration issues
- Multiple strategies increase confidence
- Log analysis, response quality, metrics
- Clear reporting of mock vs real

### Token Efficiency

**Minimal High-Signal Code:**
- Reusable base classes
- Helper methods for common patterns
- Avoid code duplication
- Clear, concise variable names

**Progressive Test Execution:**
- Run fast validation tests first
- Run slow E2E tests only if needed
- Skip expensive operations when possible
- Cache test sessions when appropriate

**Focused Reporting:**
- Limit detailed output to failures/warnings
- Summarize successes
- Provide metrics overview
- Save full details to files

### Context Preservation

**Report Generation:**
- Save reports to files (not just console)
- Include timestamps
- Preserve test context
- Machine-readable JSON option

**Debugging Support:**
- Capture error messages
- Include stack traces
- Log API requests/responses
- Save session IDs

**Reproducibility:**
- Document exact commands run
- Include environment details
- Specify versions
- Provide sample data

## Output Structure

Generate these files:

1. **tests/test_api_validation.py** (200-300 lines)
   - APIKeyValidator class
   - Validation methods for each service
   - Report generation
   - Main execution block

2. **tests/test_e2e_comprehensive.py** (500-700 lines)
   - E2ETestingAgent class
   - Mock detection methods
   - Test methods for each workflow
   - Report generation
   - Main execution block

3. **run_tests.py** (150-200 lines)
   - Test orchestration
   - CLI argument parsing
   - Report consolidation
   - Exit code handling

4. **TESTING_GUIDE.md** (Comprehensive documentation)
   - Overview and principles
   - Quick start guide
   - Component descriptions
   - Result interpretation
   - Configuration setup
   - Troubleshooting
   - Expected outcomes

5. **DIAGNOSIS_AND_FIX.md** (Problem-solving guide)
   - Common issues
   - Root cause analysis
   - Step-by-step fixes
   - Verification steps

## Success Criteria

The testing framework is complete when:

✅ **All test files created** with proper structure
✅ **Mock detection implemented** with 4+ strategies
✅ **AAA pattern** applied to all test methods
✅ **Test isolation** verified (can run independently)
✅ **Comprehensive assertions** (6-8 per test minimum)
✅ **Fail-fast strategy** implemented in test runner
✅ **Detailed reports** generated (both console and files)
✅ **Documentation complete** with examples and troubleshooting
✅ **First test run** produces clear actionable output
✅ **Configuration issues** clearly diagnosed and reported

## Project-Specific Adaptations

When applying this agent to a new project:

1. **Identify Backend Framework:**
   - FastAPI → Use httpx.AsyncClient
   - Flask → Use requests or httpx
   - Express → Use axios or fetch
   - Django → Use TestClient

2. **Map User Stories to Tests:**
   - Extract workflows from spec/requirements
   - Create one test per major workflow step
   - Group related tests by feature

3. **Identify Mock Scenarios:**
   - API integrations (LLMs, Search, Payments)
   - External services (Email, SMS, Storage)
   - Database connections (if testable)

4. **Configure Test Data:**
   - Sample inputs for each workflow
   - Expected outputs/structures
   - Edge cases and error scenarios

5. **Adapt Mock Detection:**
   - Identify service-specific patterns
   - Add custom detection strategies
   - Validate against known mock responses

## Context

$ARGUMENTS
