import imaplib
import socket
import smtplib
import os
import email
from email.utils import parseaddr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from GetAiResponses import *
from GetFlightInfo import *

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
IMAP_SERVER = os.getenv("IMAP_SERVER")
SMTP_PORT_SSL = os.getenv("SMTP_PORT_SSL")
SMTP_PORT_TLS = os.getenv("SMTP_PORT_TLS")


def check_emails():
    print("checking emails")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")
    status, messages = mail.search(None, "(UNSEEN)")
    print("status: ",status)
    if status != "OK":
        return [], mail
    email_ids = messages[0].split()
    return email_ids, mail


def process_emails(email_ids, mail):
    print("processing emails")
    for e_id in email_ids:
        status, msg_data = mail.fetch(e_id, "(RFC822)")
        if status != "OK":
            continue
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        sender = msg["From"]
        subject = msg["Subject"]
        subject = f"Re: {subject}" if subject else "Re: Your Email"

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")

        sender_email = parseaddr(sender)[1]

        # Flag to track if LLM was called
        llm_called = False

        structured_query = extract_flight_query(body)
        if structured_query:
            print("got structured query, running if statement")
            llm_called = True  # LLM called in extract_flight_query
            flight_results = fetch_flight_inventory(structured_query)
            ai_reply = compose_flight_response(body, flight_results)
            print("ai reply: ", ai_reply)
            llm_called = True  # LLM called in compose_flight_response
        else:
            print("did not got structured query, running else statement")
            ai_reply = generate_gemini_response(body)
            llm_called = True  # LLM called in general reply

        print(f"LLM called for email from {sender_email}: {llm_called}")

        send_reply(sender_email, subject, ai_reply)
        mail.store(e_id, "+FLAGS", "\\Seen")


def send_reply(recipient, subject, body):
    reply = MIMEMultipart()
    reply["From"] = EMAIL
    reply["To"] = recipient
    reply["Subject"] = subject
    reply.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT_SSL, timeout=10) as server:
            server.login(EMAIL, PASSWORD)
            server.send_message(reply)
    except (smtplib.SMTPConnectError, socket.error, OSError) as ssl_error:
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT_TLS, timeout=10) as server:
                server.starttls()
                server.login(EMAIL, PASSWORD)
                server.send_message(reply)
        except Exception as e:
            print(f"❌ Failed to send email to {recipient}: {e}")
