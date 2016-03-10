"""
File: lux-conversion-test-module.py
Course: Senior Design Project - CSE 181B / EECS 159B
Authors:    Michael Ishimoto
            Tyler Hom
            Ji Yeon Kim
            David Tran
"""

import spidev
import time
import os

spi = spidev.SpiDev();
spi.open(0,0);

def ReadChannel(channel):
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    return data

while True:
    value = ReadChannel(1);
    vOut = float(value) * 0.00322265625;
    lux = 500 / (10 * ((3.3 - vOut) / vOut));
    print("Channel 1 value: " + str(lux));
