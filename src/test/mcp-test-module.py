"""
File: mcp-test-module.py
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
    value = ReadChannel(0);

    print("Channel 0 value: " + str(value));
