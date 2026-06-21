import json
import os
from cartesia import Cartesia

# Configuration variables
API_KEY = "YOUR_API_KEY"
VOICE_ID = "SELECTED_VOICE_ID"
LANGUAGE_CODE = "LANGUAGE_CODE" # eg. "fi" for Finnish


OUTPUT_DIR = "new_wav"

# Ensure the output directory exists so it doesn't crash
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize client
client = Cartesia(api_key=API_KEY)

# Load your sentences
with open("prompts.json", "r", encoding="utf-8") as f:
    prompts = json.load(f)

# Process files
for filename, text in prompts.items():
    # Replace the .txt extension with .wav and prepend the output directory
    wav_filename = os.path.join(OUTPUT_DIR, filename.replace(".txt", ".wav"))
    
    try:
        # Generate the audio
        response = client.tts.generate(
            model_id="sonic-3.5",
            transcript=text,
            voice={
                "mode": "id",
                "id": VOICE_ID
	        },
            language=LANGUAGE_CODE,
            output_format={
                "container": "wav",
                "encoding": "pcm_s16le",
                "sample_rate": 16000
            },
        )        
        response.write_to_file(wav_filename)

        print(f"Successfully created: {wav_filename}")
        
    except Exception as e:
        # Explicit error reporting as requested
        print(f"Failed to generate {wav_filename}. Error: {e}")