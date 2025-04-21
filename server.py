import os
import uuid
import shutil
import warnings
from flask import Flask, request, jsonify
import whisper
import logging

# -------- Configuration & Logging --------
# Suppress FP16 warning on CPU
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")

# Set up logging for better traceability
logging.basicConfig(level=logging.INFO)  # Changed from default to INFO for more detailed logging
logger = logging.getLogger(__name__)

# Log environment PATH and ffmpeg location
logger.info("▶ Environment PATH: %s", os.environ.get("PATH"))
ffmpeg_path = shutil.which("ffmpeg") or os.environ.get("FFMPEG_BINARY")
logger.info("▶ ffmpeg path: %s", ffmpeg_path)

# Optionally override ffmpeg binary via environment variable
if "FFMPEG_BINARY" in os.environ:
    os.environ["FFMPEG_BINARY"] = os.environ["FFMPEG_BINARY"]
elif ffmpeg_path:
    os.environ["FFMPEG_BINARY"] = ffmpeg_path

# -------- Flask & Whisper Setup --------
app = Flask(__name__)

# Whisper 모델 로딩
model_size = os.environ.get("MODEL_SIZE", "tiny")
logger.info("▶ Loading Whisper model: %s", model_size)
model = whisper.load_model(model_size)

# ✅ 기본 health check 라우트 (컨테이너가 죽지 않게 유지)
@app.route("/", methods=["GET"])
def health():
    logger.info("Health check received.")
    return "🟢 Whisper API is running!", 200

# ✅ 실제 분석 라우트
@app.route("/analyze", methods=["POST"])
def analyze():
    logger.info("Received analyze request.")
    
    audio_file = request.files.get("audio")
    if not audio_file:
        logger.error("No audio file provided")
        return jsonify({"error": "No audio file provided"}), 400

    # Create temp path
    filename = f"audio_{uuid.uuid4().hex}.wav"
    temp_path = os.path.join("/tmp", filename)
    audio_file.save(temp_path)

    try:
        logger.info("Transcribing audio file: %s", temp_path)
        result = model.transcribe(temp_path, language="ko")
        text = result.get("text", "")
        logger.info("Transcription result: %s", text)
    except Exception as e:
        logger.error("Error during transcription: %s", str(e))
        os.remove(temp_path)
        return jsonify({"error": "Internal Server Error"}), 500

    os.remove(temp_path)
    logger.info("Successfully processed audio file.")
    return jsonify({"text": text})

# ✅ 로컬 테스트용 (Railway는 gunicorn 사용 권장)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info("Starting the Flask app on port %d", port)
    # 디버그 모드 활성화
    app.run(host="0.0.0.0", port=port, debug=True)  # debug=True 추가
