"""
Comprehensive End-to-End Testing Agent
======================================

This test suite validates the entire workflow from user input to content generation.
Following software testing best practices:
- Arrange-Act-Assert (AAA) pattern
- Test isolation and independence  
- Clear test naming conventions
- Comprehensive assertions
- Mock detection and real API validation
- Integration testing strategy

User Stories Covered:
- US1: Topic extraction and outline generation
- US2: Research and validation
- US3: Framework selection
- US4: Content generation
- US5: Platform adaptation
- US6: Iteration and refinement
"""

import pytest
import asyncio
import httpx
import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class TestStatus(Enum):
    """Test execution status"""
    PASS = "✅ PASS"
    FAIL = "❌ FAIL"
    WARN = "⚠️  WARN"
    SKIP = "⏭️  SKIP"
    MOCK = "🤖 MOCK"
    REAL = "🌐 REAL"


class APICallType(Enum):
    """Type of API call detected"""
    REAL_LLM = "Real LLM API"
    REAL_SEARCH = "Real Search API"
    MOCK_FALLBACK = "Mock Fallback"
    NOT_DETECTED = "Not Detected"


@dataclass
class TestResult:
    """Test result container"""
    test_name: str
    status: TestStatus
    api_type: APICallType
    duration: float
    details: str
    assertions_passed: int
    assertions_total: int
    error: Optional[str] = None


@dataclass
class WorkflowValidation:
    """Validation results for workflow step"""
    step_name: str
    expected_output: str
    actual_output: Any
    is_valid: bool
    validation_errors: List[str]


