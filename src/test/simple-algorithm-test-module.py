"""
File: simple-algorithm-test-module.py
Course: Senior Design Project - CSE 181B / EECS 159B
Authors:    Michael Ishimoto
            Tyler Hom
            Ji Yeon Kim
            David Tran
"""

import subprocess
import json
import urllib2
import json
import time

desiredTemp = 70.0; # This is in Fahrenheit
                        # All temperature values will be in Fahrenheit

# Main method of the program which will run first when file is executed
def main():
    # Setting the next hour
    nextHour = getNextHour();

    # Infinite loop to constantly check temperatures
    while True:
        # if str(time.localtime().tm_hour) == str(nextHour):
            nextHour = getNextHour();
            simpleAlgorithm();

# Method for retrieving an EnOcean's sensor state / value
# Returns the state as a string if the specified sensor is found, returns false otherwise
def retrieveEnOceanState(sensor):
    # Obtaining EnOcean sensor values
    output = subprocess.Popen(['/opt/fhem/fhem.pl', 'localhost:7072', 'jsonList'], stdout=subprocess.PIPE).communicate()[0]
    data = json.loads(output);
    devices = data['Results'][3]['devices']
    for device in devices:
        if device['DEF'] == '018B79C1' and sensor == 'EDWS': # Door sensor
            return device['STATE'] ;
        if device['DEF'] == '01831695' and sensor == 'STM': # Temperature sensor
            return device['STATE'];

    return False;

# Method for getting the current temperature in the specified state and city
# Returns the current fahrenheit temperature as a float
def getCurrentTemperature(state, city):
    # Making an API call to weatherunderground
    f = urllib2.urlopen('http://api.wunderground.com/api/12d1b60c95f74d26/geolookup/conditions/q/' + state + '/' + city + '.json');

    # Parsing the returned JSON
    json_string = f.read();
    parsed_json = json.loads(json_string);
    location = parsed_json['location']['city'];
    temp_f = parsed_json['current_observation']['temp_f'];
    # print "Current temperature in %s is: %s" % (location, temp_f)
    f.close()

    return temp_f;

# Method for getting the next hour from the current hours
# Returns the next hour as an integer
def getNextHour():
    currentHour = time.localtime().tm_hour;

    if (currentHour == 23):
        return 0;

    return currentHour + 1;

# Method for checking the temperatures and taking actions based on Results
def simpleAlgorithm():
    insideTemp = float(retrieveEnOceanState('STM')) * 1.8 + 32;
    outsideTemp = getCurrentTemperature('CA', 'Irvine');

    # print(type(insideTemp));
    # print(type(outsideTemp));
    # print(type(desiredTemp));

    print('Inside temp: ' + str(insideTemp));
    print('Outside temp: ' + str(outsideTemp));
    print('Desired temp: ' + str(desiredTemp));

    if insideTemp > desiredTemp:
        if outsideTemp < insideTemp:
            print('Opening window...');
        else:
            print('Closing window');
    elif insideTemp < desiredTemp:
        if outsideTemp > insideTemp:
            print('Opening window...');
        else:
            print('Closing window');

main(); # Call to main method so that it runs first
