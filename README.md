# HackUPC Backend

Backend for application management. Automatically retrieves Typeform applications. Review application interface. Sends invites and controls confirmation and cancellation application flow. Check-in interface. Admin dashboard with stats. Uses Sendgrid API for email management.


## Setup
Needs: Python 3.X

- `pip install -r requirements.txt`
- `python manage.py migrate`
- `python manage.py createsuperuser`

### Load dummy data

In order to help outside developers boarding, we provide an option to work with 3 dummy applications.
Our applications data may be private but anyone is welcome to help us on this project!

- Execute: `python manage.py loaddata fixtures/applications.json`


## Run server

### Local environment

Add 2 environment variables:

- **SG_KEY**: SendGrid API Key
- **TP_KEY**: Typeform API key

Run server to 0.0.0.0
`python manage.py runserver 0.0.0.0:8000`

### Production environment

Currently is set up using Systemd to run gunicorn as a service. See this [tutorial](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04) to understand and set it up as in our server.

In order to deploy you will need a `prod_settings.py` in the app folder. There you must define a new `SECRET_KEY`, set `DEBUG` as False and define the passwords.

1. Run `restart.sh`. This will update the database and static files.
2. Reload gunicorn `sudo service restart gunicorn`

#### Setting up gunicorn service in Systemd

- Edit this file `/etc/systemd/system/gunicorn.service`
- Add this content
```
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=user
Group=www-data
WorkingDirectory=/home/user/project_folder
ExecStart=/home/user/project_folder/env/bin/gunicorn --workers 3 --log-file=/home/user/project_folder/gunicorn.log --bind unix:/home/user/project_folder/backend.sock app.prod_wsgi:ap$

[Install]
WantedBy=multi-user.target

```

- Replace `user` for your user (deploy in our server).
- Replace `project_folder` by the name of the folder where the project is located

## Management Commands

This can be added to crontab for periodic automatic execution.

### Fetch last forms

Fetches all aplications and inserts those who don't exist in the DB

- Set environment variable: **TP_KEY**=Typeform_API_key
- Activate virtualenv (optional)
- Run: `python manange.py insert_missing`

### Check invited applications for expirations

Sends last reminder email to applications invited (not confirmed or cancelled) that are 4 days old. Sets application as expired after 24 hours of sending last reminder email.

- Set environment variable: **SG_KEY**= SendGrid key
- Activate virtualenv (optional)
- Run: `python manange.py check_invites`

