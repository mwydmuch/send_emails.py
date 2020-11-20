#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
send_emails.py
Copyright (c) 2019-2020 Marek Wydmuch
"""

import click
import csv
import yaml
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def login_to_SMTP(host, login, password, port=587):
    server = smtplib.SMTP(host, port)
    server.ehlo()
    server.starttls()
    server.login(login, password)
    return server


def send_mail(server, msg):
    server.sendmail(msg["From"], msg["To"], msg.as_string())
    print("Successfully sent email to:", msg["To"])


def compose_msg(address, content):
    msg = MIMEMultipart("alternative")

    msg["From"] = content["from"]
    msg["To"] = address["email"]
    msg["Subject"] = content["subject"].format(**address)

    msg.add_header("Content-Type", "text/html")

    part1 = MIMEText(content["plain"].format(**address), "plain")
    part2 = MIMEText(content["html"].format(**address), "html")
    msg.attach(part1)
    msg.attach(part2)

    return msg


@click.command()
@click.option(
    "-c",
    "--content_path",
    type=str,
    required=True,
    help="Path to YAML or JSON file with email content. The file should contain fields 'subject', 'from', 'html' and 'plain'.",
)
@click.option(
    "-a",
    "--address_book_path",
    type=str,
    required=True,
    help="Path to TSV or CSV file with emails and additional data. File should contain field 'email'.",
)
@click.option(
    "-d",
    "--delimiter",
    type=str,
    default="\t",
    help="Delimiter for address book file (default = '\\t') ",
)
@click.option("-h", "--host", type=str, required=True, help="SMTP host.")
@click.option("-l", "--login", type=str, required=True, help="SMTP login.")
@click.option("-p", "--password", type=str, required=True, help="SMTP password.")
@click.option("-P", "--port", type=int, default=587, help="SMTP port (default = 587).")
@click.option(
    "-e",
    "--email",
    type=str,
    default=None,
    help="Send all messages to the specified email.",
)
def send_mails(
    host: str,
    login: str,
    password: str,
    port: int,
    content_path: str,
    address_book_path: str,
    delimiter: str,
    email: str,
):
    with open(content_path, "r", encoding="utf-8") as content_file:
        if content_path.endswith(".yaml"):
            content = yaml.safe_load(content_file)
        elif content_path.endswith(".json"):
            content = json.loads(content_file)

    with open(address_book_path, "r", encoding="utf-8") as addressees_file:
        addressees_reader = csv.DictReader(addressees_file, delimiter=delimiter)
        server = login_to_SMTP(host, login, password, port=port)
        for address in addressees_reader:
            if email and len(email) > 0:
                address["email"] = email
            send_mail(server, compose_msg(address, content))

        server.quit()


if __name__ == "__main__":
    send_mails()
