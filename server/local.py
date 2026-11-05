"""Run Sarathi on your own computer: the built site and the coach on one port.

    python server/local.py        then open http://localhost:8080/practice/2/47/

localhost counts as a secure page, so the browser allows the microphone.
"""
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(os.path.dirname(HERE), "site")
os.environ.setdefault("SARATHI_WORDS", os.path.join(HERE, "practice-words.json"))
sys.path.insert(0, HERE)
import app  # noqa: E402
import align  # noqa: E402


class Local(app.Handler, SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        SimpleHTTPRequestHandler.__init__(self, *a, directory=SITE, **k)

    def do_GET(self):
        if urlparse(self.path).path.startswith("/api/"):
            return app.Handler.do_GET(self)
        return SimpleHTTPRequestHandler.do_GET(self)

    def send_error(self, code, message=None, explain=None):
        if code == 404 and os.path.exists(os.path.join(SITE, "404.html")):
            body = open(os.path.join(SITE, "404.html"), "rb").read()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().send_error(code, message, explain)


if __name__ == "__main__":
    if not os.path.isdir(SITE):
        sys.exit("No site yet. Run ./run-local.sh, which builds it first.")
    port = int(os.environ.get("PORT", "8080"))
    print("Loading the coach (the first run downloads a 1.2 GB model, then it is cached)...", flush=True)
    align.model()
    print("Ready: http://localhost:%d/practice/2/47/  (Ctrl+C to stop)" % port, flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Local).serve_forever()
