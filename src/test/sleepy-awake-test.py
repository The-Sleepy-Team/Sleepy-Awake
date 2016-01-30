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
import imaplib
import getpass
import email
import datetime
import time
import urllib2
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Creating global variables
rPiEmail            = 'sleepyraspberrypi@gmail.com';
rPiEmailPW          = '123abc123ABC';
mrWindowEmail       = 'sleepymrwindow@gmail.com';
WINDOW_POSITION     = 0;    # Position of the window, relative to openness
                            # Can take on any percentages (eg. 10% = 10, 75% = 75)
                            # 100 = 100% opened
BLINDS_POSITION     = 0;    # Similar to WINDOW_POSITION
TEMPERATURE         = 0.0;  # Temperature will be in Fahrenheit
LIGHT_LEVEL         = 0;    # Still deciding on units
PRESET              = 1;    # The current preset

# Main method of the program which will run first when file is executed
def main():
    # Letting the user know the device is operational, especially useful for headless operation
    sendEmail('4084669915@txt.att.net', 'Raspberry Pi Connection', 'Raspberry Pi operating!');

    # Setting the next minute
    nextMin = time.localtime().tm_min + 1;

    # Infinite loop to constantly check email
    while True:
        # Checking the preset text file every minute
        if str(time.localtime().tm_min) == str(nextMin):
            nextMin = getNextMin(time.localtime().tm_hour, time.localtime().tm_min);

        # Creating a session and then checking for new emails
        session = imaplib.IMAP4_SSL('imap.gmail.com');
        emails = checkForEmails(session);
        # If new emails exist, read and parse them and then close the session
        if emails != False:
            readEmails(session, emails);
            session.close();

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
            closeWindow(0);
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
    else:
        print('Incorrect action now request...');

# Method for determining which event takes place for a REQUEST_ACTION_NOW request type
def requestActionLaterHandler(content):
    # Splitting the actions up by commas
    actions = content.split(',');

    # Removing all whitespace characters from the actions
    actions = removeWhitespaces(actions);

    if actions[0] == 'NEW_PRESET':
        file_object = open('preset_' + str(PRESET) + '.txt', 'w');
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

# Method for closing the window
def closeWindow(percentage):
    # Changing global variables
    global WINDOW_POSITION;

    print('Closing window to ' + str(percentage) + '%...');
    WINDOW_POSITION = percentage;

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
# Returns the next minute
def getNextMin(hour, minute):
    if hour == 23:
        if minute == 59:
            return 0;
        else:
            return minute + 1;
    else:
        return minute + 1;

# Method for opening a preset text file and appending to it
def appendToPresetFile(contentToAdd):
    file_object = open('preset_' + str(PRESET) + '.txt', 'a');
    file_object.write(contentToAdd);
    file_object.close();

main(); # Call to main method so that it runs first
