"""
File: enocean-test-module.py
Course: Senior Design Project - CSE 181B / EECS 159B
Authors:    Michael Ishimoto
            Tyler Hom
            Ji Yeon Kim
            David Tran
"""

# Code commented out uses telnet but that is based on events

# import telnetlib;
# import os;
#
# HOST = 'localhost';
# PORT = 7072;
#
# tn = telnetlib.Telnet();
# tn.open(HOST, PORT);
#
# tn.write('inform on\n');
#
# print("Before reading");
#
# while True:
#     # output = tn.read_until('\n');
#     output = tn.read_all();
#     print(output);

# Following code gets information exactly when you need it

import subprocess
import json

output = subprocess.Popen(['/opt/fhem/fhem.pl', 'localhost:7072', 'jsonList'], stdout=subprocess.PIPE).communicate()[0]
data = json.loads(output);

devices = data['Results'][3]['devices']
for device in devices:
    if device['DEF'] == '018B79C1': # Door sensor
        print(device['STATE']);
    if device['DEF'] == '01831695': # Temperature sensor
        print(device['STATE']);


# print(data['Results'][3]['devices'][0]['STATE']); # 0 is for the door sensor
# print(data['Results'][3]['devices'][1]['STATE']); # 1 is for the temperature sensor
# print(output);
