"""
File: predictive-algorithm-test-module.py
Course: Senior Design Project - CSE 181B / EECS 159B
Authors:    Michael Ishimoto
            Tyler Hom
            Ji Yeon Kim
            David Tran
"""

import time

desiredTemp = 57;

def main():
    high = 0;
    highPos = 0;
    low = 150;
    lowPos = 0;
    storedPredictions = [];
    i = 0;

    # Determining the highest temperature and lowest temperature and their positions
    file_object = open('predictions.txt', 'r'); # Reading an existing file
    for line in file_object:
        predictions = line.split(',');
        prediction = predictions[1].replace(' ', '');
        prediction = prediction.replace('\n', '');
        storedPredictions.append(prediction);
        print(prediction);
        if int(prediction) > int(high):
            high = prediction;
            highPos = i;
        if int(prediction) < int(low):
            low = prediction;
            lowPos = i;
        i += 1;

    if desiredTemp > high:
        # Open window from 6am to 3pm
        # Close window at 3pm
        print('lol');
    elif desiredTemp < low:
        # Keep window closed until 4pm
        # Open at 4pm
        # Close at 6am next day
        print('stuff');
    else:
        if abs(desiredTemp - high) > abs(desiredTemp - low):
            # Open at 6pm
            # Close at 9pm
            print('lol');
        else:
            # Open at 9am
            # Close at 12pm
            print('ide');

main(); # Call to main method so that it runs first
