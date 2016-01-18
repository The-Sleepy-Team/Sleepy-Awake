"""
File: email-test-module.py
Course: Senior Design Project - CSE 181B / EECS 159B
Authors:    Michael Ishimoto
            Tyler Hom
            Ji Yeon Kim
            David Tran
"""

# Importing necessary libraries
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Main method of the program which will run first when file is executed
def main():
    print('Hello world!');
    sendEmail("trandl1@uci.edu", 'Just a test', 'It works!');
    print('Email sent!');

# Method for sending an email to a user
def sendEmail(user, subject, content):
    # Providing gmail information
    SMTP_SERVER     = 'smtp.gmail.com';
    SMTP_PORT       = 587;
    GMAIL_USERNAME  = 'sleepyraspberrypi@gmail.com';
    GMAIL_PASSWORD  = '123abc123ABC';

    # Establishing a gmail session
    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT);
    session.ehlo();
    session.starttls();
    session.ehlo();
    session.login(GMAIL_USERNAME, GMAIL_PASSWORD);

    # Creating the headers and message
    msg             = MIMEMultipart('alternative');
    msg['To']       = user;
    msg['From']     = GMAIL_USERNAME;
    msg['Subject']  = subject;
    body            = MIMEText(content, 'plain');
    msg.attach(body);

    # Sending the email and then closing the session
    session.sendmail(GMAIL_USERNAME, user, msg.as_string());
    session.quit();


main(); # Call to main function so that it runs first
