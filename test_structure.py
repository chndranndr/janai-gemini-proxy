"""
Test script to verify the modular structure is working correctly
"""

import os
import sys
import json

def test_imports():
    """Test that all modules can be imported"""
    try:
        from config.settings import config
        print("✓ config.settings imported successfully")
        
        from config.constants import DEFAULT_MODEL
        print("✓ config.constants imported successfully")
        
        from content.jailbreak import get_jailbreak_text
        print("✓ content.jailbreak imported successfully")
        
        from content.text_processing import clean_response_text
        print("✓ content.text_processing imported successfully")
        
        from content.lorebook import lorebook_manager
        print("✓ content.lorebook imported successfully")
        
        from tunnel.manager import tunnel_manager
        print("✓ tunnel.manager imported successfully")
        
        from ai.client import GoogleAIClient
        print("✓ ai.client imported successfully")
        
        # Test proxy.app without creating the app instance
        import proxy.app
        print("✓ proxy.app imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_config():
    """Test configuration loading"""
    try:
        from config.settings import config
        
        # Test default values
        assert config.get("model") == "gemini-2.5-flash"
        assert config.get("tunnel_provider") == "Ngrok"
        assert config.get("top_p") == 0.9
        assert config.get("top_k") == 45
        
        print("✓ Configuration loaded correctly")
        return True
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        return False

def test_jailbreak():
    """Test jailbreak text generation"""
    try:
        from content.jailbreak import get_jailbreak_text
        
        # Test different bypass levels
        none_text = get_jailbreak_text("none")
        light_text = get_jailbreak_text("light")
        strong_text = get_jailbreak_text("strong")
        
        assert none_text == ""
        assert len(light_text) > 0
        assert len(strong_text) > len(light_text)
        
        print("✓ Jailbreak text generation working")
        return True
    except Exception as e:
        print(f"✗ Jailbreak test failed: {e}")
        return False

def test_lorebook():
    """Test lorebook functionality"""
    try:
        from content.lorebook import lorebook_manager
        
        # Test empty lorebook
        lorebook_manager.load_lorebook()
        assert not lorebook_manager.is_loaded
        
        # Test with sample data
        sample_lore = {
            "characters": {
                "test_character": {
                    "name": "Test Character",
                    "description": "A test character",
                    "personality": "Friendly"
                }
            }
        }
        
        lorebook_manager.load_lorebook(json.dumps(sample_lore))
        assert lorebook_manager.is_loaded
        assert "test_character" in lorebook_manager.characters
        
        print("✓ Lorebook functionality working")
        return True
    except Exception as e:
        print(f"✗ Lorebook test failed: {e}")
        return False

def test_text_processing():
    """Test text processing utilities"""
    try:
        from content.text_processing import clean_response_text
        
        # Test response cleaning
        test_text = "  Hello world  \n\nExtra newlines\n\n"
        cleaned = clean_response_text(test_text, "")
        assert "Hello world" in cleaned
        
        # Test markdown formatting
        from content.text_processing import ensure_markdown_formatting
        
        test_md = "This is a paragraph"
        formatted = ensure_markdown_formatting(test_md)
        assert isinstance(formatted, str)
        
        print("✓ Text processing utilities working")
        return True
    except Exception as e:
        print(f"✗ Text processing test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing modular structure...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_jailbreak,
        test_lorebook,
        test_text_processing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The modular structure is working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == '__main__':
    main()
