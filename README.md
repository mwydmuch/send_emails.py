# `send_emails.py`

`send_emails.py` is a simple script for sending emails developed as a helper tool for ML in PL Conference 2019 (https://conference.mlinpl.org).

## Usage
```
Usage: send_emails.py [OPTIONS]

Options:
  -c, --content_path TEXT       Path to YAML or JSON file with email content.
                                The file should contain fields 'subject',
                                'from', 'html' and 'plain'.  [required]
  -a, --address_book_path TEXT  Path to TSV or CSV file with emails and
                                additional data. File should contain field
                                'email'.  [required]
  -d, --delimiter TEXT          Delimiter for address book file (default =
                                '\t')
  -h, --host TEXT               SMTP host.  [required]
  -l, --login TEXT              SMTP login.  [required]
  -p, --password TEXT           SMTP password.  [required]
  -P, --port INTEGER            SMTP port (default = 587).
  --help                        Show this message and exit.
```
