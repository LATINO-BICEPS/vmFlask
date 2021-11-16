# vmFlask
A simple flask webapp designed to turn on/off specific libvirt VMs.

# Quick Start

Run `web.py` as a daemon:
```
screen -dmS "flaskServer" python3 web.py
```
Add it to crontab via `crontab -e` to automatically start flask on startup.

