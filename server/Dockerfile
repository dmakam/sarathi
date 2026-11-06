# Sarathi coach: scores recitations by forced alignment (Meta MMS aligner).
# CPU only. Uses the 8-bit copy of the model (model-int8.pt, made by quantize.py and
# copied in next to this file), which needs about a third of the memory of the full one
# and gave the same word marks in testing.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir numpy torch==2.15.0 torchaudio==2.11.1 --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple
WORKDIR /app
COPY align.py app.py practice-words.json model-int8.pt ./
ENV PORT=8000 SARATHI_WORDS=/app/practice-words.json SARATHI_MODEL=/app/model-int8.pt OMP_NUM_THREADS=1
EXPOSE 8000
CMD ["python", "app.py"]
