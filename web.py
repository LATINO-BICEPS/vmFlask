from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import tkinter as tk
from tkinter import TclError, messagebox
# sudo apt-get install python3-tk 
import subprocess
import time
# control smartplugs
# modified from https://github.com/LATINO-BICEPS/tplink-smartplug-graphite/blob/master/power.py
import socket
import json
import ast
from struct import pack

# courtesy of https://www.youtube.com/watch?v=v2TSTKlrPwo
app = Flask('flaskshell')

ip_whitelist = ["127.0.0.1", "192.168.1.244"]
vmStatus = "Offline"
hostname = "192.168.1.244"
user = "collin@"
logDir = "./logs/logfile.txt"
timeout = 2*1000
vmName = "win10-2"

# Set target IP, port and command to send
smartplugIP = "192.168.1.230"
port = 9999


def encrypt(string):
    key = 171
    result = pack(">I", len(string))
    for i in string:
        a = key ^ ord(i)
        key = a
        result += bytes([a])
    return result

def decrypt(string):
    key = 171
    result = ""
    for i in string:
        a = key ^ i
        key = i
        result += chr(a)
    return result

# Send command and receive reply
def send_hs_command(ip, port, cmd):  
    try:
        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        sock_tcp.settimeout(int(10))
        sock_tcp.connect((ip, port)) 
        sock_tcp.settimeout(None)
        sock_tcp.send(encrypt(cmd)) 
        data = sock_tcp.recv(2048) 
        sock_tcp.close()
        
        decrypted = decrypt(data[4:])
        return decrypted
    except socket.error:
        quit(f"Could not connect to host {ip}:{port}")
# returns true if smartplug is on
def isPoweredOff():
    global smartplugIP
    global port
    decrypted_data = send_hs_command(smartplugIP, port, '{"emeter":{"get_realtime":{}}}')
    decrypted_data_dict = ast.literal_eval(decrypted_data)
    # returns string from dictionary
    data = json.dumps(decrypted_data_dict)
    json_data = json.loads(data)
    emeter = json_data["emeter"]["get_realtime"]
    power = emeter["power_mw"]/1000
    if(power == 0):
        return True

def valid_ip():
    client = request.remote_addr
    if client in ip_whitelist:
        return True
    else:
        return False

def logOutput(output):
    # disable welcome messages to reduce junk logs sudo chmod -x /etc/update-motd.d/*
    global logDir
    # https://www.programiz.com/python-programming/time
    named_tuple = time.localtime() # get struct_time
    time_string = time.strftime("[%d/%m/%Y %H:%M:%S] ", named_tuple)
    f = open(logDir, "a")
    for line in output:
        f.write(time_string + line)
    f.close()

def turnOn(vmName):
    global hostname
    global user
    global smartplugIP
    global port
    # turn the computer on first if it's not on already
    if(isPoweredOff()):
        print("It is powered off.")
        #send_hs_command(smartplugIP, port, '{"system":{"set_relay_state":{"state":1}}}')
    else: print("It is powered on.")
    # ssh in then turn the vm on
    ssh = subprocess.Popen(["ssh", user + hostname],
                             stdin=subprocess.PIPE, 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE, 
                             universal_newlines=True, 
                             bufsize=0)
    ssh.stdin.write("virsh start {0}\n".format(vmName))
    ssh.stdin.write("sudo cpupower frequency-set -g performance")
    ssh.stdin.close()
    logOutput(ssh.stdout)
    print("{0} is starting.".format(vmName))

def turnOff(vmName):
    global logDir
    global timeout
    global smartplugIP
    global port
    # shutdown vm
    ssh = subprocess.Popen(["ssh", user + hostname],
                             stdin=subprocess.PIPE, 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE, 
                             universal_newlines=True, 
                             bufsize=0)
    ssh.stdin.write("virsh shutdown {0}\n".format(vmName))
    ssh.stdin.write("sleep 6")
    ssh.stdin.write("if virsh domstate {0} | grep 'running'; then virsh destroy win10-2; fi;".format(vmName))
    ssh.stdin.close()
    logOutput(ssh.stdout)
    print("{0} is shutting down.".format(vmName))
    # https://stackoverflow.com/questions/51647603/python-tkinter-destroy-window-after-time-or-on-click
    # warn user before shutting down PC
    try:
        w = tk.Tk()
        w.withdraw()
        w.after(timeout, w.destroy) # Destroy the widget after specified seconds
        if messagebox.showinfo('Shutting Down in {0}s'.format(timeout//1000), 'Are you still using the PC?'):
            w.destroy()
        logOutput(['PC is Still in Use\n',])
    except TclError:
        logOutput(["Shutting Down Now\n",])
        # gracefully shutdown PC first
        ssh = subprocess.Popen(["ssh", user + hostname],
                             stdin=subprocess.PIPE, 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE, 
                             universal_newlines=True, 
                             bufsize=0)
        ssh.stdin.write("shutdown now")
        time.sleep(10)
        #send_hs_command(smartplugIP, port, '{"system":{"set_relay_state":{"state":0}}}')

@app.route('/update', methods=['POST'])
def checkVMStatus():
    global vmStatus
    global hostname
    try:
        subprocess.check_output(["ping", "-c", "1", "192.168.122.64"])
        vmStatus = "Online"
        return jsonify('', render_template('status.html', x=vmStatus))
    except:
        vmStatus="Offline"
        return jsonify('', render_template('status.html', x=vmStatus))
    
@app.route('/', methods=['POST', 'GET'])
def index():
    global vmName
    if valid_ip():    
        if request.method == 'POST':
            if request.form.get('Turn On') == 'Turn On':
                turnOn(vmName)
            elif request.form.get('Turn Off') == 'Turn Off':
                turnOff(vmName)

        return render_template('index.html', x=vmStatus)
    else:
        return "Sorry but you are not permitted to view this page."

app.run(debug=True)
