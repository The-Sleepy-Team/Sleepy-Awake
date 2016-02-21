"""
File: sleepy-awake-test.py
Course: Senior Design Project - CSE 181B / EECS 159B
Authors:    Michael Ishimoto
            Tyler Hom
            Ji Yeon Kim
            David Tran
"""

# Importing necessary libraries
import smtplib
import sys
import subprocess
import imaplib
import getpass
import email
import datetime
import time
import urllib2
import json
import spidev
import time
import os
import RPi.GPIO as GPIO
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Setting up spidev
spi = spidev.SpiDev();
spi.open(0,0);

# Setting up GPIO pins
# GPIO.cleanup();
GPIO.setmode(GPIO.BOARD);
GPIO.setup(11, GPIO.OUT);   # For the direction of the linear actuator
                            # GPIO pin 17
GPIO.setup(13, GPIO.OUT);   # To move the linear actuator
                            # 0 to open, 1 to close
                            # GPIO pin 27
GPIO.setup(16, GPIO.OUT);   # For the direction of the motor
                            # 0 to spin clockwise, 1 to spin counter-clockwise
                            # GPIO pin 23
GPIO.setup(18, GPIO.OUT);   # To have the motor spin
                            # GPIO pin 24
p = GPIO.PWM(13, 20000);    # 20kHz

# Creating global variables
rPiEmail            = 'sleepyraspberrypi@gmail.com';
rPiEmailPW          = '123abc123ABC';
mrWindowEmail       = 'sleepymrwindow@gmail.com';
WINDOW_POSITION     = 0;    # Position of the window, relative to openness
                            # Can take on any percentages (eg. 10% = 10, 75% = 75)
                            # 100 = 100% opened
MAX_MCP_VALUE       = 300;  # Max MCP value that the physical window can open
                            # 0 = 100% open
BLINDS_POSITION     = 0;    # Similar to WINDOW_POSITION
TEMPERATURE         = 0.0;  # Temperature will be in Fahrenheit
LIGHT_LEVEL         = 0;    # Still deciding on units
PRESET              = 1;    # The current preset
DESIRED_TEMP        = 0.0;  # The user's desired temperature

# Main method of the program which will run first when file is executed
def main():
    # Letting the user know the device is operational, especially useful for headless operation
    sendEmail('4084669915@txt.att.net', 'Raspberry Pi Connection', 'Raspberry Pi operating!'); # Temporary removing this because of annoyance

    # Setting the next minute
    nextMin = time.localtime().tm_min + 1;

    # Setting the next hour
    nextHour = getNextHour();

    # Infinite loop to constantly check email, preset file, and temperatures
    while True:
        # Checking the preset text file every minute
        # print(str(time.localtime().tm_hour) + ' ' + str(time.localtime().tm_min) + ' ' + str(time.localtime().tm_sec));
        if str(time.localtime().tm_min) == str(nextMin):
            nextMin = getNextMin(time.localtime().tm_hour, time.localtime().tm_min);
            checkPresetFile(time.localtime().tm_hour, time.localtime().tm_min);

        # Checking the temperatures every hour
        if str(time.localtime().tm_hour) == str(nextHour):
            nextHour = getNextHour();
            simpleAlgorithm();

        # Creating a session and then checking for new emails
        session = imaplib.IMAP4_SSL('imap.gmail.com');
        emails = checkForEmails(session);
        # If new emails exist, read and parse them and then close the session
        if emails != False:
            readEmails(session, emails);
            session.close();

# Method for sending an email to a user
def sendEmail(recpient, subject, content):
    # Providing gmail information
    SMTP_SERVER     = 'smtp.gmail.com';
    SMTP_PORT       = 587;
    GMAIL_USERNAME  = rPiEmail;
    GMAIL_PASSWORD  = rPiEmailPW;

    # Establishing a gmail session
    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT);
    session.ehlo();
    session.starttls();
    session.ehlo();
    session.login(GMAIL_USERNAME, GMAIL_PASSWORD);

    # Creating the headers and message
    msg             = MIMEMultipart('alternative');
    msg['To']       = recpient;
    msg['From']     = GMAIL_USERNAME;
    msg['Subject']  = subject;
    body            = MIMEText(content, 'plain');
    msg.attach(body);

    # Sending the email and then closing the session
    session.sendmail(GMAIL_USERNAME, recpient, msg.as_string());
    session.quit();

# Method for checking if there are new emails
# Returns the new emails if they exist, returns false otherwise
def checkForEmails(session):
    # Attempting to login
    if imapLogin(session, rPiEmail, rPiEmailPW):
        # If login is successful, check the INBOX mailbox
        if checkMailbox(session, 'INBOX'):
            # If the INBOX mailbox exists, check for unread emails
            emails = checkForType(session, '(UNSEEN)')
            if emails != False:
                return emails;

    return False;

