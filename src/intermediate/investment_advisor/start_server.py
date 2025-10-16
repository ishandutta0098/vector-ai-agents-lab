#!/usr/bin/env python3
"""
Startup script for the Financial Analysis API server.
This script provides an easy way to start the FastAPI server with proper configuration.
"""

import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def check_requirements():
    """Check if required packages are installed."""
    try:
        import crewai
        import fastapi
        import uvicorn

        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install the package")
        return False


def check_env_vars():
    """Check if required environment variables are set."""
    required_vars = ["OPENAI_API_KEY", "EXA_API_KEY"]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or environment")
        return False

    print("✅ All required environment variables are set")
    return True


def start_server(host="0.0.0.0", port=8000, reload=True):
    """Start the FastAPI server."""
    print(f"🚀 Starting Financial Analysis API server on {host}:{port}")
    print(f"📖 API documentation will be available at: http://{host}:{port}/docs")
    print(f"🔄 Auto-reload: {'enabled' if reload else 'disabled'}")

    try:
        import uvicorn

        uvicorn.run(
            "api_server:app", host=host, port=port, reload=reload, log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")


def main():
    """Main function to start the server with checks."""
    print("🔍 Checking system requirements...")

    # Check if we're in the right directory
    if not Path("src/intermediate/investment_advisor/api_server.py").exists():
        print(
            "❌ api_server.py not found. Please run this script from the root directory"
        )
        sys.exit(1)

    # Check requirements
    if not check_requirements():
        sys.exit(1)

    # Check environment variables
    if not check_env_vars():
        print("\n💡 Tip: Create a .env file with your API keys:")
        print("OPENAI_API_KEY=your_openai_key_here")
        print("EXA_API_KEY=your_exa_key_here")
        sys.exit(1)

    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(
        description="Start the Financial Analysis API server"
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind to (default: 8000)"
    )
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")

    args = parser.parse_args()

    # Start the server
    start_server(host=args.host, port=args.port, reload=not args.no_reload)


if __name__ == "__main__":
    main()
