"""Roku External Control Protocol (ECP) client."""

import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


class RokuClient:
    """HTTP client for the Roku ECP API."""

    def __init__(self, ip: str):
        self.ip = ip
        self.base = f"http://{ip}:8060"

    def post(self, path: str) -> bool:
        try:
            req = urllib.request.Request(f"{self.base}/{path}", method="POST")
            urllib.request.urlopen(req, timeout=2)
            return True
        except Exception:
            return False

    def get(self, path: str) -> str | None:
        try:
            resp = urllib.request.urlopen(f"{self.base}/{path}", timeout=2)
            return resp.read().decode()
        except Exception:
            return None

    def keypress(self, key: str) -> bool:
        return self.post(f"keypress/{key}")

    def type_char(self, ch: str) -> bool:
        encoded = urllib.parse.quote(ch)
        return self.post(f"keypress/Lit_{encoded}")

    def launch(self, app_id: str) -> bool:
        return self.post(f"launch/{app_id}")

    def active_app(self) -> str:
        xml = self.get("query/active-app")
        if xml:
            tree = ET.fromstring(xml)
            app = tree.find("app")
            if app is not None and app.text:
                return app.text
        return "Home"

    def power_state(self) -> str:
        xml = self.get("query/device-info")
        if xml:
            tree = ET.fromstring(xml)
            return tree.findtext("power-mode", "Unknown")
        return "Unreachable"
