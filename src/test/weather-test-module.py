"""
File: weather-test-module.py
Course: Senior Design Project - CSE 181B / EECS 159B
Authors:    Michael Ishimoto
            Tyler Hom
            Ji Yeon Kim
            David Tran
"""

import urllib2
import json

# Main method of the program which will run first when file is executed
def main():
    # Testing the functions
    state = 'CA';
    city = 'Irvine';
    currentTemp = getCurrentTemperature(city, state);
    print('currentTemp: ' + str(currentTemp));
    dayTemps = get24HrTemperatures(city, state);
    for i in range(len(dayTemps)):
        print('Temperature for hour ' + str(i) + ': ' + dayTemps[i]);

# Method for getting the current temperature in the specified state and city
# Returns the current fahrenheit temperature as a float
def getCurrentTemperature(state, city):
    # Making an API call to weatherunderground
    f = urllib2.urlopen('http://api.wunderground.com/api/12d1b60c95f74d26/geolookup/conditions/q/' + state + '/' + city + '.json');

    # Parsing the returned JSON
    json_string = f.read();
    parsed_json = json.loads(json_string);

    if len(parsed_json['response']) == 3:   # If a valid city / state was specified
        location = parsed_json['location']['city'];
        temp_f = parsed_json['current_observation']['temp_f'];
        # print "Current temperature in %s is: %s" % (location, temp_f)
        f.close()

        return temp_f;

    return 0;

# Method for getting the temperature for the next 24 hours in the specified state and city
# Returns the day's temperatures (in fahrenheit) as an array of integers
def get24HrTemperatures(state, city):
    # Making an API call to weatherunderground
    f = urllib2.urlopen('http://api.wunderground.com/api/12d1b60c95f74d26/hourly/q/' + state + '/' + city + '.json');

    # Parsing the returned JSON
    json_string = f.read();
    parsed_json = json.loads(json_string);

    if len(parsed_json['response']) == 3:   # If a valid city / state was specified
        # Storing the temperature information in an array
        forecast = []
        for i in range(24):
            forecast.append(parsed_json['hourly_forecast'][i]['temp']['english']);
        # for i in range(24):
        #     print "temperature for the hour %i: %s" % (i, forecast[i])
        f.close();

        return forecast;

    return ['0'];

main(); # Call to main method so that it runs first
