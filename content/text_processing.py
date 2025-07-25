"""
Text processing utilities for content manipulation and formatting
"""

import re
import random
from typing import List, Tuple
from config.settings import config

def clean_response_text(text: str, prefill_text: str = "") -> str:
    """
    Clean and format response text
    
    Args:
        text: Raw response text
        prefill_text: Optional prefill text to prepend
        
    Returns:
        Cleaned and formatted text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove any potential harmful patterns
    text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<iframe.*?</iframe>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Add prefill text if provided
    if prefill_text and prefill_text.strip():
        text = prefill_text + text
    
    return text

def ensure_markdown_formatting(text: str) -> str:
    """
    Ensure proper markdown formatting in text
    
    Args:
        text: Input text
        
    Returns:
        Text with improved markdown formatting
    """
    if not text:
        return ""
    
    # Fix common markdown issues
    text = re.sub(r'\*\*(.*?)\*\*', r'**\1**', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'*\1*', text)  # Italic
    text = re.sub(r'__(.*?)__', r'**\1**', text)  # Bold alternative
    
    # Ensure proper paragraph breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Fix code blocks
    text = re.sub(r'```\s*\n\s*```', '```\n\n```', text)
    
    return text.strip()

def check_forbidden_words(text: str, forbidden_words: List[str]) -> Tuple[bool, List[str]]:
    """
    Check if text contains forbidden words
    
    Args:
        text: Text to check
        forbidden_words: List of forbidden words
        
    Returns:
        Tuple of (has_forbidden_words, list_of_found_words)
    """
    if not text or not forbidden_words:
        return False, []
    
    text_lower = text.lower()
    found_words = []
    
    for word in forbidden_words:
        if word.lower() in text_lower:
            found_words.append(word)
    
    return len(found_words) > 0, found_words

def replace_forbidden_words(text: str, forbidden_words: List[str]) -> str:
    """
    Replace forbidden words with alternatives
    
    Args:
        text: Original text
        forbidden_words: List of forbidden words
        
    Returns:
        Text with forbidden words replaced
    """
    if not text or not forbidden_words:
        return text
    
    replacements = {
        "damn": "darn",
        "possessive": "protective",
        "possessiveness": "protectiveness",
        "butterflies in stomach": "nervous excitement",
        "butterflies": "fluttering feeling",
        "knot": "tightness"
    }
    
    text_lower = text.lower()
    
    for word in forbidden_words:
        word_lower = word.lower()
        if word_lower in text_lower:
            replacement = replacements.get(word_lower, "[REDACTED]")
            # Case-insensitive replacement
            text = re.sub(re.escape(word), replacement, text, flags=re.IGNORECASE)
    
    return text

def detect_spicy_content(text: str) -> float:
    """
    Detect if text contains spicy/mature content
    
    Args:
        text: Text to analyze
        
    Returns:
        Spiciness score (0.0 to 1.0)
    """
    if not text:
        return 0.0
    
    spicy_indicators = [
        "intimate", "passion", "desire", "tension", "heat", "sensual",
        "touch", "embrace", "kiss", "close", "warm", "electric"
    ]
    
    text_lower = text.lower()
    matches = sum(1 for indicator in spicy_indicators if indicator in text_lower)
    
    # Simple scoring based on matches
    score = min(matches / len(spicy_indicators), 1.0)
    
    # Boost score for certain combinations
    if any(phrase in text_lower for phrase in ["spicy", "mature", "adult"]):
        score = min(score + 0.3, 1.0)
    
    return score

def should_trigger_autoplot(chance: int) -> bool:
    """
    Determine if autoplot should trigger based on chance
    
    Args:
        chance: Percentage chance (0-100)
        
    Returns:
        True if autoplot should trigger
    """
    return random.randint(1, 100) <= chance

def should_trigger_spice_enhancement(chance: int) -> bool:
    """
    Determine if spice enhancement should trigger
    
    Args:
        chance: Percentage chance (0-100)
        
    Returns:
        True if enhancement should trigger
    """
    return random.randint(1, 100) <= chance

def format_for_janitor_response(content: str, model: str) -> dict:
    """
    Format response for Janitor.ai compatibility
    
    Args:
        content: Response content
        model: Model name
        
    Returns:
        Formatted response dictionary
    """
    import time
    
    return {
        "id": f"chatcmpl-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": "stop",
        }],
        "usage": {
            "prompt_tokens": len(content),
            "completion_tokens": len(content),
            "total_tokens": len(content) * 2,
        },
    }

def format_for_streaming_chunk(content: str) -> str:
    """
    Format content for streaming response
    
    Args:
        content: Content chunk
        
    Returns:
        JSON formatted chunk
    """
    import json
    
    return f"data: {json.dumps({'choices': [{'delta': {'content': content}}]})}\n\n"
