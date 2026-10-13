"""
Deterministic local mock response adapter with identifier checks.
"""
from typing import Dict, Any, Optional
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "He Slide Harmonizer Agent"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return f"[{self.system_name} local mock]: No scientific verification or LLM inference performed. Received: '{prompt[:60]}...'."


class LLMFactory:
    """Selects the deterministic local mock. External providers are not implemented."""

    @staticmethod
    def create(provider: str = "mock", system_name: str = "He Slide Harmonizer Agent"):
        prov = str(provider).lower()
        if prov in ["mock", "deterministic", "test"]:
            return MockLLM(system_name)
        raise ValueError("Only the local deterministic mock provider is implemented.")
