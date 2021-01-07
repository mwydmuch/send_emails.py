#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
send_emails.py
Copyright (c) 2019-2021 Marek Wydmuch
"""

import click
import csv
import yaml
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import sleep


def login_to_SMTP(host, login, password, port=587):
    server = smtplib.SMTP(host, port)
    server.ehlo()
    server.starttls()
    server.login(login, password)
    return server


def send_mail(server, msg):
    server.sendmail(msg["From"], msg["To"], msg.as_string())
    print("Successfully sent email to:", msg["To"])


def compose_msg(template, address):
    msg = MIMEMultipart("alternative")

    msg["From"] = template["from"]
    msg["To"] = address["email"]
    msg["Subject"] = template["subject"].format(**address)

    msg.add_header("template-Type", "text/html")

    part1 = MIMEText(template["plain"].format(**address), "plain")
    part2 = MIMEText(template["html"].format(**address), "html")
    msg.attach(part1)
    msg.attach(part2)

    return msg


@click.command()
@click.option(
    "-t",
    "--template_path",
    type=click.Path(exists=True),
    required=True,
    help="Path to YAML or JSON file with email template. The file should contain fields 'subject', 'from', 'html' and 'plain'.",
)
@click.option(
    "-a",
    "--address_book_path",
    type=click.Path(exists=True),
    required=True,
    help="Path to TSV or CSV file with emails and additional data for the template. File should contain field 'email'.",
)
@click.option(
    "-d",
    "--delimiter",
    type=str,
    default="\t",
    help="Delimiter for address book file.\t[default: '\\t']",
)
@click.option("-h", "--host", type=str, required=True, help="SMTP host.")
@click.option("-l", "--login", type=str, required=True, help="SMTP login.")
@click.option("-p", "--password", type=str, required=True, help="SMTP password.")
@click.option("-P", "--port", type=int, default=587, help="SMTP port.", show_default=True)
@click.option(
    "-e",
    "--email",
    type=str,
    default=None,
    help="Send all messages to the specified email.",
)
@click.option("-b", "--batchsize", type=int, default=10, help="Size of email batches.", show_default=True)
@click.option("-s", "--sleeptime", type=int, default=0, help="Sleep interval between sending email batches.", show_default=True)
def send_mails(
    host: str,
    login: str,
    password: str,
    port: int,
    template_path: str,
    address_book_path: str,
    delimiter: str,
    email: str,
    batchsize: int,
    sleeptime: int,
):
    with open(template_path, "r", encoding="utf-8") as template_file:
        if template_path.endswith(".yaml"):
            template = yaml.safe_load(template_file)
        elif template_path.endswith(".json"):
            template = json.loads(template_file)

    with open(address_book_path, "r", encoding="utf-8") as addressees_file:
        addressees_reader = csv.DictReader(addressees_file, delimiter=delimiter)
        server = login_to_SMTP(host, login, password, port=port)
        for i, address in enumerate(addressees_reader):
            if email and len(email) > 0:
                address["email"] = email
            send_mail(server, compose_msg(template, address))

            if sleeptime > 0 and i > 0 and i % batchsize == 0:
                print("Sent {} messages, waiting {} seconds ...".format(batchsize, sleeptime))
                sleep(sleeptime)

        server.quit()


if __name__ == "__main__":
    send_mails()
