# `send_emails.py`

`send_emails.py` is a simple script for sending emails developed as a helper tool for ML in PL Conference 2019 (https://conference.mlinpl.org).

## Usage
```
Usage: send_emails.py [OPTIONS]

Options:
  -t, --template_path PATH      Path to YAML or JSON file with email template.
                                The file should contain fields 'subject',
                                'from', 'html' and 'plain'.  [required]

  -a, --address_book_path PATH  Path to TSV or CSV file with emails and
                                additional data for the template. File should
                                contain field 'email'.  [required]

  -d, --delimiter TEXT          Delimiter for address book file.
                                [default: '\t']

  -h, --host TEXT               SMTP host.  [required]
  -l, --login TEXT              SMTP login.  [required]
  -p, --password TEXT           SMTP password.  [required]
  -P, --port INTEGER            SMTP port.  [default: 587]
  -e, --email TEXT              Send all messages to the specified email.
  -b, --batchsize INTEGER       Size of email batches.  [default: 10]
  -s, --sleeptime INTEGER       Sleep interval between sending email batches.
                                [default: 0]

  --help                        Show this message and exit.
```
