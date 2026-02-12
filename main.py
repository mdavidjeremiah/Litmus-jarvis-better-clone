#!/usr/bin/env python3
"""
JARVIS AI Assistant - Main Entry Point
"""
import argparse
import sys
import asyncio
from pathlib import Path

# Add project to path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from jarvis.core import JarvisCore
from jarvis.config.settings import Settings

def main():
    parser = argparse.ArgumentParser(description="JARVIS AI Assistant")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--text-only", "-t", action="store_true", help="Text-only mode (no voice)")
    parser.add_argument("--config", "-c", type=str, default="config/default_config.yaml", help="Config file path")
    parser.add_argument("--command", "-cmd", type=str, help="Execute single command and exit")
    
    args = parser.parse_args()
    
    # Load settings
    settings = Settings.from_yaml(args.config)
    
    if args.text_only:
        settings.voice.enabled = False
    
    # Initialize JARVIS
    jarvis = JarvisCore(settings)
    
    try:
        if args.command:
            # Single command mode
            response = asyncio.run(jarvis.process_command(args.command))
            print(response)
        elif args.interactive or not settings.voice.enabled:
            # Interactive or text-only mode
            jarvis.run_interactive()
        else:
            # Full voice mode
            jarvis.run()
            
    except KeyboardInterrupt:
        print("\nGoodbye!")
    finally:
        jarvis.shutdown()

if __name__ == "__main__":
    main()
