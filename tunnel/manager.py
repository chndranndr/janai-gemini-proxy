"""
Tunnel management for different providers (Ngrok, Cloudflare, LocalTunnel)
"""

import subprocess
import sys
from typing import Optional, Dict, Any
from config.settings import config
from pyngrok import ngrok

class TunnelManager:
    """Manages different tunnel providers for exposing the proxy"""
    
    def __init__(self):
        self.available_providers = {"Ngrok": "ngrok"}
    
    def get_available_providers(self) -> list:
        """Get list of available tunnel providers"""
        return list(self.available_providers.keys())
    
    def start_tunnel(self, app, port: int, provider: str = None) -> Optional[str]:
        """
        Start tunnel with specified provider
        
        Args:
            app: FastAPI application instance
            port: Port the app is running on
            provider: Tunnel provider name
            
        Returns:
            Tunnel URL or None if failed
        """
        if provider is None:
            provider = config.get("tunnel_provider", "Ngrok")
        
        if provider not in self.available_providers:
            print(f"Provider {provider} not available")
            return None
        
        try:
            if provider == "Ngrok":
                return self._start_ngrok(port)
        except Exception as e:
            print(f"Error starting {provider} tunnel: {e}")
            return None
    
    def _start_ngrok(self, port: int) -> str:
        """Start Ngrok tunnel"""
        ngrok_token = config.get("ngrok_token")
        if ngrok_token:
            ngrok.set_auth_token(ngrok_token)
        
        # Start ngrok tunnel
        tunnel = ngrok.connect(port)
        return tunnel.public_url
    
    def get_public_ip(self) -> Optional[str]:
        """Get public IP address"""
        try:
            import requests
            response = requests.get('https://ipecho.net/plain', timeout=5)
            return response.text.strip()
        except:
            return None
    
    def display_tunnel_info(self, tunnel_url: str):
        """Display tunnel information"""
        print("\n" + "=" * 50)
        print("🚀 Google AI Studio Proxy for Janitor.ai successfully started!")
        print("=" * 50)
        print(f"📋 Selected Model: {config.get('model')}")
        print(f"🔧 Configuration:")
        print(f"   - 🛡️ Jailbreak: {'Enabled' if config.get('enable_jailbreak') else 'Disabled'}")
        print(f"   - 💬 OOC Instructions: {'Enabled' if config.get('enable_ooc_injection') else 'Disabled'}")
        print(f"   - 📝 Markdown Formatting: {'Enabled' if config.get('enable_markdown_check') else 'Disabled'}")
        print(f"   - 🤔 Force Thinking: {'Enabled' if config.get('enable_force_thinking') else 'Disabled'}")
        print(f"   - 🏰 Medieval Mode: {'Enabled' if config.get('enable_medieval_mode') else 'Disabled'}")
        print(f"   - 🌶️ Better Spice: {'Enabled' if config.get('enable_better_spice') else 'Disabled'}")
        print(f"   - 🎭 AutoPlot: {'Enabled' if config.get('enable_autoplot') else 'Disabled'}")
        print(f"   - 🌪️ Chaos&Drama: {'Enabled' if config.get('enable_crazy_mode') else 'Disabled'}")
        print(f"   - 📚 Lorebook: {'Enabled' if config.get('enable_lorebook') else 'Disabled'}")
        print(f"   - 💬 Custom OOC: {'Enabled' if bool(config.get('custom_ooc_text')) else 'Disabled'}")
        print(f"   - 🚫 Forbidden Words: {'Enabled' if config.get('enable_forbidden_words') else 'Disabled'}")
        print(f"   - 🔓 Bypass Level: {config.get('bypass_level')}")
        print("=" * 50)
        
        print("Use the ngrok.io URL shown above as your proxy address in Janitor.ai")
        print("Add your Google AI API key in the Janitor.ai settings")
        print("=" * 50 + "\n")

# Global tunnel manager instance
tunnel_manager = TunnelManager()
