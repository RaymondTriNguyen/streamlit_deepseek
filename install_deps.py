#!/usr/bin/env python3
"""
Installation script for streamlit-deepseek app.
This script handles PyYAML compatibility issues with Python 3.13.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors gracefully."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Installing dependencies for streamlit-deepseek...")
    
    # Upgrade pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        print("⚠️  Warning: Failed to upgrade pip, continuing anyway...")
    
    # Install PyYAML with specific version to avoid build issues
    if not run_command(f"{sys.executable} -m pip install 'PyYAML>=6.0,<7.0'", "Installing PyYAML"):
        print("⚠️  Warning: PyYAML installation failed, trying alternative...")
        # Try installing from wheel only
        run_command(f"{sys.executable} -m pip install --only-binary=all 'PyYAML>=6.0,<7.0'", "Installing PyYAML (wheel only)")
    
    # Install other dependencies
    dependencies = [
        "groq>=0.4.1",
        "requests>=2.31.0", 
        "python-dotenv>=1.0.0",
        "streamlit>=1.28.0",
        "typing-extensions>=4.0.0"
    ]
    
    for dep in dependencies:
        if not run_command(f"{sys.executable} -m pip install '{dep}'", f"Installing {dep}"):
            print(f"⚠️  Warning: Failed to install {dep}")
    
    print("\n🎉 Installation process completed!")
    print("You can now run your Streamlit app with: streamlit run streamlit.py")

if __name__ == "__main__":
    main()
