#!/bin/bash

set -e

echo "Updating system packages..."
#sudo apt update

echo "Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-venv \
    python3-pip \
    ffmpeg \
    build-essential \
    libsndfile1

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing Python packages..."
pip install \
    flask \
    werkzeug \
    vosk \
    piper-tts
echo "Python packages installed."
echo "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama2:7b
echo "Ollama installed and model pulled."
echo ""
echo "========================================"
echo "Setup complete."
echo ""
echo "To run your app:"
echo "source venv/bin/activate"
echo "python app.py"
echo "========================================"
