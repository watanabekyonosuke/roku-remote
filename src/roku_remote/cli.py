"""CLI entry point for roku-remote."""

import argparse
import json
import sys
from pathlib import Path

from roku_remote.discovery import discover_roku, get_device_info, get_installed_apps, get_input_names
from roku_remote.ecp import RokuClient
from roku_remote.app import RokuRemote

CACHE_DIR = Path.home() / ".config" / "roku-remote"
CACHE_FILE = CACHE_DIR / "device.json"


def save_device(ip: str, name: str) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps({"ip": ip, "name": name}))


def load_device() -> dict | None:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text())
        except (json.JSONDecodeError, KeyError):
            return None
    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="roku-remote",
        description="TUI remote control for Roku TVs",
    )
    parser.add_argument(
        "--ip",
        help="Roku TV IP address (skips auto-discovery)",
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Scan for Roku devices and exit",
    )
    parser.add_argument(
        "--forget",
        action="store_true",
        help="Clear cached device and re-scan",
    )
    args = parser.parse_args()

    if args.forget:
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
            print("Cached device cleared.")
        else:
            print("No cached device.")
        if not args.scan:
            sys.exit(0)

    if args.scan:
        print("Scanning for Roku devices...")
        devices = discover_roku()
        if not devices:
            print("No Roku devices found.")
            sys.exit(1)
        for d in devices:
            print(f"  {d['name']} — {d['model']} ({d['ip']})")
        sys.exit(0)

    ip = args.ip
    device_name = "Roku"

    # Try cached device if no IP specified
    if not ip:
        cached = load_device()
        if cached:
            ip = cached["ip"]
            device_name = cached["name"]
            info = get_device_info(ip)
            if info:
                device_name = info["name"]
                print(f"Using cached device: {device_name} ({ip})")
            else:
                print(f"Cached device {ip} unreachable, scanning...")
                ip = None

    if not ip:
        print("Scanning for Roku devices...")
        devices = discover_roku()
        if not devices:
            print("No Roku devices found. Use --ip to specify manually.")
            sys.exit(1)
        if len(devices) == 1:
            ip = devices[0]["ip"]
            device_name = devices[0]["name"]
            print(f"Found: {device_name} ({ip})")
        else:
            print("Found multiple devices:")
            for i, d in enumerate(devices, 1):
                print(f"  [{i}] {d['name']} — {d['model']} ({d['ip']})")
            while True:
                choice = input("Select device: ").strip()
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(devices):
                        ip = devices[idx]["ip"]
                        device_name = devices[idx]["name"]
                        break
                except ValueError:
                    pass
                print("Invalid choice.")

        save_device(ip, device_name)
    elif not load_device():
        # Cache manually specified IP too
        info = get_device_info(ip)
        if info:
            device_name = info["name"]
        else:
            print(f"Warning: Could not reach {ip}")
        save_device(ip, device_name)

    client = RokuClient(ip)
    apps = get_installed_apps(ip)
    inputs = get_input_names(ip)

    app = RokuRemote(client, apps, inputs, device_name)
    app.run()
