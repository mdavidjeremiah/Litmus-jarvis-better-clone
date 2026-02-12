# 🤖 JARVIS AI Assistant
An offline-capable AI assistant inspired by Iron Man's JARVIS, built with Python. Features voice interaction, local LLM inference via Ollama, system automation, and offline web browsing.
## ✨ Features
- 🎙️ **Voice Interface** - Speech recognition and text-to-speech (fully offline)
- 🧠 **Local LLM** - Runs entirely offline using Ollama
- ⚡ **System Automation** - Open/close apps, manage files, system commands
- 🌐 **Offline Web** - Cache web pages locally with full-text search
- 🔌 **Extensible Skills** - Easy plugin system for new capabilities
## 🚀 Quick Start
### Prerequisites
- Python 3.10+
- Microphone (for voice mode)
- 8GB+ RAM recommended for LLM
### Installation
```bash
# Clone the repository
git clone <repo-url> jarvis
cd jarvis
# Run installer
chmod +x install.sh
./install.sh
# Or install manually:
pip install -r requirements.txt
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama2
Usage
bash
# Interactive text mode
python main.py --interactive
# Voice mode (default)
python main.py
# Execute single command
python main.py --command "What time is it?"
# CLI commands
python -m jarvis.cli status
python -m jarvis.cli cache https://example.com
python -m jarvis.cli search "python tutorial"