# Method for attempting to login into gmail imap
# Returns true if login is successful, returns false otherwise
def imapLogin(session, user, password):
    try:
        session.login(user, password);
    except imaplib.IMAP4.error:
        return False;

    return True;

# Method for checking if a certain mailbox exists
# Returns true if the specified mailbox exists, returns false otherwise
def checkMailbox(session, mailbox):
    rv, data = session.select(mailbox);
    if rv == 'OK':
        return True;

    return False;

# Method for checking if the mailbox has a certain type of email
# Returns the emails if they exist, returns false otherwise
def checkForType(session, emailType):
    rc, emails = session.search(None, emailType);
    if rc == 'OK':
        return emails;

    return False;

# Method for reading the emails
def readEmails(session, emails):
    # Iterating through each new email
    emailContent = {};
    for num in emails[0].split():
        # Getting the data for each email
        type, data = session.fetch(num, '(RFC822)');
        for response in data:
            if isinstance(response, tuple):
                # Separating the contents of each email
                original = email.message_from_string(response[1]);
                emailContent['From'] = original['From'];
                emailContent['Subject'] = original['Subject'];

                # Obtaining the body of the email
                for part in original.walk():
                    if part.get_content_type() == 'text/plain':
                        emailContent['Body'] = part.get_payload();

                # # Sending an email to the user (just for testing headless operation)
                # sendEmail('4084669915@txt.att.net', 'New Email!', '\n\nFrom: ' + emailContent['From'] + '\n'
                #                                                     + 'Subject: ' + emailContent['Subject'] +'\n'
                #                                                     + 'Body: ' + emailContent['Body']);

                # Parsing the email
                parseEmail(emailContent);

                # Setting the email flag to seen
                type, data = session.store(num, '+FLAGS', '\\Seen')

# Method for parsing individual emails
def parseEmail(email):
    # Determining if the email's sender is the one you want
    print(validateSender(mrWindowEmail, email['From']));
    if validateSender(mrWindowEmail, email['From']):
        # Parsing the subject of the email to look for events
        subjectContent = email['Subject'].split('=');

        # Removing all whitespace characters from the content
        subjectContent = removeWhitespaces(subjectContent);

        # Parsing the actions depending on categories
        if subjectContent[0] == 'REQUEST_DATA':
            requestDataHandler(subjectContent[1]);
        elif subjectContent[0] == 'REQUEST_ACTION_NOW':
            requestActionNowHandler(subjectContent[1]);
        elif subjectContent[0] == 'REQUEST_ACTION_LATER':
            requestActionLaterHandler(subjectContent[1]);
        else:
            print('Incorrect request type...');

# Method for validating the sender of an email
# Returns true if the particular email's sender matches the one you specifiy, returns false otherwise
def validateSender(originalEmail, senderEmail):
    # Splitting the string so that the sender's email is the only content, not their name as well
    if (senderEmail.find(">") != -1):
        senderEmail = senderEmail[senderEmail.find("<") + 1 : senderEmail.find(">")];
    if originalEmail == senderEmail:
        return True;

    return False;

# Method for determining which event takes place for a REQUEST_DATA request type
def requestDataHandler(content):
    # Splitting the actions up by commas
    actions = content.split(',');

    # Removing all whitespace characters from the actions
    actions = removeWhitespaces(actions);

    if actions[0] == 'WINDOW_POSITION':
        sendEmail(mrWindowEmail, str(WINDOW_POSITION), 'Da window position info 4 u');
    elif actions[0] == 'BLINDS_POSITION':
        sendEmail(mrWindowEmail, str(BLINDS_POSITION), 'Da blinds position info 4 u');
    elif actions[0] == 'TEMPERATURE':
        sendEmail(mrWindowEmail, str(TEMPERATURE), 'Da temperature info 4 u');
    elif actions[0] == 'LIGHT_LEVEL':
        sendEmail(mrWindowEmail, str(LIGHT_LEVEL), 'Da light level info 4 u');
    elif actions[0] == 'PRESET':
        sendEmail(mrWindowEmail, str(PRESET), 'Da current preset info 4 u');
    elif actions[0] == 'MAX_MCP_VALUE':
        sendEmail(mrWindowEmail, str(MAX_MCP_VALUE), 'Da max mcp value info 4 u');
    else:
        print('Incorrect data request...');

