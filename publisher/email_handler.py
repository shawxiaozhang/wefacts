import json
import imaplib
import smtplib
import email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import re
from dateutil import parser as dateutil_parser
import datetime

import pandas as pd

from wefacts import wefacts
from wefacts.util import logger


class EmailHandler():
    def __init__(self):
        email_account = json.load(open('../local/accounts.json'))
        self.email_address = email_account['gmail_username']
        self.imap = imaplib.IMAP4_SSL('imap.gmail.com')
        self.imap.login(email_account['gmail_username'], email_account['gmail_password'])
        self.smtp = smtplib.SMTP('smtp.gmail.com', 587)
        self.smtp.starttls()
        self.smtp.login(email_account['gmail_username'], email_account['gmail_password'])

        self._msg_sorry = "\n\nI'm afraid I couldn't understand the order. \n"
        self._msg_instructions = \
            "Please try to send me an email with the subject as the location and dates, " \
            "separated by comma (,). For example, \'Pittsburgh, 160101, 161231.\'\n" \
            "\n\nBest!\nwefacts"
        self._msg_ready = "Your order for wefacts data is ready as attached.\n\nBest!\nwefacts"

    def __del__(self):
        self.imap.close()
        self.smtp.close()

    def check(self):
        self.imap.select("inbox")

        result, data = self.imap.search(None, "ALL", '(UNSEEN)')
        email_ids = data[0].split()

        for e_id in email_ids:
            result, data = self.imap.fetch(e_id, '(BODY.PEEK[HEADER])')
            email_sender = email.message_from_string(data[0][1])['from']
            recipient = email_sender.split()[-1][1:-1]
            name = ' '.join([n.title() for n in email_sender.split()[:-1]])
            email_subject = re.findall(r"[\w']+", email.message_from_string(data[0][1])['subject'])
            if len(email_subject) < 2:
                self._reply(name, recipient)
                continue
            location = email_subject[0].strip()
            date1 = email_subject[1].strip()
            date2 = date1 if len(email_subject) <= 2 else email_subject[2].strip()
            response = self._reply(name, recipient, location, date1, date2)
            if response == 'OK':
                self.imap.store(e_id, '+FLAGS', '\Seen')
            else:
                logger.error('Fail replying for %s from %s' % (' '.join(email_subject), recipient))

    def _reply(self, name, recipient, location=None, date1=None, date2=None, note=''):
        msg = MIMEMultipart()
        msg['From'] = self.email_address
        msg['To'] = recipient
        msg['Subject'] = "wefacts data for %s from %s to %s" % (location, date1, date2)
        body = "Hello, %s" % name
        if location is None or date1 is None:
            body += self._msg_sorry + self._msg_instructions
        elif not isinstance(dateutil_parser.parse(date1), datetime.datetime):
            body += self._msg_sorry + '\nCannot parse %s.\n' % date1 + self._msg_instructions
        elif not isinstance(dateutil_parser.parse(date2), datetime.datetime):
            body += self._msg_sorry + '\nCannot parse %s.\n' % date2 + self._msg_instructions
        else:
            date1, date2 = dateutil_parser.parse(date1), dateutil_parser.parse(date2)
            df = wefacts.get_weather(location, int(date1.strftime('%Y%m%d')), int(date2.strftime('%Y%m%d')), True)
            if df is None:
                body += self._msg_sorry + '\nCannot geo-locate %s.\n' % location + self._msg_instructions
            elif isinstance(df, pd.DataFrame):
                filename = df.meta['Filename']
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload(open(filename, 'rb').read())
                encoders.encode_base64(attachment)
                attachment.add_header('Content-Disposition', "attachment; filename= %s" % os.path.split(filename)[-1])
                msg.attach(attachment)
                body += '\n\nWeather Station for %s: %s (USAF %s WBAN %s)\n\n' \
                        % (location, df.meta['StationName'], df.meta['StationID'].split('-')[0],
                           df.meta['StationID'].split('-')[1]) + self._msg_ready
        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()

        try:
            self.smtp.sendmail(self.email_address, recipient, text)
            return 'OK'
        except smtplib.SMTPException:
            logger.error('Unable to send email to %s at %s' % (name, recipient))
            return 'Fail Sending'

if __name__ == '__main__':
    gmail = EmailHandler()
    gmail.check()