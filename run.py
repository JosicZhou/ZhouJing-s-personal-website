#!/usr/bin/env python3
"""
Zhou Jing's Personal Website
Run this script to start the website locally
"""

import os
import sys

if __name__ == '__main__':
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Import and run the Flask app
    from app import app
    
    print("=" * 50)
    print("Zhou Jing's Personal Website")
    print("=" * 50)
    print("Starting server...")
    print("Open your browser and navigate to: http://localhost:8080")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=8080)
