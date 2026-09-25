from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from proxy_llm.router import Doorman

PORT = 8787
DOOR = Doorman()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        print(f"[proxy] {self.address_string()} {fmt % args}")

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            return self._json(200, {"ok": True, "service": "proxy-llm-inteligente"})
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length)
        try:
            body = json.loads(raw.decode() or "{}")
        except json.JSONDecodeError:
            return self._json(400, {"error": "json inválido"})

        if path != "/v1/chat/completions":
            return self._json(404, {"error": "not found"})

        messages = body.get("messages") or []
        policy = body.get("policy") or "auto"
        out = DOOR.route(messages, policy=policy)
        tokens = int(out.get("tokens") or 0)
        payload = {
            "id": "chatcmpl-proxy",
            "object": "chat.completion",
            "model": f"proxy-{out['route']}",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": out["answer"]},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": tokens,
                "total_tokens": tokens,
            },
            "route": out["route"],
        }
        self._json(200, payload)

    def _json(self, code: int, data: dict) -> None:
        blob = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(blob)))
        if "route" in data:
            self.send_header("X-Proxy-Route", str(data["route"]))
        self.end_headers()
        self.wfile.write(blob)


def main() -> None:
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"proxy em http://127.0.0.1:{PORT}  (GET /health, POST /v1/chat/completions)")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
