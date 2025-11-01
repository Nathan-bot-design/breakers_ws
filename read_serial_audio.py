# import serial
# import numpy as np
# import wave
# import time

# # === CONFIG ===
# PORT = "/dev/ttyACM0"    # Change if not this
# BAUD = 921600
# SAMPLE_RATE = 16000       # Must match ESP32
# RECORD_SECONDS = 5        # Must match ESP32
# OUTPUT_FILE = "esp_record.wav"

# TOTAL_BYTES = SAMPLE_RATE * RECORD_SECONDS * 2  # 2 bytes per sample

# print("Connecting to ESP32...")

# ser = serial.Serial(PORT, BAUD, timeout=5)  # 5-second timeout
# time.sleep(2)  # allow serial to settle

# print("Waiting for ESP32 to send START...")
# while True:
#     line = ser.readline().decode(errors='ignore').strip()
#     if line == "START":
#         print("🎙️ ESP32 started sending audio...")
#         break

# audio_bytes = bytearray()

# while len(audio_bytes) < TOTAL_BYTES:
#     chunk = ser.read(TOTAL_BYTES - len(audio_bytes))
#     if not chunk:
#         print("⚠️ Serial timeout — incomplete audio")
#         break
#     audio_bytes.extend(chunk)

# ser.close()
# print(f"✅ Received {len(audio_bytes)} bytes")

# # === SAVE TO WAV ===
# audio_np = np.frombuffer(audio_bytes, dtype=np.int16)

# with wave.open(OUTPUT_FILE, 'wb') as wf:
#     wf.setnchannels(1)          # mono
#     wf.setsampwidth(2)          # 16-bit PCM
#     wf.setframerate(SAMPLE_RATE)
#     wf.writeframes(audio_bytes)

# print(f"💾 Saved audio to '{OUTPUT_FILE}' ({len(audio_np)} samples)")




# import serial
# import numpy as np
# import wave
# import time
# import os
# import re
# import google.generativeai as genai
# from gtts import gTTS
# from pydub import AudioSegment
# import subprocess

# # ========= CONFIG =========
# PORT = "/dev/ttyACM0"
# BAUD = 921600
# SAMPLE_RATE = 16000
# RECORD_SECONDS = 10
# AUDIO_FILE = "esp_record.wav"

# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# model = genai.GenerativeModel("models/gemini-2.5-flash")

# def clean_text(text):
#     text = re.sub(r'[*_#`~]+', '', text)
#     text = re.sub(r'[^\w\s,.!?\'-]', '', text)
#     return text.strip()

# def record_from_esp32():
#     TOTAL_BYTES = SAMPLE_RATE * RECORD_SECONDS * 2

#     print("Connecting to ESP32...")
#     ser = serial.Serial(PORT, BAUD, timeout=5)
#     time.sleep(2)

#     print("Waiting for START...")
#     while True:
#         line = ser.readline().decode(errors='ignore').strip()
#         if line == "START":
#             print("Recording incoming audio...")
#             break

#     audio_bytes = bytearray()
#     while len(audio_bytes) < TOTAL_BYTES:
#         chunk = ser.read(TOTAL_BYTES - len(audio_bytes))
#         if not chunk:
#             print("Serial timeout.")
#             break
#         audio_bytes.extend(chunk)

#     ser.close()
#     print(f"Got {len(audio_bytes)} bytes")

#     with wave.open(AUDIO_FILE, 'wb') as wf:
#         wf.setnchannels(1)
#         wf.setsampwidth(2)
#         wf.setframerate(SAMPLE_RATE)
#         wf.writeframes(audio_bytes)

#     print("Saved:", AUDIO_FILE)


# def transcribe_audio():
#     print("Transcribing...")

#     with open(AUDIO_FILE, "rb") as f:
#         response = model.generate_content([{"mime_type": "audio/wav", "data": f.read()}])

#     text = clean_text(response.text)
#     print("You said:", text)
#     return text


# def stream_reply_and_speak(prompt):
#     print("\nAI: ", end="", flush=True)

#     response = model.generate_content(prompt, stream=True)

#     for chunk in response:
#         if not chunk.text:
#             continue

