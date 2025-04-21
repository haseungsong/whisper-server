# Python 3.10을 기반으로 하는 이미지
FROM python:3.10-slim

# 시스템 패키지 업데이트 및 ffmpeg 설치
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 Python 패키지 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . /app/

# 앱 실행
CMD ["gunicorn", "server:app", "--timeout", "60", "--preload"]