# Method for determining which event takes place for a REQUEST_ACTION_NOW request type
def requestActionNowHandler(content):
    # Splitting the actions up by commas
    actions = content.split(',');

    # Removing all whitespace characters from the actions
    actions = removeWhitespaces(actions);

    if actions[0] == 'WINDOW_OPEN':
        if WINDOW_POSITION < 100:
            openWindow(100);
    elif actions[0] == 'WINDOW_CLOSE':
        if WINDOW_POSITION > 0:
            closeWindow(100);
    elif actions[0] == 'WINDOW_OPEN_POSITION':
        if WINDOW_POSITION < float(actions[1]):
            openWindow(float(actions[1]));
    elif actions[0] == 'WINDOW_CLOSE_POSITION':
        if WINDOW_POSITION > float(actions[1]):
            closeWindow(float(actions[1]));
    elif actions[0] == 'BLINDS_OPEN':
        if BLINDS_POSITION < 100:
            openBlinds(100);
    elif actions[0] == 'BLINDS_CLOSE':
        if BLINDS_POSITION > 0:
            closeBlinds(0);
    elif actions[0] == 'BLINDS_OPEN_POSITION':
        if BLINDS_POSITION < float(actions[1]):
            openBlinds(float(actions[1]));
    elif actions[0] == 'BLINDS_CLOSE_POSITION':
        if BLINDS_POSITION > float(actions[1]):
            closeBlinds(float(actions[1]));
    elif actions[0] == 'PRESET_CHANGE':
        if PRESET != int(actions[1]):
            changePreset(int(actions[1]));
    elif actions[0] == 'SET_MAX_MCP':
        global MAX_MCP_VALUE;
        value = ReadChannel(0);
        MAX_MCP_VALUE = value;
    elif actions[0] == 'SET_DESIRED_TEMP':
        global DESIRED_TEMP;
        DESIRED_TEMP = float(actions[1]);
    else:
        print('Incorrect action now request...');

# Method for determining which event takes place for a REQUEST_ACTION_NOW request type
def requestActionLaterHandler(content):
    # Splitting the actions up by commas
    actions = content.split(',');

    # Removing all whitespace characters from the actions
    actions = removeWhitespaces(actions);

    if actions[0] == 'NEW_PRESET':
        file_object = open('preset_' + str(PRESET) + '.txt', 'w'); # Overwriting the old file, if it exists
        print('Created a new preset ' + str(PRESET) + ' text file...');
        file_object.close();
    elif actions[0] == 'WINDOW_OPEN':
        appendToPresetFile(actions[1] + ', ' + actions[0] + '\n');
    elif actions[0] == 'WINDOW_CLOSE':
        appendToPresetFile(actions[1] + ', ' + actions[0] + '\n');
    elif actions[0] == 'WINDOW_OPEN_POSITION':
        appendToPresetFile(actions[2] + ', ' + actions[0] + ', ' + actions[1] + '\n');
    elif actions[0] == 'WINDOW_CLOSE_POSITION':
        appendToPresetFile(actions[2] + ', ' + actions[0] + ', ' + actions[1] + '\n');
    elif actions[0] == 'BLINDS_OPEN':
        appendToPresetFile(actions[1] + ', ' + actions[0] + '\n');
    elif actions[0] == 'BLINDS_CLOSE':
        appendToPresetFile(actions[1] + ', ' + actions[0] + '\n');
    elif actions[0] == 'BLINDS_OPEN_POSITION':
        appendToPresetFile(actions[2] + ', ' + actions[0] + ', ' + actions[1] + '\n');
    elif actions[0] == 'BLINDS_CLOSE_POSITION':
        appendToPresetFile(actions[2] + ', ' + actions[0] + ', ' + actions[1] + '\n');
    else:
        print('Incorrect action later request...');

    print('Added new instruction to preset ' + str(PRESET) + ': ' + content);

# Method for removing all whitespace characters from a list
# Returns the list with removed whitespace characters
def removeWhitespaces(listContent):
    i = 0;
    for content in listContent:
        listContent[i] = ''.join(content.split());
        i = i + 1;
    return listContent;

# Method for opening the window
def openWindow(percentage):
    # Changing global variables
    global WINDOW_POSITION;

    print('Opening window to ' + str(percentage) + '%...');
    WINDOW_POSITION = percentage;

    GPIO.output(11, 0); # 0 to open

    openTo = 1023 - (1023 - MAX_MCP_VALUE)*(percentage/100);

    while int(ReadChannel(0)) >= int(openTo):
        p.start(100);

    p.stop();           # Stopping the operation of the linear actuator

