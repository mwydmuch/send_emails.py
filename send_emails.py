#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
send_emails.py
Copyright (c) 2019-2021 Marek Wydmuch
"""

import click
import csv
import json
import re
import smtplib
import yaml
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
    for to in msg["To"].split(","):
        to = to.strip()
        server.sendmail(msg["From"], to, msg.as_string())
    print("Successfully sent email to:", msg["To"])


def get_msg_part(template, part, format_template=True, address=None):
    if format_template and address:
        msg_part = MIMEText(template[part].format(**address), part)
    else:
        msg_part = MIMEText(template[part], part)
    return msg_part


def compose_msg(template, address, format_template=True, plain_from_html=True):
    msg = MIMEMultipart("alternative")

    msg["From"] = template["from"]
    msg["To"] = address["email"]
    msg["Subject"] = template["subject"].format(**address) if format_template else template["subject"]

    msg.add_header("template-Type", "text/html")

    if "html" in template:
        msg.attach(get_msg_part(template, "html", format_template=format_template, address=address))
        if plain_from_html and "plain" not in template:
            template["plain"] = re.sub('<[^<]+?>', '', template["html"])  # Remove HTML tags
            template["plain"] = re.sub('<[^<]+?>', '', template["html"])  # Remove HTML tags

    if "plain" in template:
        msg.attach(get_msg_part(template, "plain", format_template=format_template, address=address))

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
@click.option(
    "-f",
    "--format_template",
    type=bool,
    default=True,
    help="Format 'title'/'html'/'plain' fields of template with fields from address book.",
    show_default=True
)
@click.option(
    "-H",
    "--plain_from_html",
    type=bool,
    default=False,
    help="If no 'plain' field in template, generate it from 'html' field.",
    show_default=True
)
@click.option("-S", "--skip", type=int, default=0, help="Number of address book records to skip.", show_default=True)
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
    format_template: bool,
    plain_from_html: bool,
    skip: int,
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

            if i < skip:
                print("Skipped sending to {}".format(address["email"]))
                continue

            send_mail(server, compose_msg(template, address, format_template=format_template, plain_from_html=plain_from_html))

            if sleeptime > 0 and i > 0 and i % batchsize == 0:
                print("Sent {} messages, waiting {} seconds ...".format(batchsize, sleeptime))
                sleep(sleeptime)

        server.quit()


if __name__ == "__main__":
    send_mails()
