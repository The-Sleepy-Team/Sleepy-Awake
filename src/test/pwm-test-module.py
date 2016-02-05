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
GPIO.setup(11, GPIO.OUT);
GPIO.setup(12, GPIO.OUT);

GPIO.output(11, 0);	# 0 to open, 1 to close
p = GPIO.PWM(12, 20000);
p.start(100);
input('Press return to stop:');
p.stop();
GPIO.cleanup();
