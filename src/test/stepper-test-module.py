"""
File: stepper-test-module.py
Course: Senior Design Project - CSE 181B / EECS 159B
Authors:    Michael Ishimoto
            Tyler Hom
            Ji Yeon Kim
            David Tran
"""

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD);	# Setting up GPIO pins
GPIO.setup(11, GPIO.OUT);   # GPIO pin 17
GPIO.setup(13, GPIO.OUT);   # GPIO pin 27
GPIO.output(11, 0);	# 0 to open, 1 to close
p = GPIO.PWM(13, 20000);

def main():
    print(time.localtime().tm_sec);
    motorTimer(5);
    print(time.localtime().tm_sec);

def motorTimer(desiredElapsedTime):
    for iteration in range (0, desiredElapsedTime):
        p.stop();
        time.sleep(0.001);
        p.start(100);
        time.sleep(1);

main();
