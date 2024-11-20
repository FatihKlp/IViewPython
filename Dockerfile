# Base image olarak Python kullan
FROM python:3.9-slim

# Çalışma dizinini oluştur
WORKDIR /app

# Gereken OS bağımlılıklarını yükle (FFmpeg ve diğerleri)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Gereken Python bağımlılıklarını yükle
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Kodları container'a kopyala
COPY . .

# Port tanımlaması (Render genelde 5000'i varsayılan alır)
EXPOSE 5000

# Çalıştırma komutu (Flask uygulaması için)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.app:app"]
