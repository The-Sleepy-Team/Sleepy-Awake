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
import sys
import imaplib
import getpass
import email
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Main method of the program which will run first when file is executed
def main():
    print('Hello world!');

    # Checking if new, unread emails exists
    session = imaplib.IMAP4_SSL('imap.gmail.com');
    emails = checkForEmails(session);

    # Parsing through the emails if they exist
    if emails != False:
        parseEmails(session, emails);

    # # Letting the user know the device is operational, especially useful for headless operation
    # sendEmail('4084669915@txt.att.net', 'Raspberry Pi Connection', 'Raspberry Pi operating!');
    #
    # print('Message sent!');

    # print('Going into infinite loop');
    # while 1 :
    #     nothing = 0;

# Method for sending an email to a user
def sendEmail(recpient, subject, content):
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
    if imapLogin(session, 'sleepyraspberrypi@gmail.com', '123abc123ABC'):
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

# Method for parsing through the emails
def parseEmails(session, emails):
    # Iterating through each new email
    for num in emails[0].split():
        # Getting the data for each email
        type, data = session.fetch(num, '(RFC822)');
        for response in data:
            if isinstance(response, tuple):
                # Separating the contents of each email
                original = email.message_from_string(response[1]);
                print(original['From']);
                print(original['Subject']);

                # Obtaining the body of the email
                for part in original.walk():
                    if part.get_content_type() == 'text/plain':
                        print part.get_payload()

                # Setting the email flag to seen
                type, data = session.store(num, '+FLAGS', '\\Seen')

main(); # Call to main function so that it runs first
