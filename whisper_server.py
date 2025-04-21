import os
import uuid
import shutil
import warnings
from flask import Flask, request, jsonify
import whisper

# -------- Configuration & Logging --------
# Suppress FP16 warning on CPU
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")

# Log environment PATH and ffmpeg location
print("▶ Environment PATH:", os.environ.get("PATH"), flush=True)
ffmpeg_path = shutil.which("ffmpeg") or os.environ.get("FFMPEG_BINARY")
print("▶ ffmpeg path:", ffmpeg_path, flush=True)

# Optionally override ffmpeg binary via environment variable
if "FFMPEG_BINARY" in os.environ:
    os.environ["FFMPEG_BINARY"] = os.environ["FFMPEG_BINARY"]
elif ffmpeg_path:
    os.environ["FFMPEG_BINARY"] = ffmpeg_path

# -------- Flask & Whisper Setup --------
app = Flask(__name__)
# Load Whisper model (choose base/small/medium/large via MODEL_SIZE env var)
model_size = os.environ.get("MODEL_SIZE", "base")
print(f"Loading Whisper model: {model_size}", flush=True)
model = whisper.load_model(model_size)

@app.route("/analyze", methods=["POST"])
def analyze():
    # Expect audio file under 'audio'
    audio_file = request.files.get('audio')
    if not audio_file:
        return jsonify({"error": "No audio file provided"}), 400

    # Generate unique temp filename
    unique_name = f"audio_{uuid.uuid4().hex}.wav"
    temp_path = os.path.join('/tmp', unique_name)

    # Save uploaded file
    audio_file.save(temp_path)

    # Transcribe with Whisper
    try:
        result = model.transcribe(temp_path, language="ko")
        text = result.get('text', '')
    except Exception as e:
        # Cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({"error": str(e)}), 500

    # Remove temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)

    return jsonify({"text": text})

if __name__ == "__main__":
    # Use PORT env var if provided (Render.com sets it)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
