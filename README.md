# 🌟Mai - Local AI Assistant

## ✨ Overview

Mai is a real time local AI assistant you can speak to just like to Siri. Powered by Gemma4 E2B it is highly capable, yet in the same time requires minimal resources to work

## 🎯 Features

A detailed list of all primary capabilities your project offers. Focus on benefits, not just features.

*   ✅ **Wake word detection:** *Talk to assistant only when you want to, your conversation start only when you command so*
*   ⚙️ **Web Search:** *The assistant is able to do secure websearch using [Searxng](https://github.com/searxng/searxng]) engine*

## 💡 Installation

Follow these steps to run Mai locally on your machine.

### Prerequisites
Before starting, ensure you have:
- Mac OS
- pip installed
- Python 3.11
- 5Gb of free storage and more than 8Gb of RAM
- Git installed
- Searxng running as docker container on port 8080 [setup link](https://docs.searxng.org/admin/installation-docker.html#installation-container)

### 🛠️ Setup Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/The0Invictus/hey_mai.git
   cd hey_mai
   
2. **Activate venv and Install dependencies:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   
3. **Download models**
   ```bash
   hf download ivvvvvi/hey_mai Hey_Mai.onnx --local-dir ./models
   hf download litert-community/gemma-4-E2B-it-litert-lm gemma-4-E2B-it.litertlm --local-dir ./models
4. **Run main script**
   ```bash
   python3 main.py
