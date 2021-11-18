import subprocess
# from dotenv import load_dotenv
# # pip install python-dotenv
# load_dotenv()

# import os
# token = os.environ.get("api-token")
# print(token)
user = "collin@"
hostname = "192.168.1.198" # the VM Host (my PC)
ssh = subprocess.Popen(["ssh", user + hostname],
                             stdin=subprocess.PIPE, 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE, 
                             universal_newlines=True, 
                             bufsize=0)

sudo = subprocess.Popen(["sudo", "-S", "echo", "Hello"],
                              stdin=subprocess.PIPE, 
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, 
                             universal_newlines=True, 
                             bufsize=0)
output = sudo.communicate("#Hong071915#")
ssh.stdin.write("echo 'this is after the sudo'")
ssh.stdin.close()
print(output[0])

for line in ssh.stdout:
    print(line)

# cmd = "sudo ps -A|grep 'process_name'"
# ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
# output = ps.communicate("#Hong071915#\n")
# print(output)