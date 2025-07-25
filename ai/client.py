"""
Google AI client wrapper for the proxy
"""

import time
from typing import List, Dict, Any, Optional, Generator
from google import genai
from google.genai.types import (
    Content, Part, GenerateContentConfig, 
    HarmCategory, SafetySetting, HarmBlockThreshold
)
from config.settings import config
from config.constants import SAFETY_SETTINGS

class GoogleAIClient:
    """Wrapper for Google AI client with configuration management"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Google AI client"""
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            # Try to get from environment
            import os
            api_key = os.getenv("GOOGLE_AI_API_KEY")
            if api_key:
                self.client = genai.Client(api_key=api_key)
            else:
                raise ValueError("Google AI API key is required")
        print("Google AI client initialized")
    
    def create_safety_settings(self) -> List[SafetySetting]:
        """Create safety settings based on configuration"""
        return [
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=HarmBlockThreshold.BLOCK_NONE,
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=HarmBlockThreshold.BLOCK_NONE,
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=HarmBlockThreshold.BLOCK_NONE,
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=HarmBlockThreshold.BLOCK_NONE,
            ),
        ]
    
    def create_generation_config(self, temperature: float = None) -> GenerateContentConfig:
        """Create generation configuration"""
        return GenerateContentConfig(
            temperature=temperature if temperature is not None else 0.7,
            top_p=config.get("top_p", 0.9),
            top_k=config.get("top_k", 45),
            max_output_tokens=20000,
            safety_settings=self.create_safety_settings(),
            response_mime_type="text/plain",
        )
    
    def prepare_contents(self, messages: List[Dict[str, str]]) -> List[Content]:
        """Convert messages to Google AI format"""
        contents = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                # System messages are treated as user messages
                contents.append(Content(role="user", parts=[Part(text=content)]))
            elif role == "assistant":
                contents.append(Content(role="model", parts=[Part(text=content)]))
            else:
                contents.append(Content(role=role, parts=[Part(text=content)]))
        
        return contents
    
    def generate_content(self, 
                        model: str, 
                        messages: List[Dict[str, str]], 
                        temperature: float = None,
                        stream: bool = False) -> Any:
        """
        Generate content using Google AI
        
        Args:
            model: Model name
            messages: List of messages
            temperature: Temperature parameter
            stream: Whether to stream response
            
        Returns:
            Response object or generator
        """
        if not self.client:
            raise RuntimeError("Google AI client not initialized")
        
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
        """Get list of available models"""
        return [
            "gemini-2.5-flash",
            "gemini-2.0-flash-exp",
            "gemini-2.5-pro",
            "gemini-1.5-flash"
        ]
    
    def validate_model(self, model: str) -> bool:
        """Validate if model is available"""
        return model in self.get_available_models()

# Global client instance
google_ai_client = None

def initialize_google_ai_client(api_key: str = None) -> GoogleAIClient:
    """Initialize global Google AI client"""
    global google_ai_client
    google_ai_client = GoogleAIClient(api_key)
    return google_ai_client

def get_google_ai_client() -> GoogleAIClient:
    """Get global Google AI client"""
    if google_ai_client is None:
        raise RuntimeError("Google AI client not initialized")
    return google_ai_client
