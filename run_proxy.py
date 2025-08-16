#!/usr/bin/env python3
"""
Google AI Studio Proxy Runner
A clean, modular proxy server for Google AI Studio with enhanced features
"""

import sys
import os
import argparse
import uvicorn
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from proxy.app import app
from tunnel.manager import tunnel_manager
from config.settings import config

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Google AI Studio Proxy Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_proxy.py                    # Run with default settings
  python run_proxy.py --model gemini-2.5-flash  # Use specific model
  python run_proxy.py --tunnel cloudflare     # Use Cloudflare tunnel
  python run_proxy.py --config custom.json    # Use custom config
        """
    )
    
    parser.add_argument(
        "--model",
        type=str,
        help="AI model to use (Google: gemini-2.5-flash, Cerebras: llama3-8b)"
    )
    
    parser.add_argument(
        "--tunnel",
        type=str,
        choices=["ngrok", "cloudflare", "localtunnel"],
        help="Tunnel provider to use"
    )
    
    parser.add_argument(
        "--ai-provider",
        type=str,
        choices=["google", "cerebras"],
        default="google",
        help="AI provider to use (google or cerebras)"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to custom configuration file"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    return parser.parse_args()

def setup_environment(args):
    """Setup environment based on arguments"""
    if args.model:
        config.set("model", args.model)
    
    if args.tunnel:
        config.set("tunnel_provider", args.tunnel.capitalize())
    
    if args.ai_provider:
        config.set("ai_provider", args.ai_provider)
    
    if args.config and os.path.exists(args.config):
        import json
        with open(args.config, 'r') as f:
            custom_config = json.load(f)
            for key, value in custom_config.items():
                config.set(key, value)
    
    # Validate AI provider after setup
    if config.get("ai_provider") not in ["google", "cerebras"]:
        raise ValueError("AI provider must be 'google' or 'cerebras'")

def print_banner():
    """Print startup banner"""
    print("\n" + "=" * 60)
    print("🚀 Google AI Studio Proxy Server (FastAPI Edition)")
    print("=" * 60)
    print(f"📋 Model: {config.get('model')}")
    print(f"🌐 Tunnel: {config.get('tunnel_provider')}")
    print(f"🔧 Jailbreak: {'Enabled' if config.get('enable_jailbreak') else 'Disabled'}")
    print(f"💬 OOC: {'Enabled' if config.get('enable_ooc_injection') else 'Disabled'}")
    print(f"📚 Lorebook: {'Enabled' if config.get('enable_lorebook') else 'Disabled'}")
    print("=" * 60)
    print("Starting server...")

def main():
    """Main function to run the proxy server"""
    args = parse_arguments()
    setup_environment(args)
    print_banner()

    # Start tunnel
    tunnel_url = tunnel_manager.start_tunnel(app, args.port)
    
    if tunnel_url:
        print(f"Tunnel started: {tunnel_url}")
        tunnel_manager.display_tunnel_info(tunnel_url)

    uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="info" if not args.debug else "debug")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)
