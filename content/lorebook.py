"""
Lorebook management for character and world information
"""

import json
import re
from typing import Dict, List, Optional, Any
from config.settings import config

class LorebookManager:
    """Manages lorebook content and character information"""
    
    def __init__(self):
        self.lorebook_data = {}
        self.characters = {}
        self.world_info = {}
        self.is_loaded = False
    
    def load_lorebook(self, json_content: str = None) -> bool:
        """
        Load lorebook from JSON content
        
        Args:
            json_content: JSON string containing lorebook data
            
        Returns:
            True if loaded successfully
        """
        if json_content is None:
            json_content = config.get("lorebook_json_content", "")
        
        if not json_content or not json_content.strip():
            self.is_loaded = False
            return False
        
        try:
            data = json.loads(json_content)
            
            # Support multiple lorebook formats
            if isinstance(data, dict):
                self.lorebook_data = data
                self._extract_characters()
                self._extract_world_info()
            elif isinstance(data, list):
                # Handle array format
                self.lorebook_data = {"entries": data}
                self._process_entries(data)
            
            self.is_loaded = True
            return True
            
        except json.JSONDecodeError as e:
            print(f"Error loading lorebook: {e}")
            self.is_loaded = False
            return False
    
    def _extract_characters(self):
        """Extract character information from lorebook"""
        characters = self.lorebook_data.get("characters", {})
        for char_name, char_data in characters.items():
            self.characters[char_name.lower()] = {
                "name": char_name,
                "description": char_data.get("description", ""),
                "personality": char_data.get("personality", ""),
                "background": char_data.get("background", ""),
                "relationships": char_data.get("relationships", {}),
                "appearance": char_data.get("appearance", ""),
                "quirks": char_data.get("quirks", [])
            }
    
    def _extract_world_info(self):
        """Extract world information from lorebook"""
        world_data = self.lorebook_data.get("world", {})
        self.world_info = {
            "setting": world_data.get("setting", ""),
            "time_period": world_data.get("time_period", ""),
            "locations": world_data.get("locations", {}),
            "rules": world_data.get("rules", {}),
            "magic_system": world_data.get("magic_system", ""),
            "technology_level": world_data.get("technology_level", "")
        }
    
    def _process_entries(self, entries: List[Dict[str, Any]]):
        """Process array format entries"""
        for entry in entries:
            if entry.get("type") == "character":
                name = entry.get("name", "").lower()
                self.characters[name] = entry
            elif entry.get("type") == "world":
                self.world_info.update(entry.get("data", {}))
    
    def get_character_info(self, character_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific character
        
        Args:
            character_name: Name of the character
            
        Returns:
            Character information dictionary or None
        """
        return self.characters.get(character_name.lower())
    
    def get_world_context(self) -> str:
        """
        Get world context as a formatted string
        
        Returns:
            World context string
        """
        if not self.is_loaded:
            return ""
        
        context_parts = []
        
        if self.world_info.get("setting"):
            context_parts.append(f"Setting: {self.world_info['setting']}")
        
        if self.world_info.get("time_period"):
            context_parts.append(f"Time Period: {self.world_info['time_period']}")
        
        if self.world_info.get("technology_level"):
            context_parts.append(f"Technology: {self.world_info['technology_level']}")
        
        if self.world_info.get("magic_system"):
            context_parts.append(f"Magic System: {self.world_info['magic_system']}")
        
        locations = self.world_info.get("locations", {})
        if locations:
            context_parts.append("Key Locations:")
            for loc_name, loc_desc in locations.items():
                context_parts.append(f"- {loc_name}: {loc_desc}")
        
        return "\n".join(context_parts)
    
    def get_character_context(self, character_name: str = None) -> str:
        """
        Get character context as a formatted string
        
        Args:
            character_name: Specific character to get context for, or None for all
            
        Returns:
            Character context string
        """
        if not self.is_loaded:
            return ""
        
        if character_name:
            char = self.get_character_info(character_name)
            if char:
                return self._format_character_info(char)
        
        # Return all characters
        context_parts = []
        for char_data in self.characters.values():
            context_parts.append(self._format_character_info(char_data))
        
        return "\n\n".join(context_parts)
    
    def _format_character_info(self, char_data: Dict[str, Any]) -> str:
        """Format character information into a readable string"""
        parts = [f"Character: {char_data.get('name', 'Unknown')}"]
        
        if char_data.get("description"):
            parts.append(f"Description: {char_data['description']}")
        
        if char_data.get("personality"):
            parts.append(f"Personality: {char_data['personality']}")
        
        if char_data.get("background"):
            parts.append(f"Background: {char_data['background']}")
        
        if char_data.get("appearance"):
            parts.append(f"Appearance: {char_data['appearance']}")
        
        if char_data.get("quirks"):
            quirks = ", ".join(char_data["quirks"])
            parts.append(f"Quirks: {quirks}")
        
        relationships = char_data.get("relationships", {})
        if relationships:
            parts.append("Relationships:")
            for rel_name, rel_desc in relationships.items():
                parts.append(f"- {rel_name}: {rel_desc}")
        
        return "\n".join(parts)
    
    def inject_context(self, prompt: str, character_name: str = None) -> str:
        """
        Inject lorebook context into a prompt
        
        Args:
            prompt: Original prompt
            character_name: Specific character context to include
            
        Returns:
            Prompt with lorebook context injected
        """
        if not self.is_loaded or not config.get("enable_lorebook", False):
            return prompt
        
        context_parts = []
        
        # Add world context
        world_context = self.get_world_context()
        if world_context:
            context_parts.append(world_context)
        
        # Add character context
        char_context = self.get_character_context(character_name)
        if char_context:
            context_parts.append(char_context)
        
        if context_parts:
            full_context = "\n\n".join(context_parts)
            return f"[Lorebook Context]\n{full_context}\n\n[User Prompt]\n{prompt}"
        
        return prompt
    
    def search_lorebook(self, query: str) -> List[Dict[str, Any]]:
        """
        Search lorebook for relevant information
        
        Args:
            query: Search query
            
        Returns:
            List of relevant entries
        """
        if not self.is_loaded:
            return []
        
        query_lower = query.lower()
        results = []
        
        # Search characters
        for char_name, char_data in self.characters.items():
            if query_lower in char_name.lower():
                results.append({"type": "character", "data": char_data})
            elif any(query_lower in str(value).lower() for value in char_data.values()):
                results.append({"type": "character", "data": char_data})
        
        # Search world info
        for key, value in self.world_info.items():
            if isinstance(value, str) and query_lower in value.lower():
                results.append({"type": "world", "key": key, "value": value})
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if query_lower in str(sub_key).lower() or query_lower in str(sub_value).lower():
                        results.append({"type": "world", "key": sub_key, "value": sub_value})
        
        return results

# Global lorebook manager instance
lorebook_manager = LorebookManager()
