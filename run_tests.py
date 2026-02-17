#!/usr/bin/env python3
"""
Quick Test Runner
==================

Runs comprehensive test suite and validates API configuration.
Provides clear pass/fail results with actionable recommendations.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --validate-only    # Only validate API keys
    python run_tests.py --e2e-only         # Only run E2E tests
"""

import asyncio
import argparse
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tests.test_api_validation import APIKeyValidator
from tests.test_e2e_comprehensive import E2ETestingAgent


def print_banner(text: str):
    """Print formatted banner"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")


async def run_validation_tests() -> bool:
    """
    Run API key validation tests
    Returns True if all critical APIs configured
    """
    print_banner("🔑 STEP 1: API KEY VALIDATION")
    
    validator = APIKeyValidator()
    validator.validate_all()
    
    report = validator.generate_report()
    print(report)
    
    # Save report
    with open("API_KEY_VALIDATION_REPORT.txt", "w") as f:
        f.write(report)
    
    return validator.is_ready_for_testing()


async def run_e2e_tests() -> bool:
    """
    Run comprehensive E2E tests
    Returns True if all tests pass
    """
    print_banner("🧪 STEP 2: END-TO-END WORKFLOW TESTS")
    
    agent = E2ETestingAgent()
    
    try:
        # Run all tests
        results = await agent.run_all_tests(
            user_input="Write about the future of AI in healthcare and its impact on patient care"
        )
        
        # Generate report
        report = agent.generate_report()
        print(report)
        
        # Save report
        agent.save_report("TEST_REPORT.txt")
        
        # Check if all passed
        all_passed = all(
            r.status.value == "✅ PASS" 
            for r in results
        )
        
        # Check for mock fallbacks
        has_mocks = any(
            r.api_type.value == "Mock Fallback"
            for r in results
        )
        
        if has_mocks:
            print("\n⚠️  WARNING: Some tests used MOCK fallback instead of real APIs")
            print("   This means API keys are not configured correctly.")
            return False
        
        return all_passed
        
    finally:
        await agent.close()


async def run_all_tests():
    """Run complete test suite"""
    print_banner("🚀 COMPREHENSIVE TEST SUITE")
    print("This will validate API keys and run end-to-end workflow tests.")
    print("="*80)
    
    # Step 1: Validate API keys
    api_ready = await run_validation_tests()
    
    if not api_ready:
        print("\n" + "="*80)
        print("⚠️  CRITICAL: API keys not configured!")
        print("="*80)
        print("\n❌ Cannot proceed with E2E tests - system will use mock fallback")
        print("\n📝 Action Required:")
        print("   1. Run: python scripts/setup_secrets.py")
        print("   2. Configure your API keys (Azure OpenAI, Bing Search)")
        print("   3. Restart backend: uvicorn backend.main:app --reload --port 8000")
        print("   4. Re-run this test: python run_tests.py")
        print("\n" + "="*80)
        return False
    
    # Step 2: Run E2E tests
    print("\n✅ API keys configured - proceeding with E2E tests...\n")
    tests_passed = await run_e2e_tests()
    
    # Final summary
    print("\n" + "="*80)
    print("📊 FINAL TEST SUMMARY")
    print("="*80)
    
    if tests_passed:
        print("\n🎉 SUCCESS: All tests passed!")
        print("   ✅ API keys configured correctly")
        print("   ✅ Backend functioning properly")
        print("   ✅ Workflow executing with real APIs")
        print("   ✅ All user stories validated")
        print("\n" + "="*80)
        return True
    else:
        print("\n❌ FAILURE: Some tests failed")
        print("   Review reports above for details")
        print("\n📊 Reports Generated:")
        print("   - API_KEY_VALIDATION_REPORT.txt")
        print("   - TEST_REPORT.txt")
        print("\n" + "="*80)
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run comprehensive test suite for content generation system"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only run API key validation"
    )
    parser.add_argument(
        "--e2e-only",
        action="store_true",
        help="Only run E2E tests (skip validation)"
    )
    
    args = parser.parse_args()
    
    # Run appropriate tests
    if args.validate_only:
        success = asyncio.run(run_validation_tests())
    elif args.e2e_only:
        success = asyncio.run(run_e2e_tests())
    else:
        success = asyncio.run(run_all_tests())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
