# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt into the container
COPY requirements.txt /app/

# Install the necessary Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . /app/

# Set the environment variable for MODEL_SIZE to tiny (you can change this to 'base' or 'small' later)
ENV MODEL_SIZE=tiny

# Expose the port that the app will run on
EXPOSE 5000

