import logging
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from os.path import basename


class MailConfigurationException(Exception):
    pass


def create_mail(msg, body):
    msg[
        "Subject"
    ] = f'Reiseregning - {body["name"]}'

    text = ""
    text += f'Gruppe: {body.get("committee", "")}\n'
    text += f'Navn: {body.get("name", "")}\n'
    text += f'Kontonummer: {body.get("accountNumber", "")}\n'
    text += f'Beløp: {body.get("amount", "")}\n'
    text += f'Anledning/arrangement: {body.get("occasion", "")}\n'
    text += f'Reise startdato: {body.get("date", "")}\n'
    text += f'Reise sluttdato: {body.get("dateEnd", "")}\n'
    text += f'Reisefølge: {body.get("team", "")}\n'
    text += f'Antall reisende: {body.get("numberOfTravelers", "")}\n'
    text += f'Reisedestinasjon: {body.get("destination", "")}\n'
    text += f'Reiserute: {body.get("route", "")}\n'
    text += f'Kommentar: {body.get("comment", "")}\n\n'

    text += f"Reiseregning er generert og vedlagt. Ved spørsmål ta kontakt med kasserer@ntnui.no!"

    msg.attach(MIMEText(text))


def send_mail(mail_to, body, file):
    if "MAIL_ADDRESS" not in os.environ or "MAIL_PASSWORD" not in os.environ:
        raise MailConfigurationException("Mail isn't configured properly")
    mail_from = os.environ["MAIL_ADDRESS"]
    mail_password = os.environ["MAIL_PASSWORD"]

    msg = MIMEMultipart()
    msg["From"] = mail_from
    msg["To"] = COMMASPACE.join(mail_to)
    msg["Date"] = formatdate(localtime=True)

    create_mail(msg, body)

    filename = body.get("date", "") + " Reiseregning " + body.get("name", "") + ".pdf"
    part = MIMEApplication(file, Name=filename)
    part["Content-Disposition"] = f'attachment; filename="{filename}"'
    msg.attach(part)

    logging.info(f'Sending mail to {", ".join(mail_to)}')

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(mail_from, mail_password)
    server.sendmail(mail_from, mail_to, msg.as_string())
    server.close()
