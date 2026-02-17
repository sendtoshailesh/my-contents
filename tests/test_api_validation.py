"""
API Key Validation Utility
===========================

Validates that all required API keys are configured correctly.
Helps diagnose mock vs real API issues.

Software Testing Principles Applied:
- Dependency validation (pre-condition testing)
- Environment configuration testing
- Fail-fast strategy
- Clear error messaging
"""

import os
import sys
from typing import Dict, List, Tuple
from enum import Enum
from dataclasses import dataclass

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from services.secrets_service import get_secret
except ImportError:
    print("⚠️  Warning: Could not import secrets_service")
    get_secret = None


class ValidationStatus(Enum):
    """Validation result status"""
    PASS = "✅ CONFIGURED"
    FAIL = "❌ MISSING"
    WARN = "⚠️  INVALID"


@dataclass
class APIKeyValidation:
    """Result of API key validation"""
    service_name: str
    key_name: str
    status: ValidationStatus
    message: str
    is_critical: bool


class APIKeyValidator:
    """
    Validates API key configuration
    
    Checks for:
    1. Azure OpenAI credentials
    2. Anthropic API key
    3. OpenAI API key
    4. Bing Search API key
    """
    
    def __init__(self):
        self.results: List[APIKeyValidation] = []
        
    def validate_azure_openai(self) -> APIKeyValidation:
        """Validate Azure OpenAI configuration"""
        service_name = "Azure OpenAI"
        
        # Check for Azure credentials
        azure_key = None
        azure_endpoint = None
        
        if get_secret:
            try:
                azure_key = get_secret("AZURE_OPENAI_API_KEY")
                azure_endpoint = get_secret("AZURE_OPENAI_ENDPOINT")
            except Exception as e:
                pass
        
        # Also check environment variables
        if not azure_key:
            azure_key = os.environ.get("AZURE_OPENAI_API_KEY")
        if not azure_endpoint:
            azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        
        if azure_key and azure_endpoint:
            # Validate format
            if azure_endpoint.startswith("https://") and len(azure_key) > 20:
                return APIKeyValidation(
                    service_name=service_name,
                    key_name="AZURE_OPENAI_API_KEY",
                    status=ValidationStatus.PASS,
                    message=f"Configured: {azure_endpoint[:30]}...",
                    is_critical=True
                )
            else:
                return APIKeyValidation(
                    service_name=service_name,
                    key_name="AZURE_OPENAI_API_KEY",
                    status=ValidationStatus.WARN,
                    message="Invalid format - check endpoint URL and key",
                    is_critical=True
                )
        elif azure_key or azure_endpoint:
            return APIKeyValidation(
                service_name=service_name,
                key_name="AZURE_OPENAI_API_KEY",
                status=ValidationStatus.WARN,
                message="Partial configuration - need both key and endpoint",
                is_critical=True
            )
        else:
            return APIKeyValidation(
                service_name=service_name,
                key_name="AZURE_OPENAI_API_KEY",
                status=ValidationStatus.FAIL,
                message="Not configured - will use mock fallback",
                is_critical=True
            )
    
    def validate_anthropic(self) -> APIKeyValidation:
        """Validate Anthropic API key"""
        service_name = "Anthropic Claude"
        
        api_key = None
        if get_secret:
            try:
                api_key = get_secret("ANTHROPIC_API_KEY")
            except:
                pass
        
        if not api_key:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
        
        if api_key:
            if api_key.startswith("sk-ant-") and len(api_key) > 30:
                return APIKeyValidation(
                    service_name=service_name,
                    key_name="ANTHROPIC_API_KEY",
                    status=ValidationStatus.PASS,
                    message=f"Configured: {api_key[:15]}...",
                    is_critical=False
                )
            else:
                return APIKeyValidation(
                    service_name=service_name,
                    key_name="ANTHROPIC_API_KEY",
                    status=ValidationStatus.WARN,
                    message="Invalid format - should start with 'sk-ant-'",
                    is_critical=False
                )
        else:
            return APIKeyValidation(
                service_name=service_name,
                key_name="ANTHROPIC_API_KEY",
                status=ValidationStatus.FAIL,
                message="Not configured (optional fallback)",
                is_critical=False
            )
    
    def validate_openai(self) -> APIKeyValidation:
        """Validate OpenAI API key"""
        service_name = "OpenAI GPT"
        
        api_key = None
        if get_secret:
            try:
                api_key = get_secret("OPENAI_API_KEY")
            except:
                pass
        
        if not api_key:
            api_key = os.environ.get("OPENAI_API_KEY")
        
        if api_key:
            if api_key.startswith("sk-") and len(api_key) > 30:
                return APIKeyValidation(
                    service_name=service_name,
                    key_name="OPENAI_API_KEY",
                    status=ValidationStatus.PASS,
                    message=f"Configured: {api_key[:15]}...",
                    is_critical=False
                )
            else:
                return APIKeyValidation(
                    service_name=service_name,
                    key_name="OPENAI_API_KEY",
                    status=ValidationStatus.WARN,
                    message="Invalid format - should start with 'sk-'",
                    is_critical=False
                )
        else:
            return APIKeyValidation(
                service_name=service_name,
                key_name="OPENAI_API_KEY",
                status=ValidationStatus.FAIL,
                message="Not configured (optional fallback)",
                is_critical=False
            )
    
    def validate_bing_search(self) -> APIKeyValidation:
        """Validate Bing Search API key"""
        service_name = "Bing Search"
        
        api_key = None
        if get_secret:
            try:
                api_key = get_secret("BING_SEARCH_API_KEY")
            except:
                pass
        
        if not api_key:
            api_key = os.environ.get("BING_SEARCH_API_KEY")
        
        if api_key:
            if len(api_key) == 32:  # Bing keys are typically 32 chars
                return APIKeyValidation(
                    service_name=service_name,
                    key_name="BING_SEARCH_API_KEY",
                    status=ValidationStatus.PASS,
                    message=f"Configured: {api_key[:8]}...",
                    is_critical=True
                )
            else:
                return APIKeyValidation(
                    service_name=service_name,
                    key_name="BING_SEARCH_API_KEY",
                    status=ValidationStatus.WARN,
                    message="Invalid format - check key length",
                    is_critical=True
                )
        else:
            return APIKeyValidation(
                service_name=service_name,
                key_name="BING_SEARCH_API_KEY",
                status=ValidationStatus.FAIL,
                message="Not configured - research validation will fail",
                is_critical=True
            )
    
    def validate_all(self) -> List[APIKeyValidation]:
        """Run all validations"""
        print("\n" + "="*80)
        print("🔑 API KEY VALIDATION")
        print("="*80 + "\n")
        
        # Run validations
        self.results = [
            self.validate_azure_openai(),
            self.validate_anthropic(),
            self.validate_openai(),
            self.validate_bing_search()
        ]
        
        # Print results
        for result in self.results:
            critical_marker = "⚡ CRITICAL" if result.is_critical else "  OPTIONAL"
            print(f"{result.status.value} {result.service_name} {critical_marker}")
            print(f"   Key: {result.key_name}")
            print(f"   {result.message}\n")
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate validation report"""
        report = []
        report.append("\n" + "="*80)
        report.append("📊 API KEY VALIDATION REPORT")
        report.append("="*80)
        
        # Count results
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == ValidationStatus.PASS)
        failed = sum(1 for r in self.results if r.status == ValidationStatus.FAIL)
        warnings = sum(1 for r in self.results if r.status == ValidationStatus.WARN)
        
        critical_failed = sum(1 for r in self.results if r.status == ValidationStatus.FAIL and r.is_critical)
        
        report.append(f"\n📈 Summary:")
        report.append(f"   Total Services: {total}")
        report.append(f"   ✅ Configured: {passed}")
        report.append(f"   ❌ Missing: {failed}")
        report.append(f"   ⚠️  Invalid: {warnings}")
        report.append(f"   ⚡ Critical Missing: {critical_failed}")
        
        # Detailed results
        report.append(f"\n{'─'*80}")
        report.append("📋 Detailed Results:")
        report.append(f"{'─'*80}")
        
        for result in self.results:
            critical = "⚡ CRITICAL" if result.is_critical else "OPTIONAL"
            report.append(f"\n{result.status.value} {result.service_name} ({critical})")
            report.append(f"   Key: {result.key_name}")
            report.append(f"   {result.message}")
        
        # Recommendations
        report.append(f"\n{'='*80}")
        report.append("💡 Recommendations:")
        report.append(f"{'='*80}")
        
        if critical_failed > 0:
            report.append("\n⚠️  CRITICAL: Required API keys are missing!")
            report.append("   System will use MOCK fallback - real functionality unavailable.")
            report.append("\n   📝 Setup Instructions:")
            report.append("   1. Run: python scripts/setup_secrets.py")
            report.append("   2. Follow prompts to configure API keys")
            report.append("   3. Restart backend: uvicorn backend.main:app --reload --port 8000")
            report.append("   4. Re-run tests: python tests/test_e2e_comprehensive.py")
            
            for result in self.results:
                if result.status == ValidationStatus.FAIL and result.is_critical:
                    report.append(f"\n   ❌ Missing: {result.service_name}")
                    report.append(f"      Set: {result.key_name}")
        
        if failed > 0 and critical_failed == 0:
            report.append("\n✅ Critical APIs configured - optional fallbacks missing")
            report.append("   System will work but with reduced capabilities")
        
        if passed == total:
            report.append("\n🎉 All API keys configured correctly!")
            report.append("   System ready for full functionality testing")
        
        report.append("\n" + "="*80)
        
        return "\n".join(report)
    
    def is_ready_for_testing(self) -> bool:
        """Check if system is ready for real API testing"""
        critical_failed = sum(
            1 for r in self.results 
            if r.status == ValidationStatus.FAIL and r.is_critical
        )
        return critical_failed == 0


def main():
    """Main validation execution"""
    validator = APIKeyValidator()
    
    # Run validations
    results = validator.validate_all()
    
    # Generate report
    report = validator.generate_report()
    print(report)
    
    # Save report
    with open("API_KEY_VALIDATION_REPORT.txt", "w") as f:
        f.write(report)
    print(f"\n💾 Report saved to: API_KEY_VALIDATION_REPORT.txt")
    
    # Return exit code
    if validator.is_ready_for_testing():
        print("\n✅ System ready for testing!")
        return 0
    else:
        print("\n❌ System NOT ready - configure API keys first")
        return 1


if __name__ == "__main__":
    exit(main())
