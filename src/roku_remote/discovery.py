"""SSDP discovery for Roku devices on the local network."""

import socket
import urllib.request
import xml.etree.ElementTree as ET


def discover_roku(timeout: float = 5.0) -> list[dict]:
    """Find Roku devices on the network via SSDP."""
    msg = (
        "M-SEARCH * HTTP/1.1\r\n"
        "HOST: 239.255.255.250:1900\r\n"
        'MAN: "ssdp:discover"\r\n'
        "ST: roku:ecp\r\n"
        f"MX: {int(timeout)}\r\n"
        "\r\n"
    ).encode()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    sock.sendto(msg, ("239.255.255.250", 1900))

    devices: list[dict] = []
    seen: set[str] = set()

    try:
        while True:
            data, addr = sock.recvfrom(1024)
            ip = addr[0]
            if ip in seen:
                continue
            seen.add(ip)

            info = get_device_info(ip)
            if info:
                devices.append(info)
    except socket.timeout:
        pass
    finally:
        sock.close()

    return devices


def get_device_info(ip: str) -> dict | None:
    """Query and validate a Roku device.

    Validates that the response contains expected Roku device-info fields
    (serial-number, software-version, is-tv/is-stick) to guard against
    rogue SSDP responders pretending to be Roku devices.
    """
    try:
        resp = urllib.request.urlopen(f"http://{ip}:8060/query/device-info", timeout=3)
        tree = ET.fromstring(resp.read())

        # Validate this is actually a Roku device — a rogue SSDP responder
        # could point us at an arbitrary HTTP server
        serial = tree.findtext("serial-number")
        software = tree.findtext("software-version")
        is_tv = tree.findtext("is-tv")
        is_stick = tree.findtext("is-stick")
        if not serial or not software or (is_tv is None and is_stick is None):
            return None

        return {
            "ip": ip,
            "name": tree.findtext("user-device-name", "Roku"),
            "model": tree.findtext("friendly-model-name", "Unknown"),
            "model_number": tree.findtext("model-name", ""),
            "serial": serial,
            "power": tree.findtext("power-mode", "Unknown"),
            "software": software,
            "network": tree.findtext("network-name", ""),
        }
    except Exception:
        return None


def get_installed_apps(ip: str) -> dict[str, str]:
    """Get installed apps from a Roku device. Returns {name: id}."""
    try:
        resp = urllib.request.urlopen(f"http://{ip}:8060/query/apps", timeout=3)
        tree = ET.fromstring(resp.read())
        apps = {}
        for app in tree.findall("app"):
            if app.get("type") == "appl" and app.text:
                apps[app.text] = app.get("id", "")
        return apps
    except Exception:
        return {}


def get_input_names(ip: str) -> dict[str, str]:
    """Get named HDMI/AV inputs. Returns {id: user-assigned name}."""
    try:
        resp = urllib.request.urlopen(f"http://{ip}:8060/query/apps", timeout=3)
        tree = ET.fromstring(resp.read())
        inputs = {}
        for app in tree.findall("app"):
            if app.get("type") == "tvin" and app.text:
                app_id = app.get("id", "")
                inputs[app_id] = app.text
        return inputs
    except Exception:
        return {}
