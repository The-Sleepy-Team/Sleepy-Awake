"""
File: pwm-stop-module.py
Course: Senior Design Project - CSE 181B / EECS 159B
Authors:    Michael Ishimoto
            Tyler Hom
            Ji Yeon Kim
            David Tran
"""

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD);	# Setting up GPIO pins
GPIO.setup(13, GPIO.OUT);   # GPIO pin 27

p = GPIO.PWM(13, 20000);
p.stop();

GPIO.setup(18, GPIO.OUT);   # GPIO pin 24
p = GPIO.PWM(18, 20000);
p.stop();

GPIO.cleanup();