# Method for closing the window
def closeWindow(percentage):
    # Changing global variables
    global WINDOW_POSITION;

    print('Closing window to ' + str(percentage) + '%...');
    WINDOW_POSITION = 100 - percentage;

    GPIO.output(11, 1);	# 1 to close

    closeTo = (1023-MAX_MCP_VALUE) * (percentage / 100) + MAX_MCP_VALUE;

    print('Channel: ' + str(ReadChannel(0)));
    while int(ReadChannel(0)) < int(closeTo):
        print('Channel: ' + str(ReadChannel(0)));
        print('closeTo: ' + str(closeTo));
        p.start(100);

    p.stop();           # Stopping the operation of the linear actuator

# Method for opening the blinds
def openBlinds(percentage):
    # Changing global bariavles
    global BLINDS_POSITION;

    print('Opening blinds to ' + str(percentage) + '%...');
    BLINDS_POSITION = percentage;

# Method for closing the blinds
def closeBlinds(percentage):
    # Changing global variables
    global BLINDS_POSITION;

    print('Closing blinds to ' + str(percentage) + '%...');
    BLINDS_POSITION = percentage;

# Method for changing the current preset
def changePreset(preset):
    # Changing global variables
    global PRESET;

    print('Changing preset to ' + str(preset) + '...');
    PRESET = preset;

# Method for getting the next minute based on the current hour and minute
# Returns the next minute as an integer
def getNextMin(hour, minute):
    if hour == 23:
        if minute == 59:
            return 0;
        else:
            return minute + 1;
    else:
        return minute + 1;

# Method for getting the next hour from the current hours
# Returns the next hour as an integer
def getNextHour():
    currentHour = time.localtime().tm_hour;

    if (currentHour == 23):
        return 0;

    return currentHour + 1;

# Method for opening a preset text file and appending to it
def appendToPresetFile(contentToAdd):
    file_object = open('preset_' + str(PRESET) + '.txt', 'a'); # Appending to an existing file
    file_object.write(contentToAdd);
    file_object.close();

# Method for checking a preset file for timed events
def checkPresetFile(hour, minute):
    file_object = open('preset_' + str(PRESET) + '.txt', 'r'); # Reading an existing file
    for line in file_object:
        # Splitting the actions up by commas
        actions = line.split(',');

        # Removing all whitespace characters from the actions
        actions = removeWhitespaces(actions);

        # Splitting the time in the file into hour and minute
        time = actions[0].split(':');

        # Removing the first 0 if the minute or hour is less than 10
        if time[0][0] == '0':
            time[0] = time[0].replace('0', '');
        if time[1][0] == '0':
            time[1] = time[1].replace('0', '');

        # Executing the action if it is time
        if (str(time[0]) == str(hour) and str(time[1]) == str(minute)):
            if len(actions) == 3: # Determining if a second parameter was given
                requestActionNowHandler(actions[1] + ', ' + actions[2]);
            else:
                requestActionNowHandler(actions[1]);

# Method for reading a specified channel of the MCP
# Returns the data as an integer
def ReadChannel(channel):
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    return data

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

# Method for getting the temperature for the next 24 hours in the specified state and city
# Returns the day's temperatures (in fahrenheit) as an array of integers
def get24HrTemperatures(state, city):
    # Making an API call to weatherunderground
    f = urllib2.urlopen('http://api.wunderground.com/api/12d1b60c95f74d26/hourly/q/' + state + '/' + city + '.json');

    # Parsing the returned JSON
    json_string = f.read();
    parsed_json = json.loads(json_string);

    # Storing the temperature information in an array
    forecast = []
    for i in range(24):
        forecast.append(parsed_json['hourly_forecast'][i]['temp']['english']);
    # for i in range(24):
    #     print "temperature for the hour %i: %s" % (i, forecast[i])
    f.close();

    return forecast;

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

# Method for checking the temperatures and taking actions based on Results
def simpleAlgorithm():
    insideTemp = float(retrieveEnOceanState('STM')) * 1.8 + 32;
    outsideTemp = getCurrentTemperature('CA', 'Irvine');

    # print(type(insideTemp));
    # print(type(outsideTemp));
    # print(type(DESIRED_TEMP));

    print('Inside temp: ' + str(insideTemp));
    print('Outside temp: ' + str(outsideTemp));
    print('Desired temp: ' + str(DESIRED_TEMP));

    if insideTemp > DESIRED_TEMP:
        if outsideTemp < insideTemp:
            print('Opening window...');
            openWindow(100);
        else:
            print('Closing window');
            closeWindow(100);
    elif insideTemp < DESIRED_TEMP:
        if outsideTemp > insideTemp:
            print('Opening window...');
            openWindow(100);
        else:
            print('Closing window');
            closeWindow(100);

main(); # Call to main method so that it runs first
