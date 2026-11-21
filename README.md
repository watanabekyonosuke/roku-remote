# roku-remote

A sleek TUI remote control for Roku TVs. Control your TV from the terminal.

## Install

```
pip install roku-remote
```

Or with [uv](https://docs.astral.sh/uv/):

```
uvx roku-remote
```

## Usage

```x
roku-remote                      # auto-discovers Roku TVs on your network
roku-remote --ip 192.168.1.100   # connect to a specific IP
roku-remote --scan               # list all Roku devices on the network
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Arrow keys | Navigate |
| Enter | Select / OK |
| Escape | Back |
| Space | Play / Pause |
| h | Home |
| b | Back |
| r | Rewind |
| f | Fast forward |
| +/- | Volume up/down |
| m | Mute |
| i | Info |
| s | Search |
| t | Type text (for keyboard input on TV) |
| q | Quit |

Click any app in the right panel to launch it. All installed apps and HDMI inputs are detected automatically.

## How It Works

Uses Roku's [External Control Protocol (ECP)](https://developer.roku.com/docs/developer-program/debugging/external-control-api.md) -- a local HTTP API that Roku TVs expose on port 8060. Device discovery uses SSDP (the same protocol your phone's Roku app uses).

No accounts, no cloud, no tracking. Everything stays on your local network.

## Requirements

- Python 3.11+
- A Roku TV on the same network
