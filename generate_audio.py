import os
import wave
import sys
from google import genai
from google.genai import types

# 1. API Key Setup
api_key = os.environ.get("GEMINI_API_KEY")
default_key = "AIzaSyDStjE_IOWgo7NWUSqrxHi3KBki2Rfyk0k"
if not api_key or not api_key.startswith("AIza"):
    api_key = default_key

client = genai.Client(api_key=api_key)

narration_text = (
    "In 1962, three men pulled off the impossible: escaping from Alcatraz, "
    "the most inescapable fortress on Earth. "
    "Frank Morris and the Anglin brothers spent months secretly chipping through concrete walls "
    "using nothing but sharpened cafeteria spoons. "
    "To fool the night guards, they sculpted fake human heads from soap, toilet paper, and real hair, "
    "tucking them into their beds. "
    "In the dead of night, they slipped into the utility pipes, climbed to the rain-soaked roof, "
    "and inflated a makeshift raft made from fifty stolen raincoats. "
    "They launched into the freezing, treacherous waters of San Francisco Bay, and vanished forever. "
    "Did they survive? To this day, the case remains unsolved."
)

prompt_content = f"""Read the following transcript based on the audio profile and director's note.

# Audio Profile
A young, casual YouTube storyteller. The voice is completely effortless, slightly dry, and relaxed. 
Zero pressure, no dramatic acting, just a smooth, natural speaking voice.

# Director's note
Style: Flat affect, minimal pitch variation, dry delivery. Pace: Fast, energetic, no dead air. 
Sentences overlap slightly. Accent: American (General).

## Scene:
A casual bedroom studio. A young guy is calmly explaining an incredible history story to his audience with a relaxed, dry delivery.

## Transcript:
{narration_text}"""

contents = [
    types.Content(
        role="user",
        parts=[types.Part.from_text(text=prompt_content)],
    ),
]

generate_content_config = types.GenerateContentConfig(
    temperature=0.85,
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Achird"
            )
        )
    ),
)

print("Connecting to Gemini and generating Achird audio...")

try:
    response = client.models.generate_content(
        model="gemini-3.1-flash-tts-preview",
        contents=contents,
        config=generate_content_config,
    )
except Exception as e:
    print(f"Primary API key error: {e}. Retrying with fallback...")
    client = genai.Client(api_key=default_key)
    response = client.models.generate_content(
        model="gemini-3.1-flash-tts-preview",
        contents=contents,
        config=generate_content_config,
    )

if not response.candidates:
    print("No candidates returned!")
    sys.exit(1)

part = response.candidates[0].content.parts[0]
if part.inline_data and part.inline_data.data:
    raw_audio = part.inline_data.data
    out_file = "/Users/vinaybt/Downloads/history-pixel-shorts/audio/alcatraz_voiceover.wav"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    
    with wave.open(out_file, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(raw_audio)
        
    frames = len(raw_audio) // 2
    duration_sec = frames / 24000.0
    print(f"SUCCESS! Audio saved to: {out_file}")
    print(f"Duration: {duration_sec:.2f} seconds")
else:
    print("No audio data returned in response.")
    sys.exit(1)
