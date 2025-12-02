from datetime import datetime
import os
import asyncio
import base64
import soundfile as sf
import numpy as np
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

def tprint(message):
    """print message with timestamp"""
    now = datetime.now()
    timestamp = now.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

async def send_audio(connection, is_loop=True):
    """
    Reads audio/noise-5.wav, chunks it, and sends it to the WebSocket.
    Loops the audio file indefinitely.
    """
    audio_file_path = 'audio/voice-with-noise.wav'
    
    if not os.path.exists(audio_file_path):
        tprint(f"Error: {audio_file_path} not found.")
        return

    # Read the audio file
    # dtype='int16' ensures we get PCM16 data directly
    data, samplerate = sf.read(audio_file_path, dtype='int16')
    
    # OpenAI Realtime API expects 24kHz. 
    tprint(f"Loaded audio file: {audio_file_path}, Sample Rate: {samplerate}Hz, Samples: {len(data)}")

    # Calculate chunk size for ~100ms (0.1s)
    # 24000 Hz * 0.1s = 2400 samples
    chunk_duration = 0.1
    chunk_size = int(samplerate * chunk_duration)
    
    while True:
        tprint("Audio input loop starting...")
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i+chunk_size]
            
            # Ensure we have bytes
            if isinstance(chunk, np.ndarray):
                chunk_bytes = chunk.tobytes()
            else:
                chunk_bytes = chunk
                
            base64_audio = base64.b64encode(chunk_bytes).decode('utf-8')
            
            try:
                await connection.input_audio_buffer.append(audio=base64_audio)
            except Exception as e:
                tprint(f"Error sending audio: {e}")
                break
            
            # Sleep to simulate real-time
            await asyncio.sleep(chunk_duration)
        
        if not is_loop:
            tprint("Audio input loop stopped")
            break

        await asyncio.sleep(1) # Pause briefly between loops

async def receive_events(connection):
    """
    Listens for events from the WebSocket and prints transcripts.
    """
    async for event in connection:
        try:
            # print(f"\n[Event]: {event.type}")
            if event.type == "response.output_audio_transcript.done":
                # Final assistant transcript
                tprint(f"[Assistant]: {event.transcript}")

            # elif event.type == "response.output_audio_transcript.delta":
                # Streaming assistant transcript
                # print(event.delta, end="", flush=True)
                
            elif event.type == "conversation.item.input_audio_transcription.completed":
                # User transcript
                tprint(f"[User]: {event.transcript}")
            elif event.type == "input_audio_buffer.speech_started":
                tprint("==== User speech detected, interrupting AI playback ====")
                
            elif event.type == "error":
                tprint(f"\nError: {event.error.message}")
                
            elif event.type == "session.created":
                tprint("Session created.")
                
        except Exception as e:
            tprint(f"Error processing message: {e}")

async def main():
    if not API_KEY:
        tprint("Please set OPENAI_API_KEY in .env file")
        return

    client = AsyncOpenAI()
    
    tprint("Connecting to OpenAI Realtime API...")
    
    try:
        realtime_model = os.getenv("OPENAI_REALTIME_MODEL") or "gpt-realtime"
        async with client.realtime.connect(model=realtime_model) as connection:
            tprint("Connected.")
            
            # Configure session to enable input audio transcription
            await connection.session.update(session={
                "type": "realtime",
                "instructions": "You are an English teacher.",
                "audio": {
                    "input": {
                        "transcription": {"language": "en", "model": "whisper-1"},
                        "noise_reduction": {"type": "far_field"},
                        "turn_detection": {
                            "type": "server_vad",
                            "silence_duration_ms": 700,
                            "threshold": 0.5
                        },
                    }
                },
            })
            
            # Run send and receive concurrently
            await asyncio.gather(
                send_audio(connection, is_loop=False),
                receive_events(connection)
            )
    except Exception as e:
        tprint(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
