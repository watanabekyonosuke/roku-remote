"""CLI entry point for roku-remote."""

import argparse
import sys

from roku_remote.discovery import discover_roku, get_device_info, get_installed_apps, get_input_names
from roku_remote.ecp import RokuClient
from roku_remote.app import RokuRemote


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
    args = parser.parse_args()

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
    else:
        info = get_device_info(ip)
        if info:
            device_name = info["name"]
        else:
            print(f"Warning: Could not reach {ip}")

    client = RokuClient(ip)
    apps = get_installed_apps(ip)
    inputs = get_input_names(ip)

    app = RokuRemote(client, apps, inputs, device_name)
    app.run()
