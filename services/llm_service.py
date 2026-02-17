"""
LLM Service with Multi-Model Routing

Routes LLM requests to optimal models based on task type to balance cost and quality.

Supported Providers:
  - Azure AI Foundry (GPT-4 Turbo, Llama 3.1, Mistral Large)
  - Anthropic API (Claude 3.5 Sonnet)
  - GitHub Copilot (Codex)
  - OpenAI API (fallback)

Usage:
    from services.llm_service import ModelRouter
    
    router = ModelRouter()
    response = router.call(
        task_type='classification',
        prompt='Extract topics from this text...'
    )
"""

import time
import logging
import os
from typing import Optional, Dict, Any
from functools import lru_cache

from services.secrets_service import get_secrets_service

# Initialize logger
logger = logging.getLogger("backend.services.llm")


class ModelRouter:
    """Routes LLM requests to optimal model based on task type."""

    # Model mappings for each task type (T012)
    TASK_TO_MODEL = {
        "classification": "azure-gpt4o-mini",  # Cost-effective for topic extraction, platform formatting
        "reasoning": "azure-gpt4o",  # Complex reasoning, outline generation, content synthesis
        "creative": "azure-gpt4o",  # Creative content generation, storytelling
        "structured": "azure-gpt4o-mini",  # Structured output, fact validation, JSON parsing
        "code": "github-copilot",  # Code generation
        "validation": "azure-gpt4o-mini",  # Fact validation, structured validation
    }

    # Temperature configuration by task type (T013)
    TASK_TO_TEMPERATURE = {
        "classification": 0.3,  # Factual tasks
        "validation": 0.3,  # Factual tasks
        "structured": 0.3,  # Factual tasks
        "reasoning": 0.7,  # Creative/complex reasoning
        "creative": 0.7,  # Creative content
        "code": 0.2,  # Code generation
    }

    # Fallback chain for resilience
    FALLBACK_CHAIN = {
        "azure-gpt4o-mini": "azure-gpt4o",
        "azure-gpt4o": "openai-gpt4",
        "azure-llama-3.1": "azure-gpt4o",
        "azure-gpt4-turbo": "openai-gpt4",
        "azure-mistral-large": "azure-gpt4o",
        "anthropic-claude-3.5": "azure-gpt4o",
        "github-copilot": "azure-gpt4o",
        "openai-gpt4": None,  # Last resort
    }

    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0  # Initial delay in seconds
    RETRY_BACKOFF = 2.0  # Exponential backoff multiplier

    def __init__(self):
        """Initialize ModelRouter with API clients for all providers."""
        self.secrets_service = get_secrets_service()
        self._clients = {}
        
        logger.info("🤖 Initializing ModelRouter...")
        
        # Initialize Azure OpenAI client
        self._init_azure_openai()
        
        # Initialize Anthropic client
        self._init_anthropic()
        
        # Initialize OpenAI client (fallback)
        self._init_openai()
        
        # Initialize GitHub Copilot client (optional)
        self._init_github_copilot()
        
        logger.info(f"✓ ModelRouter initialized with {len(self._clients)} providers")

    def _init_azure_openai(self):
        """Initialize Azure OpenAI client for GPT-4, Llama, Mistral."""
        try:
            from openai import AzureOpenAI
            from azure.identity import DefaultAzureCredential, get_bearer_token_provider
            
            # Get Azure OpenAI credentials
            endpoint = self.secrets_service.get("azure-openai-endpoint", required=False)
            api_key = self.secrets_service.get("azure-ai-key", required=False)
            use_aad = os.environ.get("AZURE_OPENAI_USE_AAD", "").lower() in ["1", "true", "yes"]
            
            if not endpoint or not api_key:
                if not endpoint:
                    logger.warning("⊘ Azure OpenAI endpoint not found - skipping")
                    return
                use_aad = True
            
            # Initialize client
            if use_aad:
                credential = DefaultAzureCredential()
                token_provider = get_bearer_token_provider(
                    credential, "https://cognitiveservices.azure.com/.default"
                )
                self._clients["azure"] = AzureOpenAI(
                    azure_endpoint=endpoint,
                    azure_ad_token_provider=token_provider,
                    api_version="2024-02-01"
                )
                logger.info("✓ Azure OpenAI client initialized (Azure AD auth)")
            else:
                self._clients["azure"] = AzureOpenAI(
                    azure_endpoint=endpoint,
                    api_key=api_key,
                    api_version="2024-02-01"
                )
                logger.info("✓ Azure OpenAI client initialized (API key auth)")
            
            logger.info("✓ Azure OpenAI client ready")
            
        except ImportError:
            logger.warning("⊘ openai library not installed - Azure OpenAI unavailable")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Azure OpenAI: {e}")

    def _init_anthropic(self):
        """Initialize Anthropic client for Claude 3.5."""
        try:
            from anthropic import Anthropic
            
            # Get Anthropic API key
            api_key = self.secrets_service.get("anthropic-api-key", required=False)
            
            if not api_key:
                logger.warning("⊘ Anthropic API key not found - skipping")
                return
            
            # Initialize client
            self._clients["anthropic"] = Anthropic(api_key=api_key)
            
            logger.info("✓ Anthropic client initialized (Claude 3.5)")
            
        except ImportError:
            logger.warning("⊘ anthropic library not installed - Anthropic unavailable")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Anthropic: {e}")

    def _init_openai(self):
        """Initialize OpenAI client (fallback)."""
        try:
            from openai import OpenAI
            
            # Get OpenAI API key
            api_key = self.secrets_service.get("openai-api-key", required=False)
            
            if not api_key:
                logger.warning("⊘ OpenAI API key not found - skipping")
                return
            
            # Initialize client
            self._clients["openai"] = OpenAI(api_key=api_key)
            
            logger.info("✓ OpenAI client initialized (GPT-4 fallback)")
            
        except ImportError:
            logger.warning("⊘ openai library not installed - OpenAI unavailable")
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI: {e}")

    def _init_github_copilot(self):
        """Initialize GitHub Copilot client (optional)."""
        try:
            # GitHub Copilot integration would go here
            # Currently not available via standard pip package
            # Placeholder for future implementation
            
            github_token = self.secrets_service.get("github-copilot-token", required=False)
            
            if not github_token:
                logger.warning("⊘ GitHub Copilot token not found - skipping")
                return
            
            # TODO: Initialize GitHub Copilot client when available
            # self._clients["github-copilot"] = GitHubCopilot(token=github_token)
            
            logger.info("⊘ GitHub Copilot integration not yet implemented")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize GitHub Copilot: {e}")

    def get_model_for_task(self, task_type: str) -> str:
        """
        Return model name for given task type.
        
        Args:
            task_type: One of 'classification', 'reasoning', 'creative', 'structured', 'code', 'validation'
        
        Returns:
            Model identifier string
        """
        model = self.TASK_TO_MODEL.get(task_type, "azure-gpt4-turbo")
        logger.debug(f"Task '{task_type}' → Model '{model}'")
        return model

    def get_temperature_for_task(self, task_type: str) -> float:
        """
        Return optimal temperature for task type.
        
        Args:
            task_type: Task type identifier
        
        Returns:
            Temperature value (0.0-1.0)
        """
        temp = self.TASK_TO_TEMPERATURE.get(task_type, 0.7)
        logger.debug(f"Task '{task_type}' → Temperature {temp}")
        return temp

    def call(
        self,
        task_type: str,
        prompt: str,
        **kwargs
    ) -> str:
        """
        Route to appropriate model based on task_type with retry logic.
        
        Args:
            task_type: One of 'classification', 'reasoning', 'creative', 'structured', 'code', 'validation'
            prompt: User prompt
            **kwargs: Additional model parameters (temperature, max_tokens, etc.)
        
        Returns:
            Model response text
        
        Raises:
            Exception: If all retries and fallbacks fail
        """
        # Determine model and temperature
        model = self.get_model_for_task(task_type)
        temperature = kwargs.pop("temperature", self.get_temperature_for_task(task_type))
        max_tokens = kwargs.pop("max_tokens", 2048)
        
        logger.info(f"🎯 Routing task '{task_type}' to model '{model}' (temp={temperature})")
        
        # Try primary model with retries
        try:
            return self._call_with_retry(
                model=model,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        except Exception as primary_error:
            logger.warning(f"⚠ Primary model '{model}' failed: {primary_error}")
            
            # Try fallback chain
            fallback_model = self.FALLBACK_CHAIN.get(model)
            if fallback_model:
                logger.info(f"🔄 Attempting fallback to '{fallback_model}'")
                try:
                    return self._call_with_retry(
                        model=fallback_model,
                        prompt=prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **kwargs
                    )
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback model '{fallback_model}' also failed: {fallback_error}")
                    raise Exception(
                        f"Both primary ({model}) and fallback ({fallback_model}) failed. "
                        f"Primary: {primary_error}. Fallback: {fallback_error}"
                    )
            else:
                # No fallback available
                raise primary_error

    def _call_with_retry(
        self,
        model: str,
        prompt: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """
        Call model with exponential backoff retry logic.
        
        Args:
            model: Model identifier
            prompt: User prompt
            temperature: Temperature parameter
            max_tokens: Max tokens to generate
            **kwargs: Additional parameters
        
        Returns:
            Model response text
        """
        last_exception = None
        delay = self.RETRY_DELAY
        
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                logger.debug(f"Attempt {attempt}/{self.MAX_RETRIES} for model '{model}'")
                
                response = self._call_model(
                    model=model,
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                
                logger.info(f"✓ Model '{model}' responded successfully")
                return response
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt} failed: {e}")
                
                if attempt < self.MAX_RETRIES:
                    logger.info(f"Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    delay *= self.RETRY_BACKOFF
        
        # All retries exhausted
        raise Exception(f"Model '{model}' failed after {self.MAX_RETRIES} retries: {last_exception}")

    def _call_model(
        self,
        model: str,
        prompt: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """
        Call specific model provider.
        
        Args:
            model: Model identifier (e.g., 'azure-gpt4-turbo', 'anthropic-claude-3.5')
            prompt: User prompt
            temperature: Temperature parameter
            max_tokens: Max tokens to generate
            **kwargs: Additional parameters
        
        Returns:
            Model response text
        """
        # Route to appropriate provider
        if model.startswith("azure-"):
            return self._call_azure_openai(model, prompt, temperature, max_tokens, **kwargs)
        elif model.startswith("anthropic-"):
            return self._call_anthropic(model, prompt, temperature, max_tokens, **kwargs)
        elif model.startswith("openai-"):
            return self._call_openai(model, prompt, temperature, max_tokens, **kwargs)
        elif model.startswith("github-"):
            return self._call_github_copilot(model, prompt, temperature, max_tokens, **kwargs)
        else:
            raise ValueError(f"Unknown model provider: {model}")

    def _call_azure_openai(
        self,
        model: str,
        prompt: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Call Azure OpenAI API."""
        if "azure" not in self._clients:
            raise Exception("Azure OpenAI client not initialized")
        
        client = self._clients["azure"]
        
        # Map model to Azure deployment name
        deployment_map = {
            "azure-gpt4o": "gpt-4o",
            "azure-gpt4o-mini": "gpt-4o-mini",
            "azure-gpt4-turbo": "gpt-4-turbo",
            "azure-llama-3.1": "llama-3.1-405b-instruct",
            "azure-mistral-large": "mistral-large",
        }
        
        deployment = deployment_map.get(model)
        if not deployment:
            raise ValueError(f"Unknown Azure model: {model}")
        
        # Make API call
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        return response.choices[0].message.content

    def _call_anthropic(
        self,
        model: str,
        prompt: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Call Anthropic API."""
        if "anthropic" not in self._clients:
            raise Exception("Anthropic client not initialized")
        
        client = self._clients["anthropic"]
        
        # Map model to Anthropic model name
        model_map = {
            "anthropic-claude-3.5": "claude-3-5-sonnet-20241022",
        }
        
        anthropic_model = model_map.get(model)
        if not anthropic_model:
            raise ValueError(f"Unknown Anthropic model: {model}")
        
        # Make API call
        response = client.messages.create(
            model=anthropic_model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "user", "content": prompt}
            ],
            **kwargs
        )
        
        return response.content[0].text

    def _call_openai(
        self,
        model: str,
        prompt: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Call OpenAI API (fallback)."""
        if "openai" not in self._clients:
            raise Exception("OpenAI client not initialized")
        
        client = self._clients["openai"]
        
        # Map model to OpenAI model name
        model_map = {
            "openai-gpt4": "gpt-4-turbo-preview",
        }
        
        openai_model = model_map.get(model, "gpt-4-turbo-preview")
        
        # Make API call
        response = client.chat.completions.create(
            model=openai_model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        return response.choices[0].message.content

    def _call_github_copilot(
        self,
        model: str,
        prompt: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Call GitHub Copilot API (placeholder)."""
        # GitHub Copilot integration not yet available
        # Fallback to Azure GPT-4 for code tasks
        logger.warning("GitHub Copilot not available, falling back to Azure GPT-4")
        return self._call_azure_openai(
            "azure-gpt4-turbo",
            prompt,
            temperature,
            max_tokens,
            **kwargs
        )


# Singleton instance
_model_router: Optional[ModelRouter] = None


def get_model_router() -> ModelRouter:
    """Get global ModelRouter instance."""
    global _model_router
    if _model_router is None:
        _model_router = ModelRouter()
    return _model_router


def get_llm_service() -> ModelRouter:
    """
    Get LLM service instance (alias for get_model_router).
    
    Returns:
        ModelRouter: LLM router instance
    """
    return get_model_router()


# Example usage and testing
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Add repo root to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "=" * 70)
    print("🤖 LLM SERVICE TEST")
    print("=" * 70)
    
    # Initialize router
    router = ModelRouter()
    
    # Test 1: Classification task
    print("\n📊 Test 1: Classification Task (Llama 3.1)")
    print("-" * 70)
    try:
        response = router.call(
            task_type="classification",
            prompt="Extract the main topics from this text: 'Python is a great programming language for data science and machine learning.'"
        )
        print(f"✓ Response: {response[:200]}...")
    except Exception as e:
        print(f"❌ Classification test failed: {e}")
    
    # Test 2: Reasoning task
    print("\n🧠 Test 2: Reasoning Task (GPT-4 Turbo)")
    print("-" * 70)
    try:
        response = router.call(
            task_type="reasoning",
            prompt="Explain why multi-model routing is beneficial for LLM applications."
        )
        print(f"✓ Response: {response[:200]}...")
    except Exception as e:
        print(f"❌ Reasoning test failed: {e}")
    
    # Test 3: Structured output task
    print("\n📋 Test 3: Structured Output (Claude 3.5)")
    print("-" * 70)
    try:
        response = router.call(
            task_type="structured",
            prompt='Return a JSON object with keys "name", "age", and "occupation" for a sample person.'
        )
        print(f"✓ Response: {response[:200]}...")
    except Exception as e:
        print(f"❌ Structured output test failed: {e}")
    
    # Show model routing table
    print("\n" + "=" * 70)
    print("📋 MODEL ROUTING TABLE")
    print("=" * 70)
    for task, model in router.TASK_TO_MODEL.items():
        temp = router.TASK_TO_TEMPERATURE.get(task, 0.7)
        print(f"  {task:15s} → {model:25s} (temp={temp})")
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)
