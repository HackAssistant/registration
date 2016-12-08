# mercuryhack

Backend for hackathons. Integrates with Sendgrid and Typeform.


## Setup
Needs: Python 3.5

- `pip install -r requirements.txt`
- `python manage.py migrate`
- `python manage.py createsuperuser`

## Run server

Add 2 environment variables:

- **SG_KEY**: SendGrid API Key
- **TP_KEY**: Typeform API key

You can also set up a **A_TP_ID** to a custom typeform form id.

Run server to 0.0.0.0
`python manage.py runserver 0.0.0.0:8000`
