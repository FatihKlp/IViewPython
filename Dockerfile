# Base image olarak Python 3.9 kullan
FROM python:3.9-slim

# Çalışma dizinini oluştur
WORKDIR /app

# OS bağımlılıklarını yükle
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# TensorFlow için CPU modunu zorla
ENV CUDA_VISIBLE_DEVICES=""

# Gereken Python bağımlılıklarını yükle
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# spaCy modelini yükleyin
RUN pip install spacy && python -m spacy download en_core_web_md

# Kodları container'a kopyala
COPY . .

# Port tanımlaması
EXPOSE 10000

# Çalıştırma komutu (Flask uygulaması için)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:${PORT}", "--timeout", "180", "src.api.main:app"]