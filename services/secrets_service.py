"""
Hybrid secrets management service.

Uses OS keychain (keyring library) as primary source.
Falls back to Azure Key Vault if keyring secrets not found.

This provides:
  1. Fast local development (keyring - instant, offline access)
  2. Multi-device sync option (Azure Key Vault - cloud backup)
  3. Flexibility (try local first, cloud second)

Usage:
    from services.secrets_service import SecretsService
    
    secrets_service = SecretsService()
    azure_ai_key = secrets_service.get("azure-ai-key")
    bing_key = secrets_service.get("bing-search-key")
"""

import os
import logging
from typing import Optional
from functools import lru_cache


logger = logging.getLogger(__name__)


class SecretsService:
    """Hybrid secrets management with keyring (primary) and Azure Key Vault (fallback)."""

    SERVICE_NAME = "content-studio"

    def __init__(self):
        """Initialize secrets service."""
        self._keyring_available = self._check_keyring()
        self._keyvault_client = None
        self._keyvault_config = self._load_keyvault_config()

    @staticmethod
    def _check_keyring() -> bool:
        """Check if keyring library is available."""
        try:
            import keyring  # noqa: F401
            logger.info("✓ Keyring library available (OS keychain)")
            return True
        except ImportError:
            logger.warning(
                "⚠ Keyring not installed. Install with: pip install keyring"
            )
            return False

    @staticmethod
    def _load_keyvault_config() -> Optional[dict]:
        """Load Azure Key Vault config from environment or config file."""
        keyvault_name = os.environ.get("AZURE_KEYVAULT_NAME")

        if keyvault_name:
            logger.info(f"✓ Azure Key Vault configured: {keyvault_name}")
            return {
                "name": keyvault_name,
                "url": f"https://{keyvault_name}.vault.azure.net/",
            }

        # Optionally load from config file (if exists)
        config_file = os.path.expanduser("~/.content-studio/config.yaml")
        if os.path.exists(config_file):
            try:
                import yaml

                with open(config_file) as f:
                    config = yaml.safe_load(f) or {}
                    keyvault_name = config.get("key_vault", {}).get("name")

                    if keyvault_name:
                        logger.info(
                            f"✓ Azure Key Vault configured from config: {keyvault_name}"
                        )
                        return {
                            "name": keyvault_name,
                            "url": f"https://{keyvault_name}.vault.azure.net/",
                        }
            except Exception as e:
                logger.debug(f"Could not load Key Vault config from file: {e}")

        logger.info("⊘ Azure Key Vault not configured (will skip fallback)")
        return None

    def _get_from_keyring(self, secret_id: str) -> Optional[str]:
        """Get secret from OS keychain via keyring library."""
        if not self._keyring_available:
            return None

        try:
            import keyring

            secret = keyring.get_password(self.SERVICE_NAME, secret_id)
            if secret:
                logger.debug(f"✓ Retrieved '{secret_id}' from OS keychain")
                return secret
        except Exception as e:
            logger.warning(f"Error retrieving from keyring: {e}")

        return None

    def _get_from_keyvault(self, secret_id: str) -> Optional[str]:
        """Get secret from Azure Key Vault."""
        if not self._keyvault_config:
            return None

        # Lazy-init Key Vault client
        if self._keyvault_client is None:
            self._keyvault_client = self._init_keyvault_client()

        if self._keyvault_client is None:
            return None

        try:
            # Convert snake_case to kebab-case (Key Vault naming convention)
            keyvault_secret_id = secret_id.replace("_", "-")
            secret = self._keyvault_client.get_secret(keyvault_secret_id)
            logger.debug(f"✓ Retrieved '{keyvault_secret_id}' from Azure Key Vault")
            return secret.value
        except Exception as e:
            logger.debug(f"Secret '{secret_id}' not found in Key Vault: {e}")
            return None

    def _init_keyvault_client(self):
        """Initialize Azure Key Vault client."""
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient

            credential = DefaultAzureCredential()
            client = SecretClient(
                vault_url=self._keyvault_config["url"], credential=credential
            )
            logger.info(
                f"✓ Connected to Azure Key Vault: {self._keyvault_config['name']}"
            )
            return client
        except ImportError:
            logger.warning(
                "Azure SDK not installed. Install with: pip install azure-identity azure-keyvault-secrets"
            )
            return None
        except Exception as e:
            logger.warning(f"Failed to connect to Azure Key Vault: {e}")
            return None

    def get(self, secret_id: str, required: bool = True) -> Optional[str]:
        """
        Get a secret from OS keychain (primary) or Azure Key Vault (fallback).

        Args:
            secret_id: Secret identifier (e.g., "azure-ai-key", "anthropic_api_key")
            required: If True, raise error if secret not found

        Returns:
            Secret value, or None if not found and not required

        Raises:
            ValueError: If required=True and secret not found
        """
        # Try keyring first (fast, local, offline)
        secret = self._get_from_keyring(secret_id)
        if secret:
            return secret

        # Fall back to Azure Key Vault (cloud, multi-device sync)
        secret = self._get_from_keyvault(secret_id)
        if secret:
            return secret

        # Not found anywhere
        if required:
            raise ValueError(
                f"Required secret '{secret_id}' not found in keyring or Key Vault. "
                f"Run: python scripts/setup_secrets.py"
            )

        logger.debug(f"Optional secret '{secret_id}' not found")
        return None

    def get_all(self) -> dict:
        """
        Get all configured secrets (for testing/debugging).

        Returns:
            Dictionary of secret_id -> value for all secrets
        """
        secrets = {}
        required_keys = [
            "azure-ai-key",
            "bing-search-key",
        ]
        optional_keys = [
            "anthropic-api-key",
            "github-copilot-token",
            "content-moderator-key",
        ]

        for key_id in required_keys + optional_keys:
            value = self.get(key_id, required=False)
            if value:
                # Mask for security (only show first 6 chars)
                masked = value[:6] + "***" if len(value) > 6 else "***"
                secrets[key_id] = masked

        return secrets

    @lru_cache(maxsize=32)
    def get_cached(self, secret_id: str) -> str:
        """Get secret and cache it (for performance)."""
        return self.get(secret_id, required=True)

    @staticmethod
    def setup_interactive():
        """Run interactive setup (calls setup_secrets.py)."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "scripts/setup_secrets.py"], check=False
        )
        return result.returncode == 0


# Singleton instance (create once, reuse everywhere)
_secrets_service: Optional[SecretsService] = None


def get_secrets_service() -> SecretsService:
    """Get global secrets service instance."""
    global _secrets_service
    if _secrets_service is None:
        _secrets_service = SecretsService()
    return _secrets_service


def init_secrets():
    """Initialize secrets service at app startup."""
    service = get_secrets_service()
    logger.info("🔐 Secrets Service Initialized")
    logger.info(f"   Keyring available: {service._keyring_available}")
    logger.info(f"   Key Vault configured: {service._keyvault_config is not None}")


# Example usage (for testing)
if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Add repo root to path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    logging.basicConfig(level=logging.INFO)

    print("\n" + "=" * 70)
    print("🔐 HYBRID SECRETS SERVICE TEST")
    print("=" * 70)

    service = SecretsService()

    # Test required secrets
    print("\n📦 Required Secrets:")
    try:
        azure_ai_key = service.get("azure-ai-key")
        print(f"✓ azure-ai-key: {azure_ai_key[:10]}...")
    except ValueError as e:
        print(f"❌ {e}")

    try:
        bing_key = service.get("bing-search-key")
        print(f"✓ bing-search-key: {bing_key[:10]}...")
    except ValueError as e:
        print(f"❌ {e}")

    # Test optional secrets
    print("\n📦 Optional Secrets:")
    anthropic_key = service.get("anthropic-api-key", required=False)
    print(f"  anthropic-api-key: {'✓ Found' if anthropic_key else '⊘ Not found'}")

    github_token = service.get("github-copilot-token", required=False)
    print(f"  github-copilot-token: {'✓ Found' if github_token else '⊘ Not found'}")

    # Show all secrets (masked)
    print("\n📋 All Configured Secrets (masked):")
    all_secrets = service.get_all()
    for key, masked_value in all_secrets.items():
        print(f"   {key}: {masked_value}")

    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)
