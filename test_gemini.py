import os
import re
import google.generativeai as genai
from gtts import gTTS
from pydub import AudioSegment
import tempfile
import subprocess

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Pick a fast, supported model
model = genai.GenerativeModel("models/gemini-2.5-flash")

def clean_text(text):
    """Remove markdown, emojis, and other unwanted symbols."""
    text = re.sub(r'[*_#`~]+', '', text)
    text = re.sub(r'[^\w\s,.!?\'-]', '', text)
    return text.strip()

prompt = input("You: ")

# Start streaming response
response_stream = model.generate_content(
    prompt,
    stream=True
)

full_text = ""

for chunk in response_stream:
    if chunk.text:
        text_piece = clean_text(chunk.text)
        print(text_piece, end="", flush=True)
        full_text += " " + text_piece

        if text_piece.strip():
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_mp3:
                tts = gTTS(text_piece)
                tts.save(tmp_mp3.name)
                tmp_wav = tmp_mp3.name.replace(".mp3", ".wav")
                AudioSegment.from_mp3(tmp_mp3.name).export(tmp_wav, format="wav")
                subprocess.run(["aplay", tmp_wav], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print("\n\nDone.")
