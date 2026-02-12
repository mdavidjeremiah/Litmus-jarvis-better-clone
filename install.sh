#!/bin/bash
# JARVIS Installation Script
set -e
echo "🤖 JARVIS AI Assistant - Installation"
echo "====================================="
# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"
# Create directories
echo "📁 Creating directories..."
mkdir -p data/sandbox
mkdir -p config
mkdir -p skills/custom
# Install system dependencies
echo "📦 Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    # Debian/Ubuntu
    sudo apt-get update
    sudo apt-get install -y \
        portaudio19-dev \
        python3-pyaudio \
        libespeak1 \
        espeak \
        ffmpeg \
        gcc \
        g++
elif command -v brew &> /dev/null; then
    # macOS
    brew install portaudio espeak ffmpeg
elif command -v yum &> /dev/null; then
    # RHEL/CentOS
    sudo yum install -y portaudio-devel espeak ffmpeg gcc
fi
# Install Python dependencies
echo "🐍 Installing Python packages..."
pip3 install -r requirements.txt
# Install Ollama
echo "🦙 Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.com/install.sh | sh
    echo "✅ Ollama installed"
else
    echo "✅ Ollama already installed"
fi
# Start Ollama service
echo "🚀 Starting Ollama service..."
ollama serve &
sleep 2
# Download default model
echo "📥 Downloading default model (llama2)..."
ollama pull llama2
# Create default config if not exists
if [ ! -f config/default_config.yaml ]; then
    echo "⚙️ Creating default configuration..."
    cp config/default_config.yaml.example config/default_config.yaml 2>/dev/null || true
fi
echo ""
echo "✅ Installation complete!"
echo ""
echo "To start JARVIS:"
echo "  python3 main.py --interactive    # Text mode"
echo "  python3 main.py                  # Voice mode"
echo ""
echo "To use CLI:"
echo "  python3 -m jarvis.cli --help"
