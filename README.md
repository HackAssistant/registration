<br>
<p align="center">
  <img alt="HackCU" src="https://github.com/HackCU/splash-page/blob/master/img/hackcu_black.png" width="200"/>
</p>
<br>


[![Maintainability](https://api.codeclimate.com/v1/badges/0806a9c40ea11ded0efd/maintainability)](https://codeclimate.com/github/HackCU/backend/maintainability)
[![Build Status](https://travis-ci.org/HackCU/backend.svg?branch=master)](https://travis-ci.org/hackcu/backend)

Backend for hackathon application management. Forked and adapted from [HackUPC's Backend](https://github.com/hackupc/backend).

## Features

- Email sign up and basic data management interface for hackers
- Role management: Organizer, Volunteer and Director
- Review and vote application interface
- Sends invites and controls confirmation and cancellation application flow
- Check-in interface with QR scanner
- Admin dashboard
- Flexible email backend (SendGrid is the default supported backend)
- Reimbursement management interface
- (Optional) Slack invites on confirm and on demand in admin interface



## Setup

Needs: Python 3.X, virtualenv

- `git clone https://github.com/hackupc/backend && cd backend`
- `virtualenv env --python=python3`
- `source ./env/bin/activate`
- (Optional) If using Postgres, set up the necessary environment variables for its usage before this step
- `pip install -r requirements.txt`. For production run: `pip install -r requirements/prod.txt`
- `python manage.py migrate`
- `python manage.py createsuperuser`

## Available enviroment variables

- **SG_KEY**: SendGrid API Key. Mandatory if you want to use SendGrid as your email backend. You can manage them [here](https://app.sendgrid.com/settings/api_keys).  Note that if you don't add it the system will write all emails in the filesystem for preview.
You can replace the email backend easily. See more [here](https://djangopackages.org/grids/g/email/). Also enables Sendgrid lists integration.
- **PROD_MODE**(optional): Disables debug mode. Avoids using filesystem mail backend.
- **SECRET**(optional): Sets web application secret. You can generate a random secret with python running: `os.urandom(24)`
- **PG_PWD**(optional): Postgres password. Also enables Postgres as the default database with the default values specified below.
- **PG_NAME**(optional): Postgres database name. Default: backend
- **PG_USER**(optional): Postgres user. Default: backenduser
- **PG_HOST**(optional): Postgres host. Default: localhost
- **DOMAIN**(optional): Domain where app will be running. Default: localhost:8000
- **SL_TOKEN**(optional): Slack token to invite hackers automatically on confirmation. You can obtain it [here](https://api.slack.com/custom-integrations/legacy-tokens)
- **SL_TEAM**(optional): Slack team name (xxx on xxx.slack.com)
- **EMAIL_HOST_PASSWORD**(optional): STMP host password for admin emails. Enables admin emails.
- **EMAIL_HOST**(optional): STMP host name. Defaults: smtp.sendgrid.net
- **EMAIL_HOST_USER**(optional): STMP host username. Defaults: hupc_mail


## Run server

### Local environment

- Add `SG_KEY` in environment (if you want to send emails)
- `python manage.py runserver`

### Production environment

See this [tutorial](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04) to understand and set it up as in our server.

#### Set up gunicorn service in Systemd
Needs: Systemd.
- Create server.sh from template: `cp server.sh.template server.sh`
- `chmod +x server.sh`
- Edit variables to match your environment
- Run `restart.sh`. This will update the database, dependecies and static files.
- Edit this file `/etc/systemd/system/backend.service`
- Add this content
```
[Unit]
Description=backend daemon
After=network.target

[Service]
User=user
Group=www-data
WorkingDirectory=/home/user/project_folder
ExecStart=/home/user/project_folder/server.sh >>/home/user/project_folder/out.log 2>>/home/user/project_folder/error.log

[Install]
WantedBy=multi-user.target

```

- Replace `user` for your user (deploy in our server).
- Replace `project_folder` by the name of the folder where the project is located
- Create and enable service: `sudo systemctl start backend && sudo systemctl enable backend`

#### Deploy new version

Needs: Postgres environment variables set

- `git pull`
- `./restart.sh`
- `sudo service backend restart`


#### Set up Postgres

Needs: PostgreSQL installed

- Enter PSQL console: `sudo -u postgres psql`
- Create database: `CREATE DATABASE backend;`
- Create user for database: `CREATE USER backenduser WITH PASSWORD 'password';` (make sure to include a strong password)
- Prepare user for Django

```sql
ALTER ROLE backenduser SET client_encoding TO 'utf8';
ALTER ROLE backenduser SET default_transaction_isolation TO 'read committed';
ALTER ROLE backenduser SET timezone TO 'UTC';
```

- Grant all priviledges to your user for the created database: `GRANT ALL PRIVILEGES ON DATABASE myproject TO myprojectuser;`
- Exit PSQL console: `\q`

Other SQL engines may be used, we recommend PostgreSQL for it's robustness. To use other please check [this documentation](https://docs.djangoproject.com/en/1.11/ref/databases/) for more information on SQL engines in Django.

#### Set up nginx

Needs: Nginx

- `sudo vim /etc/nginx/sites-available/default`
- Add site:

```
server {
    listen 80;
    listen [::]:80;

    server_name my.hackupc.com;


    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        alias /home/user/project_folder/staticfiles/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/user/project_folder/backend.sock;
    }


}
```

### Set up dummy data

TODO: CREATE NEW DUMMY DATA


## Management

### Commands

- `SG_KEY=REPLACE_WITH_SENDGRID_KEY python manange.py expire_applications`: Sends last reminder email to applications invited (not confirmed or cancelled) that are 4 days old. Sets application as expired after 24 hours of sending last reminder email.


#### Production

Create your own management.sh script and add to crontab.

- Create management.sh from template: `cp management.sh.template management.sh`
- `chmod +x management.sh`
- Edit variables to match your environment
- Add to crontab: `crontab -e`
```
*/5 * * * * cd /home/user/project_folder/ && ./management.sh > /home/user/project_folder/management.log 2> /home/user/project_folder/management_err.log
```

### User roles

- **is_volunteer**: Allows user to check-in hackers with QR and list view
- **is_organizer**: Allows user to vote, see voting ranking and check-in hackers.
- **is_director**: Allows user to enter Admin interface and invite hackers


## Personalization

You can personalize this backend in style and strings for your hackathon.

### Style

For colors and presentation of views you can edit [app/static/css/main.css](app/static/css/main.css).

To edit the navbar content/disposition you can modify [app/templates/base.html](app/templates/base.html)

The email base template is in [app/templates/base_email.html](app/templates/base_email.html)

### Content

- Emails:
    - Hackers (application invite, event ticket): [hackers/templates/mails/](register/templates/mails/)
    - Reimbursement (reimbursement email): [reimbursement/templates/mails/](reimbursement/templates/mails/)
- General information (documented in the file itself): [app/settings.py](app/settings.py)

# Want to Contribute?
Read these [guidelines](.github/CONTRIBUTING.md) carefully.

By making a contribution, in any form (including, but not limited to, Issues and Pull Requests), you agree to abide by the [Code of Conduct](.github/CODE_OF_CONDUCT.md). Report any incidents to devs@hackcu.org and appropriate action will be taken against the offender after investigation.

# License

MIT © Hackers@UPC

MIT © HackCU
