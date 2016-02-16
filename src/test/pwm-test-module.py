"""
File: pwm-test-module.py
Course: Senior Design Project - CSE 181B / EECS 159B
Authors:    Michael Ishimoto
            Tyler Hom
            Ji Yeon Kim
            David Tran
"""

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD);	# Setting up GPIO pins
GPIO.setup(11, GPIO.OUT);   # GPIO pin 17
GPIO.setup(13, GPIO.OUT);   # GPIO pin 22

GPIO.output(11, 1);	# 0 to open, 1 to close
p = GPIO.PWM(13, 20000);
p.start(100);
input('Press return to stop:');
p.stop();
GPIO.cleanup();
