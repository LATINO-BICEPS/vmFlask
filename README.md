# vmFlask

A simple flask webapp designed to start/shutdown specific libvirt VMs and start up the PC via the WebGUI. Designed to run on a low-power device such as a Raspberry Pi.

This was primarily made to help less tech-savvy people like my Dad to be able to remote into a VM on my PC with a click of a button. The PC is normally powered off to save on power so this all-in-one-solution is very convenient.

# Features

* Start/Stop a VM via the WebGUI
* If the computer is not powered on yet, it will automatically switch it on via the TPLink HS110 SmartPlug (Turn "Restore Power on AC Loss" in BIOS) then starts the VM
* If the user is done using the VM and shuts down via the WebGUI, all while someone else working on the PC at the same time, a message box will appear on the host alerting them to cancel the shutdown. There is a timeout of 60 seconds before it will automatically power off completely.

# Quick Start

Ensure that you are able to SSH in using SSH keys.

Run `web.py` as a daemon:
```
screen -dmS "flaskServer" python3 web.py
```
Add it to crontab via `crontab -e` to automatically start flask on startup.

