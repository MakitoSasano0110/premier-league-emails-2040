#!/usr/bin/env python3
"""
Launcher script for the Premier League Email Search Web App
"""
import subprocess
import sys
import os

def start_app():
    """Start the Streamlit web application"""
    try:
        print("🚀 プレミアリーグメール検索ウェブアプリを起動中...")
        print("📧 30通のメールデータが利用可能です")
        print("🌐 ブラウザで http://localhost:8501 にアクセスしてください")
        print("\n✨ 使用例:")
        print("  • Mohamed Salah Jr.の契約条件は？")
        print("  • Gabriel Fernandez 移籍金")
        print("  • Kai Havertz Jr. transfer")
        print("\n⚠️  アプリを停止するには Ctrl+C を押してください\n")
        
        # Start Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "web_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--server.headless", "true"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 アプリを停止しました")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    start_app()