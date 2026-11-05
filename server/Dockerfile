# Sarathi coach: scores recitations by forced alignment (Meta MMS aligner).
# CPU only. The 1.2 GB model is baked into the image so the first request is fast.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir numpy torch torchaudio --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple
WORKDIR /app
COPY align.py app.py practice-words.json ./
RUN python -c "import align; align.model()"
ENV PORT=8000 SARATHI_WORDS=/app/practice-words.json OMP_NUM_THREADS=2
EXPOSE 8000
CMD ["python", "app.py"]
