"""
Cerebras AI client wrapper for the proxy
"""

import os
import time
from typing import List, Dict, Any, Optional, Generator
from cerebras.cloud.sdk import Cerebras
# Cerebras SDK does not have equivalent types to Google AI's Content, Part, etc.
# Remove these imports and adjust code to use Cerebras' actual API
from config.settings import config
from config.constants import SAFETY_SETTINGS

class CerebrasAIClient:
    """Wrapper for Cerebras AI client with configuration management"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Cerebras AI client"""
        if self.api_key:
            self.client = Cerebras(api_key=self.api_key)
        else:
            # Try to get from environment
            api_key = os.getenv("CEREBRAS_API_KEY")
            if api_key:
                self.client = Cerebras(api_key=api_key)
            else:
                raise ValueError("Cerebras API key is required")
        print("Cerebras AI client initialized")
    
    def create_safety_settings(self) -> dict:
        """Create safety settings based on configuration"""
        # Cerebras SDK handles safety settings differently - returning empty dict
        return {}
    
    def create_generation_config(self, temperature: float = None) -> dict:
        """Create generation configuration"""
        return {
            "temperature": temperature if temperature is not None else 0.7,
            "top_p": config.get("top_p", 0.9),
            "top_k": config.get("top_k", 45),
            "max_output_tokens": 20000,
            "response_mime_type": "text/plain",
        }
    
    def prepare_contents(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Convert messages to Cerebras AI format"""
        # Cerebras SDK accepts messages directly without wrapping in Content/Part
        return messages
    
    def generate_content(self, 
                        model: str, 
                        messages: List[Dict[str, str]], 
                        temperature: float = None,
                        stream: bool = False) -> Any:
        """Generate content using Cerebras AI
        
        Args:
            model: Model name
            messages: List of messages
            temperature: Temperature parameter
            stream: Whether to stream response
            
        Returns:
            Response object or generator
        """
        if not self.client:
            raise RuntimeError("Cerebras AI client not initialized")
        
        contents = self.prepare_contents(messages)
        generation_config = self.create_generation_config(temperature)
        
        if stream:
            return self.client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generation_config,
            )
        else:
            return self.client.models.generate_content(
                model=model,
                contents=contents,
                config=generation_config,
            )
    
    def get_available_models(self) -> List[str]:
        """Get list of available Cerebras models"""
        return [
            "llama3-8b",
            "llama3-70b",
            "gemma-2b",
            "gemma-7b",
            "mistral-7b",
            "mixtral-8x7b",
            "granite-20b"
        ]
    
    def validate_model(self, model: str) -> bool:
        """Validate if model is available in Cerebras"""
        return model in self.get_available_models()

# Global client instance
cerebras_ai_client = None

def initialize_cerebras_ai_client(api_key: str = None) -> CerebrasAIClient:
    """Initialize global Cerebras AI client"""
    global cerebras_ai_client
    cerebras_ai_client = CerebrasAIClient(api_key)
    return cerebras_ai_client

def get_cerebras_ai_client() -> CerebrasAIClient:
    """Get global Cerebras AI client"""
    if cerebras_ai_client is None:
        raise RuntimeError("Cerebras AI client not initialized")
    return cerebras_ai_client
