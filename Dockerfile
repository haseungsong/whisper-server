FROM python:3.10-slim

# 필수 패키지 설치
RUN apt-get update && apt-get install -y ffmpeg git

# 작업 디렉토리
WORKDIR /app

# 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 소스 코드 복사
COPY . .

# 포트 환경변수
ENV PORT=5000

# ✅ Gunicorn으로 Flask 실행 (핵심)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "whisper_server:app"]
