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

# Whisper 모델 로딩
model_size = os.environ.get("MODEL_SIZE", "tiny")
print(f"▶ Loading Whisper model: {model_size}", flush=True)
model = whisper.load_model(model_size)


# ✅ 기본 health check 라우트 (컨테이너가 죽지 않게 유지)
@app.route("/", methods=["GET"])
def health():
    return "🟢 Whisper API is running!", 200


# ✅ 실제 분석 라우트
@app.route("/analyze", methods=["POST"])
def analyze():
    audio_file = request.files.get("audio")
    if not audio_file:
        return jsonify({"error": "No audio file provided"}), 400

    # Create temp path
    filename = f"audio_{uuid.uuid4().hex}.wav"
    temp_path = os.path.join("/tmp", filename)
    audio_file.save(temp_path)

    try:
        result = model.transcribe(temp_path, language="ko")
        text = result.get("text", "")
    except Exception as e:
        os.remove(temp_path)
        return jsonify({"error": str(e)}), 500

    os.remove(temp_path)
    return jsonify({"text": text})


# ✅ 로컬 테스트용 (Railway는 gunicorn 사용 권장)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
