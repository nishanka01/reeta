# REETA — AI Desktop Voice Assistant

> **Phase 1** — A working AI voice assistant that listens, thinks, speaks, and controls your desktop.

REETA is an AI software layer that runs on top of Windows. Think of it as a beginner version of JARVIS — it listens for your voice commands, responds intelligently using AI, opens applications, searches the web, and speaks back to you naturally.

---

## ✨ Features (Phase 1)

| Feature | Description |
|---|---|
| 🎤 Wake Word | Say "Hey Reeta" to activate |
| 🗣️ Voice Input | Speech-to-text using OpenAI Whisper (local) |
| 🧠 AI Brain | Powered by GPT-4o or Claude for intelligent responses |
| 🔊 Voice Output | Text-to-speech using pyttsx3 (offline) |
| 💻 Desktop Control | Open Chrome, VS Code, Notepad, and more |
| 🌐 Web Commands | Open YouTube, Google, Gmail, search the web |
| 🕐 Utilities | Tell current time/date, lock screen |
| 📝 Logging | Colored console + rotating file logs |

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** (recommended: 3.11 or 3.12)
- **Windows 10/11**
- **A microphone** (built-in laptop mic works)
- **Internet connection** (for API calls and wake word detection)

### Step 1: Clone / Copy the Project
```bash
# Copy the REETA folder to your desired location
```

### Step 2: Create a Virtual Environment
```bash
cd REETA
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**⚠️ PyAudio Trouble on Windows?**
```bash
# Option 1: Use pipwin
pip install pipwin
pipwin install pyaudio

# Option 2: Download wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
pip install PyAudio‑0.2.14‑cp311‑cp311‑win_amd64.whl
```

**💡 Smaller PyTorch (CPU-only, saves ~1GB):**
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Step 4: Configure API Keys
Edit the `.env` file:
```env
OPENAI_API_KEY=sk-your-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Step 5: Run REETA
```bash
python main.py
```

---

## 🎤 How to Use

1. **Start REETA**: Run `python main.py`
2. **Wait for calibration**: Microphone calibrates automatically
3. **Say "Hey Reeta"**: The assistant activates
4. **Speak your command**: e.g., "Open Chrome" or "What's the weather like?"
5. **Listen to response**: REETA speaks back to you
6. **Say "Exit"** or press `Ctrl+C` to stop

### Example Commands

```
"Hey Reeta" → "Open Chrome"
"Hey Reeta" → "What time is it?"
"Hey Reeta" → "Search for Python tutorials"
"Hey Reeta" → "Open YouTube"
"Hey Reeta" → "Who invented the internet?"
"Hey Reeta" → "Open VS Code"
"Hey Reeta" → "What's today's date?"
"Hey Reeta" → "Goodbye"
```

---

## 📁 Project Structure

```
REETA/
├── brain/
│   └── llm_handler.py      # AI brain (OpenAI + Claude)
├── voice/
│   ├── wakeword.py          # Wake word detection
│   ├── listener.py          # Speech-to-text (Whisper)
│   └── speaker.py           # Text-to-speech (pyttsx3)
├── commands/
│   └── command_handler.py   # Command router
├── automation/
│   └── app_control.py       # Desktop app launcher
├── config/
│   └── settings.py          # Configuration loader
├── utils/
│   ├── logger.py            # Logging system
│   └── helpers.py           # Utility functions
├── logs/                    # Auto-generated log files
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
├── .env                     # API keys (never commit!)
└── README.md                # This file
```

---

## 🔑 API Key Setup

### OpenAI
1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Navigate to **API Keys**
4. Click **Create new secret key**
5. Copy and paste into `.env` as `OPENAI_API_KEY`

### Anthropic (Claude)
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Navigate to **API Keys**
4. Click **Create Key**
5. Copy and paste into `.env` as `ANTHROPIC_API_KEY`

---

## 🐛 Common Issues & Fixes

| Issue | Fix |
|---|---|
| `PyAudio` install fails | Use `pipwin install pyaudio` or download a pre-built wheel |
| "No microphone found" | Check Windows Sound settings → Input devices |
| Wake word not detected | Speak clearly, reduce background noise, try recalibrating |
| Whisper download slow | First run downloads the model (~140MB). Wait for it. |
| API key errors | Double-check your `.env` file. No quotes around the key. |
| `torch` too large | Use CPU-only: `pip install torch --index-url https://download.pytorch.org/whl/cpu` |

---

## ⚡ Performance Tips

1. **Use `whisper` model `tiny`** for faster (but less accurate) transcription
2. **Use `gpt-4o-mini`** instead of `gpt-4o` for faster AI responses
3. **CPU-only PyTorch** saves disk space and works fine for the `base` model
4. **Close other mic-using apps** (Discord, Zoom) to avoid conflicts

---

## 🔮 Phase 2 Roadmap

- **Memory System** — Remember past conversations using vector database
- **Multi-Agent Architecture** — Specialized agents for coding, research, etc.
- **Automation Engine** — File management, email drafting, scheduling
- **Vision AI** — Screenshot analysis with GPT-4V
- **Desktop GUI** — CustomTkinter or Electron-based interface
- **FastAPI Backend** — REST API for remote control
- **Plugin System** — Community-contributed skills

---

## 📄 License

This project is for educational and personal use.

---

Built with ❤️ by the REETA team.
