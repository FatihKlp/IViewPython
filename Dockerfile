FROM nvidia/cuda:11.8.0-base-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    ffmpeg \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

EXPOSE 10000
CMD ["gunicorn", "-w", "4", "--threads", "2", "-b", "0.0.0.0:10000", "--timeout", "240", "src.api.main:app"]
