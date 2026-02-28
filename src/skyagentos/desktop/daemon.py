from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from uuid import uuid4


class DesktopHandler(BaseHTTPRequestHandler):
    def _json(self, code: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/execute":
            return self._json(404, {"error": "not found"})
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")

        action = payload.get("action", "noop")
        dry = os.getenv("SKYAGENT_DRY_RUN", "false").lower() == "true"
        artifact_root = Path(os.getenv("DESKTOP_ARTIFACT_ROOT", "workspace_artifacts/desktop"))
        artifact_root.mkdir(parents=True, exist_ok=True)

        screenshot = artifact_root / f"desktop_{uuid4().hex[:8]}.txt"
        screenshot.write_text(f"simulated-{action}", encoding="utf-8")

        if dry:
            return self._json(
                200,
                {
                    "status": "ok",
                    "runtime": "desktop",
                    "action": action,
                    "result": "simulated",
                    "evidence": str(screenshot),
                },
            )

        return self._json(
            200,
            {"status": "ok", "runtime": "desktop", "action": action, "evidence": str(screenshot)},
        )


def run_desktop_daemon() -> None:
    host = os.getenv("DESKTOP_DAEMON_HOST", "0.0.0.0")
    port = int(os.getenv("DESKTOP_DAEMON_PORT", "8890"))
    srv = ThreadingHTTPServer((host, port), DesktopHandler)
    print(f"desktop-daemon listening on {host}:{port}")
    srv.serve_forever()


if __name__ == "__main__":
    run_desktop_daemon()
