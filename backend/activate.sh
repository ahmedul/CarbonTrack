#!/bin/bash
# Backend Environment Activation Script for CarbonTrack
# This script activates the Python virtual environment for the backend project

echo "🚀 Activating CarbonTrack Backend Environment..."
source .venv/bin/activate
echo "✅ Backend environment activated (Python $(python --version | cut -d' ' -f2))"
echo "📦 FastAPI version: $(pip show fastapi | grep Version | cut -d' ' -f2)"
echo ""
echo "Available commands:"
echo "  uvicorn main:app --reload        # Start development server"
echo "  python -m pytest                 # Run tests"
echo "  python scripts/setup_cognito.py  # Setup AWS Cognito"
echo "  black . && isort .               # Format code"
echo ""