#         text_piece = clean_text(chunk.text)
#         print(text_piece, end="", flush=True)

#         if text_piece.strip():
#             tts = gTTS(text_piece)
#             tts.save("reply.mp3")
#             AudioSegment.from_mp3("reply.mp3").export("reply.wav", format="wav")
#             subprocess.run(["aplay", "reply.wav"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# # ======= MAIN FLOW LOOP =======
# while True:
#     record_from_esp32()
#     user_text = transcribe_audio()

#     if user_text.lower() in ["exit", "quit", "stop"]:
#         print("\nConversation ended.")
#         break

#     stream_reply_and_speak(user_text)
#     print("\n")

import os
import re
import time
import wave
import serial
import numpy as np
import subprocess
import google.generativeai as genai
from gtts import gTTS
from pydub import AudioSegment
import threading

# ========= ENV / AUDIO CONFIG =========
os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["ALSA_CARD"] = "default"
os.environ["AUDIODEV"] = "hw:0,0"

PORT = "/dev/ttyACM0"
BAUD = 921600
SAMPLE_RATE = 16000
RECORD_SECONDS = 10
AUDIO_FILE = "esp_record.wav"

# ========= GOOGLE GENAI CONFIG =========
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("models/gemini-2.5-flash")

# ========= HELPERS =========
def clean_text(text):
    """Remove unwanted markdown or strange symbols."""
    text = re.sub(r'[*_#`~]+', '', text)
    text = re.sub(r'[^\w\s,.!?\'-]', '', text)
    return text.strip()


def play_audio_non_blocking(file):
    """Play audio asynchronously (no hang on Ctrl+C)."""
    subprocess.Popen(["aplay", "-D", "default", file],
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)


def record_from_esp32():
    """Read raw PCM stream from ESP32 via serial and save as WAV."""
    TOTAL_BYTES = SAMPLE_RATE * RECORD_SECONDS * 2

    print("\n🔌 Connecting to ESP32...")
    ser = serial.Serial(PORT, BAUD, timeout=5)
    time.sleep(2)

    print("⏳ Waiting for START signal...")
    while True:
        line = ser.readline().decode(errors='ignore').strip()
        if line == "START":
            print("🎙️ Recording incoming audio...")
            break

    audio_bytes = bytearray()
    while len(audio_bytes) < TOTAL_BYTES:
        chunk = ser.read(TOTAL_BYTES - len(audio_bytes))
        if not chunk:
            print("⚠️ Serial timeout.")
            break
        audio_bytes.extend(chunk)

    ser.close()
    print(f"✅ Got {len(audio_bytes)} bytes")

    with wave.open(AUDIO_FILE, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_bytes)

    print("💾 Saved:", AUDIO_FILE)


def transcribe_audio():
    """Send audio to Gemini model for transcription."""
    print("\n🧠 Transcribing...")

    with open(AUDIO_FILE, "rb") as f:
        response = model.generate_content([{"mime_type": "audio/wav", "data": f.read()}])

    text = clean_text(response.text)
    print("🗣️ You said:", text)
    return text


def stream_reply_and_speak(prompt):
    """Generate streaming text + voice reply."""
    print("\n🤖 AI:", end=" ", flush=True)

    response = model.generate_content(prompt, stream=True)

    for chunk in response:
        if not chunk.text:
            continue

        text_piece = clean_text(chunk.text)
        print(text_piece, end=" ", flush=True)

        if text_piece.strip():
            # TTS piecewise (live streaming feel)
            tts = gTTS(text_piece)
            tts.save("reply.mp3")
            AudioSegment.from_mp3("reply.mp3").export("reply.wav", format="wav")
            play_audio_non_blocking("reply.wav")

    print()  # newline at end


# ========= MAIN LOOP =========
try:
    while True:
        record_from_esp32()
        user_text = transcribe_audio()

        if user_text.lower() in ["exit", "quit", "stop"]:
            print("\n👋 Conversation ended.")
            break

        stream_reply_and_speak(user_text)
        print("\n" + "-" * 50)

except KeyboardInterrupt:
    print("\n🛑 Stopped by user.")
except Exception as e:
    print(f"\n❌ Error: {e}")
finally:
    print("✅ Clean exit.\n")

