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

Run server to 0.0.0.0
`python manage.py runserver 0.0.0.0:8000`

## Fetch last forms

- Set environment variable: **TP_KEY**=Typeform_API_key
- Activate virtualenv (optional)
- Run: `python manange.py fetchforms`
