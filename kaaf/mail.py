from io import BytesIO
import logging
import os
import json
import base64

from googleapiclient.discovery import build
from google.oauth2 import service_account

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate, formataddr


class MailConfigurationException(Exception):
    pass


def service_account_login(mail_from, service_account_str):
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    credentials = service_account.Credentials.from_service_account_info(json.loads(base64.b64decode(service_account_str)), scopes=SCOPES)
    delegated_credentials = credentials.with_subject(mail_from)
    return build('gmail', 'v1', credentials=delegated_credentials)


def create_mail(msg, body):
    msg[
        "Subject"
    ] = f'Refusjonsskjema - {body.get("name", "")}'

    text = ""
    text += f'Navn: {body.get("name", "")}\n'
    text += f'E-post: {body.get("mailfrom", "")}\n'
    text += f'Gruppe: {body.get("committee", "")}\n'
    text += f'Kontonummer: {body.get("accountNumber", "")}\n'
    text += f'Beløp: {body.get("amount", "")}\n'
    text += f'Dato: {body.get("date", "")}\n'
    text += f'Anledning/arrangement: {body.get("occasion", "")}\n'
    text += f'Kommentar: {body.get("comment", "")}\n'
    text += f'\n'
    text += f"Refusjonsskjema er generert og vedlagt. Ved spørsmål ta kontakt med kasserer@ntnui.no!"

    msg.attach(MIMEText(text))


def send_mail(mail_to, body, file):
    if "MAIL_ADDRESS" not in os.environ or "SERVICE_ACCOUNT_STR" not in os.environ:
        raise MailConfigurationException("Mail isn't configured properly")
    mail_from = os.environ["MAIL_ADDRESS"]
    service_account_str = os.environ["SERVICE_ACCOUNT_STR"]

    msg = MIMEMultipart()
    msg["From"] = formataddr(("NTNUI refusjon", mail_from))
    msg["To"] = COMMASPACE.join(mail_to)
    msg["Date"] = formatdate(localtime=True)

    create_mail(msg, body)

    filename = body.get("date", "") + " Refusjonsskjema " + body.get("name", "") + ".pdf"
    part = MIMEApplication(file, Name=filename)
    part["Content-Disposition"] = f'attachment; filename="{filename}"'
    msg.attach(part)

    logging.info(f'Sending mail to {", ".join(mail_to)}')

    service = service_account_login(mail_from, service_account_str)
    raw = base64.urlsafe_b64encode(msg.as_bytes())
    body = { 'raw': raw.decode() }
    messages = service.users().messages()
    messages.send(userId="me", body=body).execute()
