# Base image olarak Python 3.10 kullan (3.12 veya 3.11 isterseniz güncelleyebilirsiniz)
FROM python:3.10-slim

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

# spaCy ve modelini yükle
RUN python -m spacy download en_core_web_md

# Kodları container'a kopyala
COPY . .

# Port tanımlaması
EXPOSE 10000

# Çalıştırma komutu (Flask uygulaması için)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:10000", "--timeout", "180", "src.api.main:app"]