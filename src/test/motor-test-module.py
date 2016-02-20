"""
File: motor-test-module.py
Course: Senior Design Project - CSE 181B / EECS 159B
Authors:    Michael Ishimoto
            Tyler Hom
            Ji Yeon Kim
            David Tran
"""

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD);	# Setting up GPIO pins
GPIO.setup(16, GPIO.OUT);   # GPIO pin 23
GPIO.setup(18, GPIO.OUT);   # GPIO pin 24

GPIO.output(16, 0);	# 0 to spin clockwise, 1 to spin counter-clockwise
p = GPIO.PWM(18, 20000);
p.start(100);
input('Press return to stop:');
p.stop();
GPIO.cleanup();
