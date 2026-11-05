"""Sarathi coach API: POST /api/score with the recorded audio as the body and
the verse id in ?v=2.47. Returns a mark for every word of the verse.

Audio is decoded in memory, scored and dropped; nothing is written to disk.
Standard library HTTP server; one scoring job at a time keeps memory flat.
"""
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import align

WORDS = json.load(open(os.environ.get("SARATHI_WORDS", "/app/practice-words.json"), encoding="utf-8"))
MAX_BYTES = 4 * 1024 * 1024
MAX_SECONDS = 75
CLEAR, CLOSE, PASS_SHARE = -1.5, -2.5, 0.85
JOB = threading.Semaphore(1)
ORIGINS = set(filter(None, os.environ.get("SARATHI_ORIGINS", "https://gita.dhirajmakam.com").split(",")))


def mark(g):
    return "clear" if g >= CLEAR else "close" if g >= CLOSE else "missed"


class Handler(BaseHTTPRequestHandler):
    server_version = "sarathi-coach"

    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=True).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        origin = self.headers.get("Origin")
        if origin in ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        origin = self.headers.get("Origin")
        if origin in ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Methods", "POST")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if urlparse(self.path).path == "/api/health":
            return self._send(200, {"ok": True})
        self._send(404, {"error": "not_found"})

    def do_POST(self):
        url = urlparse(self.path)
        if url.path != "/api/score":
            return self._send(404, {"error": "not_found"})
        vid = (parse_qs(url.query).get("v") or [""])[0]
        if vid not in WORDS:
            return self._send(400, {"error": "unknown_verse"})
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0 or n > MAX_BYTES:
            return self._send(413, {"error": "too_large", "message": "Keep the recording under a minute."})
        data = self.rfile.read(n)
        audio = align.load_audio(data)
        secs = len(audio) / align.BUNDLE.sample_rate
        if secs < 1.0:
            return self._send(422, {"error": "too_short", "message": "That recording was too short. Recite the whole verse."})
        if secs > MAX_SECONDS:
            return self._send(413, {"error": "too_long", "message": "Keep the recording under a minute."})
        if not JOB.acquire(timeout=30):
            return self._send(503, {"error": "busy", "message": "The coach is busy. Try again in a moment."})
        try:
            t = time.time()
            res = align.score(WORDS[vid], audio)
        finally:
            JOB.release()
        words = [dict(r, mark=mark(r["gop"])) for r in res]
        clear = sum(1 for w in words if w["mark"] == "clear")
        missed = sum(1 for w in words if w["mark"] == "missed")
        share = clear / len(words) if words else 0
        self._send(200, {"verse": vid, "words": words, "clearShare": round(share, 3), "missed": missed,
                         "good": share >= PASS_SHARE and missed == 0, "seconds": round(secs, 1),
                         "took": round(time.time() - t, 2)})

    def log_message(self, fmt, *args):  # no request logging: no audio metadata kept
        pass


if __name__ == "__main__":
    align.model()  # load once at start
    port = int(os.environ.get("PORT", "8000"))
    print("sarathi-coach listening on", port, flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
