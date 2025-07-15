#!/usr/bin/env python3
"""
Main entry point for Employee Directory API.

This is the primary entry point for the application.
For development, use: python main.py
For production, use: uvicorn main:app
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
