# calendar-manager

## Introduction

The idea of this project is to create appointments in my Google calendar reading info from a Google sheet.

## Installation

To work with Google Calendar and  Google Sheet, you first need to get some credentials and enable the API. Follow the instructions in https://www.makeuseof.com/tag/read-write-google-sheets-python/ and store the credentials in `creds.json`, which is ignored by Git.

Then, install all necessary packages using a virtualenv (see https://docs.python-guide.org/dev/virtualenvs/).

```bash
pip install --user pipenv
pipenv install gspread
pipenv install oauth2client
pipenv install PyOpenSSL
```

## Run

Run as: `pipenv run python read_gspread.py`
