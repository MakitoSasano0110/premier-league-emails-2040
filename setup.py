#!/usr/bin/env python3
"""
Setup script for Premier League Email RAG Chatbot
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    try:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def run_app():
    """Run the Streamlit application"""
    try:
        print("Starting the application...")
        print("🚀 The chatbot will open in your browser at http://localhost:8501")
        print("📧 You can ask questions about Premier League player contracts in Japanese!")
        print("\nSample questions:")
        print("- Mohamed Salah Jr.の契約条件は？")
        print("- Arsenalの選手の年俸はいくら？")
        print("- Gabriel Fernandezの移籍金は？")
        print("\nPress Ctrl+C to stop the application\n")
        
        subprocess.run([sys.executable, "-m", "streamlit", "run", "email_rag_chatbot.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")

def main():
    print("🏁 Setting up Premier League Email RAG Chatbot...")
    
    # Check if we're in the right directory
    if not os.path.exists("requirements.txt"):
        print("❌ Error: requirements.txt not found. Please run this script from the project directory.")
        return
    
    if not os.path.exists("email_rag_chatbot.py"):
        print("❌ Error: email_rag_chatbot.py not found. Please run this script from the project directory.")
        return
    
    # Install requirements
    if install_requirements():
        print("\n" + "="*50)
        run_app()
    else:
        print("❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()