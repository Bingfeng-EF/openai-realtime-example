# OpenAI Realtime API Example

This project demonstrates how to use the OpenAI Python SDK to interact with the **GPT Realtime API**. It streams a local audio file to the API, simulating a microphone input, and prints the user's transcription and the assistant's response.

## Prerequisites

- **Python 3.9+**
- **[uv](https://github.com/astral-sh/uv)** (recommended for dependency management) or `pip`
- **OpenAI API Key** with access to the Realtime API

## Setup

1.  **Clone the repository** (if applicable) or navigate to the project directory.

2.  **Configure Environment Variables**
    Create a `.env` file in the root directory and add your OpenAI API Key:
    ```bash
    cp .env.example .env
    ```
    Edit `.env`:
    ```env
    OPENAI_API_KEY=sk-proj-...
    # provide the right value for if you use Azure OpenAI
    OPENAI_BASE_URL=https://efekta-ai-qa-east-us-2.openai.azure.com/openai/v1
    OPENAI_REALTIME_MODEL=gpt-realtime
    ```

3.  **Install Dependencies**
    Using `uv`:
    ```bash
    uv sync
    ```
    *(Note: you can install directly if you don't have `uv`: `pip install openai>=1.55.0 websockets soundfile numpy python-dotenv`)*

## Usage

Run the main script using `uv`:

```bash
uv run main.py
```

Or with standard Python:

```bash
python main.py
```

### What it does

1.  **Connects**: Establishes a WebSocket connection to the OpenAI Realtime API using the `AsyncOpenAI` client.
2.  **Configures Session**: Sets up the session with the following parameters:
    *   **Instructions**: "You are an English teacher."
    *   **Voice Activity Detection (VAD)**: Server-side VAD enabled.
    *   **Transcription**: Whisper-1 model for English.
3.  **Streams Audio**: Reads `audio/noise-voice.wav` and streams it in chunks to the API, simulating real-time user speech.
4.  **Prints Events**:
    *   `[User]: ...` - Transcription of the uploaded audio.
    *   `[Assistant]: ...` - The model's text response.

## Project Structure

- `main.py`: The main script handling the WebSocket connection, audio streaming, and event processing.
- `pyproject.toml`: Dependency configuration (for `uv`).
- `audio/`: Directory containing sample audio files (`voice-with-noise.wav`).
- `.env`: API key configuration (not committed to version control).
