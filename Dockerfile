# FROM python:3.8-buster
FROM nvidia/cuda:12.1.1-runtime-ubuntu20.04

# Set working Dir
WORKDIR /app/

# Copy application
COPY . /app/

# RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -yq \
    libgl1 \
    libglib2.0-0 \
    python3 \
    pip

# Install pixplot and additional python libraries
RUN python3 -m pip install --upgrade pip && python3 -m pip install -r requirements.txt

# Download the models
RUN python3 helpers/download_models.py --models paddle_ocr

# Create data directory for output
RUN mkdir /app/data/
RUN mkdir /app/temp/

# Or Start gunicorn server on startup
CMD ["python3", "-m", "gunicorn", "--worker-tmp-dir", "/dev/shm", "--workers=1", "--threads=4", "--worker-class=gthread", "--log-level=debug", "--reload", "--bind", "0.0.0.0:80", "server:app"]
