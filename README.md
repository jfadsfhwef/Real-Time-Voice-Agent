# Real-Time Voice Agent

A real-time voice agent that conducts backend development interviews using LiveKit for audio streaming, Microsoft Edge TTS for voice synthesis, and Google's Gemini model for conversational AI.

## Features

- **Real-time audio streaming** using LiveKit
- **Speech-to-text** using Deepgram
- **Text-to-speech** using Microsoft Edge TTS (free)
- **Conversational AI** using Google Gemini
- **RESTful API** with FastAPI
- **CLI tool** for direct agent usage

## Architecture

The system is built with a modular architecture:

- **Services**: Core speech and language functionality
- **Agent**: Business logic for interviews
- **API**: FastAPI endpoints for web access
- **Config**: Centralized configuration management
- **Utils**: Helper utilities

## Project Structure

```
real-time-voice-agent/
├── src/                    # Main source code
│   ├── agent/              # Interview agent components
│   ├── api/                # FastAPI endpoints
│   ├── config/             # Configuration management
│   ├── services/           # Core services (TTS, STT, LLM)
│   └── utils/              # Utility functions
├── tests/                  # Test suite
├── examples/               # Example usage
│   ├── basic_usage.py      # Basic Python example
│   └── web/                # Web examples
├── run_api.sh              # Script to run the API server
├── run_cli.sh              # Script to run the CLI tool
├── run_tests.sh            # Script to run tests
└── requirements.txt        # Dependencies
```

## Prerequisites

- Python 3.9+
- LiveKit account (for real-time audio)
- Google API key (for Gemini)
- Deepgram API key (for speech-to-text)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/real-time-voice-agent.git
cd real-time-voice-agent
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys (copy from env.example):
```bash
cp env.example .env
# Then edit .env with your actual API keys
```

## Usage

### Running the API Server

```bash
# Using the script (recommended)
./run_api.sh

# Or manually
uvicorn src.main:app --reload
```

The API will be available at http://localhost:8000, with interactive documentation at http://localhost:8000/docs.

### Running the CLI Tool

```bash
# Using the script (recommended)
./run_cli.sh
# With custom room
./run_cli.sh --room custom-room-name
# With debug logging
./run_cli.sh --debug

# Or manually
python -m src.run_cli
```

### Running the Example

```bash
python examples/basic_usage.py
```

### Running Tests

```bash
# Using the script (recommended)
./run_tests.sh

# Or manually
python -m pytest tests/
```

## API Endpoints

- **POST /api/v1/transcribe**: Transcribe audio to text
- **POST /api/v1/synthesize**: Synthesize text to speech
- **GET /api/v1/interview/questions**: List interview questions
- **POST /api/v1/interview/generate**: Generate interview response
- **GET /api/v1/interview/history**: Get conversation history
- **POST /api/v1/interview/reset**: Reset interview
- **POST /api/v1/room/create**: Create a new LiveKit room
- **DELETE /api/v1/room/{room_name}**: Delete a room

## License

MIT License