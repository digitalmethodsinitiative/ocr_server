FROM python:3.8-buster

# Set working Dir
WORKDIR /app/

# Copy application
COPY . /app/

# RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get update && apt-get install libgl1 -y

# Install pixplot and additional python libraries
RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt

# Or Start gunicorn server on startup
CMD ["python", "-m", "gunicorn", "--worker-tmp-dir", "/dev/shm", "--workers=1", "--threads=4", "--worker-class=gthread", "--log-level=debug", "--reload", "--bind", "0.0.0.0:80", "server:app"]
