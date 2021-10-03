import subprocess
import time

time.sleep(1)

cmd = ["/home/pi/pi_nfcrd/env/bin/python", "/home/pi/pi_nfcrd/main.py"]

subprocess.Popen( cmd )

count = 0
while True:
    print("manage : " + str(count) + " sec")
    time.sleep(5)
    count += 5