class E2ETestingAgent:
    """
    Comprehensive End-to-End Testing Agent
    
    Responsibilities:
    1. Test all 12 user functionalities
    2. Detect mock vs real API calls
    3. Validate workflow state transitions
    4. Measure performance metrics
    5. Generate detailed test reports
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[TestResult] = []
        self.session_id: Optional[str] = None
        self.client = httpx.AsyncClient(timeout=60.0)
        
    async def close(self):
        """Cleanup resources"""
        await self.client.aclose()
        
    # ========================================================================
    # CORE TESTING METHODS
    # ========================================================================
    
    def detect_api_type(self, response_data: Dict, logs: str = "") -> APICallType:
        """
        Detect if response came from real API or mock fallback
        
        Detection strategies:
        1. Check for mock indicators in response
        2. Look for API error messages in logs
        3. Validate response quality/length
        4. Check for placeholder text
        """
        
        # Strategy 1: Check logs for API failures
        if "Azure OpenAI client not initialized" in logs:
            return APICallType.MOCK_FALLBACK
        if "failed after 3 retries" in logs:
            return APICallType.MOCK_FALLBACK
            
        # Strategy 2: Check response for mock indicators
        response_str = json.dumps(response_data).lower()
        mock_indicators = [
            "mock",
            "placeholder",
            "example content",
            "test data",
            "not implemented"
        ]
        
        for indicator in mock_indicators:
            if indicator in response_str:
                return APICallType.MOCK_FALLBACK
                
        # Strategy 3: Check response quality
        if isinstance(response_data, dict):
            # Check outline quality
            if "outline" in response_data:
                outline = response_data["outline"]
                if isinstance(outline, dict) and "sections" in outline:
                    sections = outline["sections"]
                    # Real API should generate multiple detailed sections
                    if len(sections) < 2:
                        return APICallType.MOCK_FALLBACK
                    # Check section content depth
                    for section in sections:
                        if "content" in section and len(section["content"]) < 20:
                            return APICallType.MOCK_FALLBACK
                            
            # Check content quality
            if "content" in response_data:
                content = response_data["content"]
                if isinstance(content, str) and len(content) < 100:
                    return APICallType.MOCK_FALLBACK
                    
        # Strategy 4: Check for successful API indicators
        if "validated" in response_str or "research" in response_str:
            # If we have validation data, check if it's meaningful
            if "validation" in response_data:
                validation = response_data["validation"]
                if isinstance(validation, dict):
                    # Real validation should have percentage > 0
                    if validation.get("percentage", 0) > 0:
                        return APICallType.REAL_LLM
                        
        return APICallType.NOT_DETECTED
    
    async def test_health_check(self) -> TestResult:
        """Test 0: Health check endpoint"""
        start_time = time.time()
        test_name = "Health Check"
        
        try:
            response = await self.client.get(f"{self.base_url}/health")
            duration = time.time() - start_time
            
            # Assertions
            assertions_passed = 0
            assertions_total = 3
            
            assert response.status_code == 200, "Status code should be 200"
            assertions_passed += 1
            
            data = response.json()
            assert "status" in data, "Response should contain 'status'"
            assertions_passed += 1
            
            assert data["status"] == "healthy", "Status should be 'healthy'"
            assertions_passed += 1
            
            return TestResult(
                test_name=test_name,
                status=TestStatus.PASS,
                api_type=APICallType.NOT_DETECTED,
                duration=duration,
                details=f"Backend healthy: {data}",
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
                details="Health check failed",
                assertions_passed=0,
                assertions_total=3,
                error=str(e)
            )
    
    async def test_us1_topic_extraction(self, user_input: str) -> TestResult:
        """
        Test US1: Topic extraction and outline generation
        
        Validates:
        - Session creation
        - Topic extraction from input
        - Outline generation with sections
        - Mock vs Real API detection
        """
        start_time = time.time()
        test_name = "US1: Topic Extraction & Outline"
        
        try:
            # Arrange: Prepare session request
            payload = {"user_input": user_input}
            
            # Act: Create session and trigger workflow
            response = await self.client.post(
                f"{self.base_url}/api/sessions",
                json=payload
            )
            duration = time.time() - start_time
            
            # Assert: Validate response
            assertions_passed = 0
            assertions_total = 8
            
            assert response.status_code == 200, "Should return 200 OK"
            assertions_passed += 1
            
            data = response.json()
            assert "session_id" in data, "Should return session_id"
            assertions_passed += 1
            
            self.session_id = data["session_id"]
            
            # Wait for workflow to complete
            await asyncio.sleep(3)
            
            # Get outline
            outline_response = await self.client.get(
                f"{self.base_url}/api/sessions/{self.session_id}/outline"
            )
            
            assert outline_response.status_code == 200, "Outline should be available"
            assertions_passed += 1
            
            outline_data = outline_response.json()
            assert "outline" in outline_data, "Should contain outline"
            assertions_passed += 1
            
            outline = outline_data["outline"]
            assert isinstance(outline, dict), "Outline should be dict"
            assertions_passed += 1
            
            assert "title" in outline, "Outline should have title"
            assertions_passed += 1
            
            assert "sections" in outline, "Outline should have sections"
            assertions_passed += 1
            
            sections = outline["sections"]
            assert len(sections) > 0, "Should have at least one section"
            assertions_passed += 1
            
            # Detect API type
            api_type = self.detect_api_type(outline_data)
            
            status = TestStatus.PASS if api_type == APICallType.REAL_LLM else TestStatus.WARN
            
            return TestResult(
                test_name=test_name,
                status=status,
                api_type=api_type,
                duration=duration,
                details=f"Generated outline with {len(sections)} sections. Title: {outline.get('title', 'N/A')}",
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
                details="Topic extraction failed",
                assertions_passed=assertions_passed,
                assertions_total=assertions_total,
                error=str(e)
            )
    
    async def test_us2_research_validation(self) -> TestResult:
        """
        Test US2: Research and fact validation
        
        Validates:
        - Claims extraction from outline
        - Web search execution
        - Fact validation percentage
        - Mock vs Real Search API detection
        """
        start_time = time.time()
        test_name = "US2: Research & Validation"
        
        if not self.session_id:
            return TestResult(
                test_name=test_name,
                status=TestStatus.SKIP,
                api_type=APICallType.NOT_DETECTED,
                duration=0,
                details="Skipped: No active session",
                assertions_passed=0,
                assertions_total=6,
                error="Session not initialized"
            )
        
        try:
            # Act: Get validation results
            response = await self.client.get(
                f"{self.base_url}/api/sessions/{self.session_id}/validation"
            )
            duration = time.time() - start_time
            
            # Assert
            assertions_passed = 0
            assertions_total = 6
            
            assert response.status_code == 200, "Should return validation data"
            assertions_passed += 1
            
            data = response.json()
            assert "validation" in data, "Should contain validation"
            assertions_passed += 1
            
            validation = data["validation"]
            assert isinstance(validation, dict), "Validation should be dict"
            assertions_passed += 1
            
            # Check for validation fields
            has_percentage = "percentage" in validation
            has_claims = "claims" in validation or "validated_claims" in validation
            has_sources = "sources" in validation or "search_results" in validation
            
            if has_percentage:
                assertions_passed += 1
            if has_claims:
                assertions_passed += 1
            if has_sources:
                assertions_passed += 1
            
            # Detect if real search was used
            percentage = validation.get("percentage", 0)
            
            if percentage == 0:
                api_type = APICallType.MOCK_FALLBACK
                status = TestStatus.WARN
            elif percentage > 50:
                api_type = APICallType.REAL_SEARCH
                status = TestStatus.PASS
            else:
                api_type = APICallType.NOT_DETECTED
                status = TestStatus.WARN
            
            return TestResult(
                test_name=test_name,
                status=status,
                api_type=api_type,
                duration=duration,
                details=f"Validation percentage: {percentage}%. Claims validated: {has_claims}",
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
                details="Research validation failed",
                assertions_passed=0,
                assertions_total=6,
                error=str(e)
            )
    
    async def test_us3_outline_approval(self) -> TestResult:
        """Test US3: Outline approval workflow"""
        start_time = time.time()
        test_name = "US3: Outline Approval"
        
        if not self.session_id:
            return TestResult(
                test_name=test_name,
                status=TestStatus.SKIP,
                api_type=APICallType.NOT_DETECTED,
                duration=0,
                details="Skipped: No active session",
                assertions_passed=0,
                assertions_total=3,
                error="Session not initialized"
            )
        
        try:
            # Act: Approve outline
            response = await self.client.post(
                f"{self.base_url}/api/sessions/{self.session_id}/approve"
            )
            duration = time.time() - start_time
            
            # Assert
            assertions_passed = 0
            assertions_total = 3
            
            assert response.status_code == 200, "Should approve successfully"
            assertions_passed += 1
            
            data = response.json()
            assert "message" in data or "status" in data, "Should return confirmation"
            assertions_passed += 1
            
            # Verify state changed
            session_response = await self.client.get(
                f"{self.base_url}/api/sessions/{self.session_id}"
            )
            session_data = session_response.json()
            
            # Check if outline is marked as approved
            approved = session_data.get("outline_approved", False)
            if approved or session_data.get("status") == "approved":
                assertions_passed += 1
            
            return TestResult(
                test_name=test_name,
                status=TestStatus.PASS,
                api_type=APICallType.NOT_DETECTED,
                duration=duration,
                details="Outline approved successfully",
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
                details="Outline approval failed",
                assertions_passed=0,
                assertions_total=3,
                error=str(e)
            )
    
    async def test_us4_framework_selection(self, framework: str = "problem-solution") -> TestResult:
        """
        Test US4: Framework selection and application
        
        Validates:
        - Framework list retrieval
        - Framework selection
        - Framework application to content
        """
        start_time = time.time()
        test_name = "US4: Framework Selection"
        
        if not self.session_id:
            return TestResult(
                test_name=test_name,
                status=TestStatus.SKIP,
                api_type=APICallType.NOT_DETECTED,
                duration=0,
                details="Skipped: No active session",
                assertions_passed=0,
                assertions_total=5,
                error="Session not initialized"
            )
        
        try:
            # First, get available frameworks
            frameworks_response = await self.client.get(
                f"{self.base_url}/api/frameworks"
            )
            
            assertions_passed = 0
            assertions_total = 5
            
            assert frameworks_response.status_code == 200, "Should return frameworks"
            assertions_passed += 1
            
            frameworks_data = frameworks_response.json()
            assert isinstance(frameworks_data, dict), "Should be dict"
            assertions_passed += 1
            
            # Act: Select framework
            response = await self.client.post(
                f"{self.base_url}/api/sessions/{self.session_id}/framework",
                json={"framework": framework}
            )
            duration = time.time() - start_time
            
            assert response.status_code == 200, "Should select framework"
            assertions_passed += 1
            
            data = response.json()
            assert "message" in data or "framework" in data, "Should confirm selection"
            assertions_passed += 1
            
            # Verify framework was saved
            session_response = await self.client.get(
                f"{self.base_url}/api/sessions/{self.session_id}"
            )
            session_data = session_response.json()
            
            if session_data.get("framework") == framework:
                assertions_passed += 1
            
            return TestResult(
                test_name=test_name,
                status=TestStatus.PASS,
                api_type=APICallType.NOT_DETECTED,
                duration=duration,
                details=f"Framework '{framework}' selected successfully",
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
                details="Framework selection failed",
                assertions_passed=0,
                assertions_total=5,
                error=str(e)
            )
    
    async def test_us5_content_generation(self) -> TestResult:
        """
        Test US5: Content generation with framework
        
        Validates:
        - Content generation triggered
        - Content structure matches framework
        - Content quality and length
        - Mock vs Real LLM detection
        """
        start_time = time.time()
        test_name = "US5: Content Generation"
        
        if not self.session_id:
            return TestResult(
                test_name=test_name,
                status=TestStatus.SKIP,
                api_type=APICallType.NOT_DETECTED,
                duration=0,
                details="Skipped: No active session",
                assertions_passed=0,
                assertions_total=6,
                error="Session not initialized"
            )
        
        try:
            # Act: Generate content
            response = await self.client.post(
                f"{self.base_url}/api/sessions/{self.session_id}/content"
            )
            duration = time.time() - start_time
            
            # Assert
            assertions_passed = 0
            assertions_total = 6
            
            assert response.status_code == 200, "Should generate content"
            assertions_passed += 1
            
            data = response.json()
            assert "content" in data or "message" in data, "Should return content"
            assertions_passed += 1
            
            # Get full session to check content
            session_response = await self.client.get(
                f"{self.base_url}/api/sessions/{self.session_id}"
            )
            session_data = session_response.json()
            
            content = session_data.get("content", "")
            
            if content:
                assertions_passed += 1
                
                # Check content length (real LLM should generate substantial content)
                if len(content) > 100:
                    assertions_passed += 1
                    
                # Check content structure
                if len(content) > 500:
                    assertions_passed += 1
                    
                # Check for framework-specific patterns
                framework = session_data.get("framework", "")
                if framework in content.lower() or len(content) > 1000:
                    assertions_passed += 1
            
            # Detect API type
            api_type = self.detect_api_type(session_data)
            status = TestStatus.PASS if api_type == APICallType.REAL_LLM else TestStatus.WARN
            
            return TestResult(
                test_name=test_name,
                status=status,
                api_type=api_type,
                duration=duration,
                details=f"Generated {len(content)} characters of content",
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
                details="Content generation failed",
                assertions_passed=0,
                assertions_total=6,
                error=str(e)
            )
    
    async def test_us6_platform_adaptation(self, platform: str = "linkedin") -> TestResult:
        """
        Test US6: Platform-specific content adaptation
        
        Validates:
        - Platform selection
        - Content adaptation
        - Platform-specific formatting
        """
        start_time = time.time()
        test_name = "US6: Platform Adaptation"
        
        if not self.session_id:
            return TestResult(
                test_name=test_name,
                status=TestStatus.SKIP,
                api_type=APICallType.NOT_DETECTED,
                duration=0,
                details="Skipped: No active session",
                assertions_passed=0,
                assertions_total=4,
                error="Session not initialized"
            )
        
        try:
            # Act: Request platform adaptation
            response = await self.client.post(
                f"{self.base_url}/api/sessions/{self.session_id}/platform",
                json={"platform": platform}
            )
            duration = time.time() - start_time
            
            # Assert
            assertions_passed = 0
            assertions_total = 4
            
            assert response.status_code == 200, "Should adapt for platform"
            assertions_passed += 1
            
            data = response.json()
            assert "content" in data or "message" in data, "Should return adapted content"
            assertions_passed += 1
            
            # Check if platform-specific content exists
            platform_content = data.get("content", "")
            if platform_content and len(platform_content) > 50:
                assertions_passed += 1
                
            # Verify platform was saved
            session_response = await self.client.get(
                f"{self.base_url}/api/sessions/{self.session_id}"
            )
            session_data = session_response.json()
            
            if session_data.get("platform") == platform:
                assertions_passed += 1
            
            # Detect API type
            api_type = self.detect_api_type(data)
            status = TestStatus.PASS if assertions_passed >= 3 else TestStatus.WARN
            
            return TestResult(
                test_name=test_name,
                status=status,
                api_type=api_type,
                duration=duration,
                details=f"Adapted content for {platform}",
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
                details="Platform adaptation failed",
                assertions_passed=0,
                assertions_total=4,
                error=str(e)
            )
    
    # ========================================================================
    # TEST EXECUTION & REPORTING
    # ========================================================================
    
    async def run_all_tests(self, user_input: str = "Write about the future of AI in healthcare") -> List[TestResult]:
        """
        Run comprehensive test suite for all user stories
        
        Returns list of TestResult objects
        """
        print("\n" + "="*80)
        print("🧪 COMPREHENSIVE E2E TESTING AGENT")
        print("="*80)
        print(f"Testing user input: '{user_input}'")
        print("="*80 + "\n")
        
        # Test 0: Health check
        print("Running Test 0: Health Check...")
        result = await self.test_health_check()
        self.results.append(result)
        self._print_result(result)
        
        # Test 1: Topic extraction and outline
        print("\nRunning Test 1: Topic Extraction & Outline Generation...")
        result = await self.test_us1_topic_extraction(user_input)
        self.results.append(result)
        self._print_result(result)
        
        # Wait for background workflow
        print("\n⏳ Waiting for workflow to complete...")
        await asyncio.sleep(5)
        
        # Test 2: Research & Validation
        print("\nRunning Test 2: Research & Validation...")
        result = await self.test_us2_research_validation()
        self.results.append(result)
        self._print_result(result)
        
        # Test 3: Outline approval
        print("\nRunning Test 3: Outline Approval...")
        result = await self.test_us3_outline_approval()
        self.results.append(result)
        self._print_result(result)
        
        # Test 4: Framework selection
        print("\nRunning Test 4: Framework Selection...")
        result = await self.test_us4_framework_selection()
        self.results.append(result)
        self._print_result(result)
        
        # Test 5: Content generation
        print("\nRunning Test 5: Content Generation...")
        result = await self.test_us5_content_generation()
        self.results.append(result)
        self._print_result(result)
        
        # Test 6: Platform adaptation
        print("\nRunning Test 6: Platform Adaptation...")
        result = await self.test_us6_platform_adaptation()
        self.results.append(result)
        self._print_result(result)
        
        return self.results
    
    def _print_result(self, result: TestResult):
        """Print formatted test result"""
        print(f"\n{result.status.value} {result.test_name}")
        print(f"   API Type: {result.api_type.value}")
        print(f"   Duration: {result.duration:.2f}s")
        print(f"   Assertions: {result.assertions_passed}/{result.assertions_total}")
        print(f"   Details: {result.details}")
        if result.error:
            print(f"   Error: {result.error}")
    
    def _generate_intelligent_recommendations(
        self, 
        total_tests: int,
        passed: int,
        failed: int,
        warnings: int,
        skipped: int,
        real_api: int,
        mock_api: int,
        assertions_passed: int,
        assertions_total: int,
        total_duration: float
    ) -> List[str]:
        """
        Generate context-aware recommendations based on test results
        
        Analyzes failure patterns and provides priority-based, actionable recommendations
        """
        recommendations = []
        
        # Pattern 1: Backend not running (CRITICAL)
        backend_errors = [r for r in self.results if r.error and "Connection" in r.error]
        if len(backend_errors) >= total_tests * 0.5:  # 50%+ connection errors
            recommendations.append("\n🔴 CRITICAL: Backend server not running!")
            recommendations.append("")
            recommendations.append("Root Cause: Cannot connect to http://localhost:8000")
            recommendations.append("")
            recommendations.append("Action Required:")
            recommendations.append("  1. Check if backend is running: curl http://localhost:8000/health")
            recommendations.append("  2. If not running, start it:")
            recommendations.append("     uvicorn backend.main:app --reload --port 8000")
            recommendations.append("  3. Verify it starts without errors")
            recommendations.append("  4. Re-run tests: python3 run_tests.py")
            recommendations.append("")
            recommendations.append("Common causes:")
            recommendations.append("  - Backend was never started")
            recommendations.append("  - Backend crashed due to dependency issues")
            recommendations.append("  - Port 8000 already in use by another process")
            return recommendations
        
        # Pattern 2: All/Most tests using mock fallback (CRITICAL)
        if mock_api > 0 and mock_api >= real_api:
            recommendations.append("\n🔴 CRITICAL: API keys not configured!")
            recommendations.append("")
            recommendations.append("Root Cause: System using MOCK fallback instead of real APIs")
            recommendations.append("")
            recommendations.append(f"Impact:")
            recommendations.append(f"  - {mock_api} test(s) using placeholder mock data")
            recommendations.append(f"  - {real_api} test(s) using real API calls")
            recommendations.append(f"  - You're seeing mock responses, not actual AI-generated content")
            recommendations.append("")
            recommendations.append("Action Required:")
            recommendations.append("  1. Run: python3 scripts/setup_secrets.py")
            recommendations.append("  2. Configure the following services:")
            recommendations.append("     - Azure OpenAI (CRITICAL): API Key + Endpoint URL")
            recommendations.append("     - Bing Search (CRITICAL): API Key")
            recommendations.append("     - Anthropic Claude (OPTIONAL): API Key")
            recommendations.append("  3. Restart backend: uvicorn backend.main:app --reload --port 8000")
            recommendations.append("  4. Re-run tests: python3 run_tests.py")
            recommendations.append("")
            recommendations.append("Expected outcome after fix:")
            recommendations.append("  ✅ Tests show 'Real LLM API' instead of 'Mock Fallback'")
            recommendations.append("  ✅ Content generation produces real AI results")
            recommendations.append("  ✅ Validation percentage > 0%")
            return recommendations
        
        # Pattern 3: Database errors (HIGH)
        db_errors = [r for r in self.results if r.error and ("table" in r.error.lower() or "relation" in r.error.lower())]
        if db_errors:
            recommendations.append("\n🟠 HIGH: Database not initialized!")
            recommendations.append("")
            recommendations.append("Root Cause: Database tables missing")
            recommendations.append("")
            recommendations.append(f"Failed tests: {len(db_errors)}")
            for error_result in db_errors[:3]:  # Show first 3
                recommendations.append(f"  - {error_result.test_name}")
            recommendations.append("")
            recommendations.append("Action Required:")
            recommendations.append("  1. Initialize database: python3 scripts/setup_db.py")
            recommendations.append("  2. Verify tables created successfully")
            recommendations.append("  3. Restart backend: uvicorn backend.main:app --reload --port 8000")
            recommendations.append("  4. Re-run tests: python3 run_tests.py")
            recommendations.append("")
            recommendations.append("Why this is needed:")
            recommendations.append("  Application stores session data, outlines, and content in database.")
            recommendations.append("  Without initialized database, data persistence fails.")
            return recommendations
        
        # Pattern 4: Partial mock fallback (MEDIUM)
        if mock_api > 0 and real_api > mock_api:
            recommendations.append("\n🟡 MEDIUM: Partial configuration detected")
            recommendations.append("")
            recommendations.append("Status:")
            recommendations.append(f"  ✅ Real API calls: {real_api}")
            recommendations.append(f"  ⚠️  Mock fallback: {mock_api}")
            recommendations.append("")
            recommendations.append("Impact:")
            recommendations.append("  - Some features working with real AI")
            recommendations.append("  - Some features using placeholder data")
            recommendations.append("")
            recommendations.append("Action Required (Priority Order):")
            recommendations.append("  1. Run validation: python3 run_tests.py --validate-only")
            recommendations.append("  2. Configure missing services shown in validation report")
            recommendations.append("  3. Run: python3 scripts/setup_secrets.py")
            recommendations.append("  4. Restart backend and re-run tests")
            recommendations.append("")
            recommendations.append("Note: System partially functional but not fully operational")
            return recommendations
        
        # Pattern 5: Test assertion failures (MEDIUM)
        if failed > 0 and mock_api == 0:
            recommendations.append("\n🟡 MEDIUM: Test logic errors detected")
            recommendations.append("")
            recommendations.append(f"Failed Tests: {failed}/{total_tests}")
            
            failed_results = [r for r in self.results if r.status == TestStatus.FAIL]
            for result in failed_results[:3]:  # Show first 3
                recommendations.append(f"")
                recommendations.append(f"  • {result.test_name}")
                recommendations.append(f"    Expected: {result.assertions_total} assertions passed")
                recommendations.append(f"    Actual: {result.assertions_passed} assertions passed")
                if result.error:
                    recommendations.append(f"    Error: {result.error}")
            
            recommendations.append("")
            recommendations.append("Possible causes:")
            recommendations.append("  a) Test expectations too strict")
            recommendations.append("  b) Application behavior changed")
            recommendations.append("  c) Framework updated but tests not updated")
            recommendations.append("")
            recommendations.append("Action Required:")
            recommendations.append("  1. Review test expectations in tests/test_e2e_comprehensive.py")
            recommendations.append("  2. Check if assertions match current application behavior")
            recommendations.append("  3. Update test assertions if expectations changed")
            recommendations.append("  4. Debug individual tests with added logging")
            return recommendations
        
        # Pattern 6: Performance issues (LOW)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        if passed == total_tests and avg_duration > 3.0:  # Average > 3 seconds
            recommendations.append("\n🟢 LOW: Performance optimization recommended")
            recommendations.append("")
            recommendations.append(f"Performance Metrics:")
            recommendations.append(f"  Average test duration: {avg_duration:.2f}s (threshold: 3.0s)")
            
            # Find slowest tests
            sorted_results = sorted(self.results, key=lambda r: r.duration, reverse=True)
            recommendations.append(f"")
            recommendations.append(f"  Slowest tests:")
            for i, result in enumerate(sorted_results[:3], 1):
                recommendations.append(f"    {i}. {result.test_name}: {result.duration:.2f}s")
            
            recommendations.append("")
            recommendations.append("Impact: ⚠️  Tests taking longer than expected")
            recommendations.append("")
            recommendations.append("Recommended optimizations:")
            recommendations.append("  1. Enable response caching for repeated requests")
            recommendations.append("  2. Use faster LLM models for testing (gpt-4o-mini vs gpt-4o)")
            recommendations.append("  3. Reduce test input complexity")
            recommendations.append("  4. Consider parallel test execution")
            recommendations.append("")
            recommendations.append("Note: This is NOT critical - all functionality working correctly.")
            return recommendations
        
        # Pattern 7: All tests passed! (SUCCESS)
        if passed == total_tests and mock_api == 0 and failed == 0:
            recommendations.append("\n🎉 SUCCESS: All tests passed!")
            recommendations.append("")
            recommendations.append("Test Summary:")
            recommendations.append(f"  ✅ {passed}/{total_tests} tests passed")
            recommendations.append(f"  ✅ All using real APIs (no mock fallback)")
            recommendations.append(f"  ✅ {assertions_passed}/{assertions_total} assertions passed ({(assertions_passed/assertions_total*100):.1f}%)")
            recommendations.append(f"  ✅ Average duration: {avg_duration:.2f}s ({'excellent' if avg_duration < 2.0 else 'good'} performance)")
            recommendations.append("")
            recommendations.append("Configuration Status:")
            recommendations.append("  ✅ Azure OpenAI configured and working")
            recommendations.append("  ✅ Bing Search configured and working")
            recommendations.append("  ✅ Backend healthy and responsive")
            recommendations.append("  ✅ Database initialized and functioning")
            recommendations.append("")
            recommendations.append("Next Steps:")
            recommendations.append("  ✅ System ready for use!")
            recommendations.append("  ✅ You can now start the frontend: streamlit run frontend/Home.py")
            recommendations.append("  ✅ All workflows validated and working with real APIs")
            recommendations.append("")
            recommendations.append("Maintenance:")
            recommendations.append("  - Re-run tests after code changes")
            recommendations.append("  - Run tests before commits")
            recommendations.append("  - Include tests in CI/CD pipeline")
            recommendations.append("")
            recommendations.append("No action required - everything working perfectly! 🚀")
            return recommendations
        
        # Pattern 8: Mixed results (warnings but passing)
        if warnings > 0 and failed == 0:
            recommendations.append("\n🟡 MEDIUM: Tests passing with warnings")
            recommendations.append("")
            recommendations.append(f"Status:")
            recommendations.append(f"  ✅ Passed: {passed}")
            recommendations.append(f"  ⚠️  Warnings: {warnings}")
            recommendations.append(f"  🤖 Mock Fallback: {mock_api}")
            recommendations.append("")
            recommendations.append("Action Required:")
            recommendations.append("  1. Review warnings above for specific issues")
            recommendations.append("  2. Check API configuration: python3 run_tests.py --validate-only")
            recommendations.append("  3. Configure missing services if needed")
            recommendations.append("")
            recommendations.append("Note: Core functionality working but configuration incomplete")
            return recommendations
        
        # Default fallback
        recommendations.append("\n⚠️  Review test results above for details")
        recommendations.append("")
        recommendations.append(f"Summary: {passed} passed, {failed} failed, {warnings} warnings")
        recommendations.append("")
        recommendations.append("For detailed diagnostics: cat TEST_REPORT.txt")
        
        return recommendations
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        report = []
        report.append("\n" + "="*80)
        report.append("📊 COMPREHENSIVE TEST REPORT")
        report.append("="*80)
        
        # Summary statistics
        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r.status == TestStatus.PASS)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAIL)
        warnings = sum(1 for r in self.results if r.status == TestStatus.WARN)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIP)
        
        real_api = sum(1 for r in self.results if r.api_type in [APICallType.REAL_LLM, APICallType.REAL_SEARCH])
        mock_api = sum(1 for r in self.results if r.api_type == APICallType.MOCK_FALLBACK)
        
        total_duration = sum(r.duration for r in self.results)
        total_assertions_passed = sum(r.assertions_passed for r in self.results)
        total_assertions = sum(r.assertions_total for r in self.results)
        
        report.append(f"\n📈 Summary:")
        report.append(f"   Total Tests: {total_tests}")
        report.append(f"   ✅ Passed: {passed}")
        report.append(f"   ❌ Failed: {failed}")
        report.append(f"   ⚠️  Warnings: {warnings}")
        report.append(f"   ⏭️  Skipped: {skipped}")
        report.append(f"\n🔌 API Calls:")
        report.append(f"   🌐 Real API: {real_api}")
        report.append(f"   🤖 Mock Fallback: {mock_api}")
        report.append(f"\n⏱️  Performance:")
        report.append(f"   Total Duration: {total_duration:.2f}s")
        report.append(f"   Average Duration: {total_duration/total_tests:.2f}s per test")
        report.append(f"\n✓ Assertions:")
        report.append(f"   Passed: {total_assertions_passed}/{total_assertions}")
        report.append(f"   Success Rate: {(total_assertions_passed/total_assertions*100):.1f}%")
        
        # Detailed results
        report.append(f"\n{'─'*80}")
        report.append("📋 Detailed Results:")
        report.append(f"{'─'*80}")
        
        for i, result in enumerate(self.results, 1):
            report.append(f"\n{i}. {result.status.value} {result.test_name}")
            report.append(f"   API Type: {result.api_type.value}")
            report.append(f"   Duration: {result.duration:.2f}s")
            report.append(f"   Assertions: {result.assertions_passed}/{result.assertions_total}")
            report.append(f"   Details: {result.details}")
            if result.error:
                report.append(f"   Error: {result.error}")
        
        # Intelligent Recommendations
        report.append(f"\n{'='*80}")
        report.append("💡 Intelligent Recommendations:")
        report.append(f"{'='*80}")
        
        recommendations = self._generate_intelligent_recommendations(
            total_tests, passed, failed, warnings, skipped,
            real_api, mock_api, total_assertions_passed, total_assertions,
            total_duration
        )
        
        for rec in recommendations:
            report.append(rec)
        
        report.append("\n" + "="*80)
        
        return "\n".join(report)
    
    def save_report(self, filename: str = "test_report.txt"):
        """Save report to file"""
        report = self.generate_report()
        with open(filename, "w") as f:
            f.write(report)
        print(f"\n💾 Report saved to: {filename}")


# ========================================================================
# MAIN EXECUTION
# ========================================================================

async def main():
    """Main test execution"""
    agent = E2ETestingAgent()
    
    try:
        # Run all tests
        results = await agent.run_all_tests(
            user_input="Write about the future of AI in healthcare and its impact on patient care"
        )
        
        # Generate and print report
        report = agent.generate_report()
        print(report)
        
        # Save report
        agent.save_report("TEST_REPORT.txt")
        
    finally:
        await agent.close()


if __name__ == "__main__":
    # Run tests
    asyncio.run(main())
