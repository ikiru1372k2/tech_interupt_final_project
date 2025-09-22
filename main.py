#!/usr/bin/env python3
"""
Effort Expense Management
Main entry point for the application
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from config import Config
from streamlit_app import main as run_streamlit_app

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('effort_expense_system.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_environment():
    """Check if required environment variables are set."""
    required_vars = ['TENANT_ID', 'CLIENT_ID', 'CLIENT_SECRET']
    missing_vars = []
    
    for var in required_vars:
        if not getattr(Config, var, None):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Warning: The following environment variables are not set:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Please set these variables in your .env file or environment.")
        print("   You can copy env_example.txt to .env and fill in your values.")
        print("\n🚀 The application will still run, but some features may not work.")
        print("   (Notifications will be disabled without Microsoft 365 credentials)")
        print("\n" + "="*60 + "\n")

def main():
    """Main application entry point."""
    print("🚀 Starting Effort Expense Management System...")
    print("="*60)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check environment
    check_environment()
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("📄 No .env file found. Creating from template...")
        try:
            with open('env_example.txt', 'r') as src:
                with open('.env', 'w') as dst:
                    dst.write(src.read())
            print("✅ Created .env file from template. Please update it with your credentials.")
        except FileNotFoundError:
            print("⚠️  env_example.txt not found. Please create .env file manually.")
    
    # Display configuration status
    print("🔧 Configuration Status:")
    print(f"   - Effort Limit: {Config.EFFORT_EXPENSE_LIMIT} hours")
    print(f"   - Missing Threshold: {Config.MISSING_VALUE_THRESHOLD * 100}%")
    print(f"   - n8n Webhook: {'✅ Configured' if Config.N8N_WEBHOOK_URL else '❌ Not configured'}")
    print(f"   - Microsoft 365: {'✅ Configured' if Config.TENANT_ID else '❌ Not configured'}")
    print("\n" + "="*60 + "\n")
    
    try:
        # Run Streamlit application
        logger.info("Starting Streamlit application...")
        run_streamlit_app()
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user.")
        logger.info("Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {str(e)}")
        logger.error(f"Error starting application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
