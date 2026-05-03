#!/usr/bin/env python3
"""
KisanMitra – Smart Farming & Direct Selling Platform
Run with: python run.py
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    print("\n🌾  KisanMitra is starting...")
    print("🌐  Open http://localhost:5000 in your browser\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
