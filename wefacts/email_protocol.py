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

import wefacts
import util


class EmailHandler():
    def __init__(self):
        local_account = os.path.dirname(util.base_dir) + '/local/accounts.json'
        email_account = json.load(open(local_account))
        self.email_address = email_account['gmail_username']
        self.imap = imaplib.IMAP4_SSL('imap.gmail.com')
        self.imap.login(email_account['gmail_username'], email_account['gmail_password'])
        self.smtp = smtplib.SMTP('smtp.gmail.com', 587)
        self.smtp.starttls()
        self.smtp.login(email_account['gmail_username'], email_account['gmail_password'])

        self._msg_sorry = "\n\nI'm afraid I cannot understand the order. \n"
        self._msg_instructions = \
            "Please try to send me an email with the subject as the location and dates, " \
            "separated by semicolon (;). For example, \'5000 Forbes Ave, Pittsburgh, PA 15213; 160101; 161231\'\n" \
            "\n\nBest!\nwefacts"
        self._msg_ready = "\n\nYour order for wefacts data is ready as attached.\n"
        self._msg_bye = "\n\nBest!\nwefacts"

    def __del__(self):
        self.imap.close()
        self.smtp.close()

    def check(self):
        self.imap.select("inbox")

        result, data = self.imap.search(None, "ALL", '(UNSEEN)')
        email_ids = data[0].split()

        # todo catch exception and continues with following emails
        # todo when find exception : send an error email to user
        # todo e.g. typo 201070601
        for e_id in email_ids:
            result, data = self.imap.fetch(e_id, '(BODY.PEEK[HEADER])')
            email_sender = email.message_from_string(data[0][1])['from']
            recipient = email_sender.split()[-1][1:-1]
            name = ' '.join([n.title() for n in email_sender.split()[:-1]])
            if len(name) == 0:
                name = 'Friend'
            order = email.message_from_string(data[0][1])['subject']
            # email_subject = re.findall(r"[\w']+", email.message_from_string(data[0][1])['subject'])
            email_subject = email.message_from_string(data[0][1])['subject'].split(';')
            util.logger.info('Processing %s for %s' % (' '.join(email_subject), recipient))
            if len(email_subject) < 2:
                response = self._reply(name, recipient, order)
            else:
                location = email_subject[0].strip()
                date1 = email_subject[1].strip()
                date2 = date1 if len(email_subject) <= 2 else email_subject[2].strip()
                response = self._reply(name, recipient, order, location, date1, date2)
            if response == 'OK':
                util.logger.info('Successfully replied %s from %s' % (' '.join(email_subject), recipient))
            else:
                util.logger.error('Fail replying for %s from %s' % (' '.join(email_subject), recipient))
            self.imap.store(e_id, '+FLAGS', '\Seen')

    def _reply(self, name, recipient, order, location=None, date1=None, date2=None, note=''):
        msg = MIMEMultipart()
        msg['From'] = self.email_address
        msg['To'] = recipient
        msg['Subject'] = "Your wefacts order %s" % order
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
            elif isinstance(df, str):
                body += '\n\n' + df
            elif isinstance(df, pd.DataFrame):
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload(open(df.meta['Filename'], 'rb').read())
                encoders.encode_base64(attachment)
                attachment.add_header('Content-Disposition', "attachment; filename= %s"
                                      % os.path.split(df.meta['Filename'])[-1])
                msg.attach(attachment)
                body += self._msg_ready
                body += '\nReports obtained from the following weather stations.\n'
                body += ''.join(['- Year %d: %s (USAF %s WBAN %s)\n' % (y, v[0], v[1], v[2])
                                 for y, v in df.meta['Stations'].iteritems()])
                body += '\nYour files include the following.\n'
                body += '- Hourly Weather Recording: %s\n' % os.path.split(df.meta.get('Filename'))[-1]
                if df.meta.get('SWFilename', None):
                    attachment2 = MIMEBase('application', 'octet-stream')
                    attachment2.set_payload(open(df.meta.get('SWFilename'), 'rb').read())
                    encoders.encode_base64(attachment2)
                    attachment2.add_header('Content-Disposition', "attachment; filename= %s"
                                           % os.path.split(df.meta.get('SWFilename'))[-1])
                    msg.attach(attachment2)
                    body += '- Preliminary Local Severe Weather Reports: %s\n' \
                            % os.path.split(df.meta.get('SWFilename'))[-1]
        body += self._msg_bye
        # todo add readme.txt
        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()

        try:
            self.smtp.sendmail(self.email_address, recipient, text)
            return 'OK'
        except smtplib.SMTPException:
            return 'Fail Sending'


if __name__ == '__main__':
    gmail = EmailHandler()
    gmail.check()