# Setting Up myhackupc Locally

## Prerequisites

- Python 3.10

If you don't have Python 3.10 (e.g. Ubuntu 24.04 no longer ships it), install it with [uv](https://docs.astral.sh/uv/):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.10
python3.10 --version
```

This puts a `python3.10` executable in `~/.local/bin`; make sure that directory is in your `PATH`.

---

## Installation

```bash
git clone https://github.com/hackupc/myhackupc && cd myhackupc
python3.10 -m venv env
source ./env/bin/activate
pip install -r requirements.txt
```

> **Note on virtualenv:** Use `python -m venv` rather than the system `virtualenv` package. On Debian/Ubuntu, `virtualenv` installs a patched `setuptools` that fails to build some old dependencies with `AttributeError: install_layout`.

> **Note on psycopg2-binary:** If you get an error, install openssl@3 and export LDFLAGS, CPPFLAGS, and PKG_CONFIG_PATH before running pip install.

---

## Configuration

Open `app/hackathon_variables.py` and set the required variables. You can reference the variables documented in `README.md` under "Available environment variables".

Open `app/hackathon_variables.py` and set at minimum:
- `HACKATHON_NAME`
- `HACKATHON_DOMAIN` (use `localhost:8000` for local dev)
- Application deadlines

---

## Database

```bash
python manage.py migrate
python manage.py createsuperuser
```

---

## Running the Dev Server

```bash
source ./env/bin/activate
python manage.py runserver
```

Visit http://localhost:8000. Log in with the superuser you created.

---

## Environment Variables (Optional)

| Variable | Purpose |
|----------|---------|
| **SG_KEY** | SendGrid API Key. Mandatory if you want to use SendGrid as your email backend. You can manage them [here](https://app.sendgrid.com/settings/api_keys). If not added, the system will write all emails to the filesystem for preview. |
| **PROD_MODE** | (optional) Disables Django debug mode. |
| **SECRET** | (optional) Sets web application secret. You can generate a random secret with python running: `os.urandom(24)` |
| **DATABASE_URL** | (optional) URL to connect to the database. If not set, defaults to django default SQLite database. See schema for different databases [here](https://github.com/kennethreitz/dj-database-url#url-schema). |
| **DATABASE_SECURE** | (optional) Whether or not to use SSL to connect to the database. Defaults to `true`. |
| **DOMAIN** | (optional) Domain where app will be running. Default: localhost:8000 |
| **SL_TOKEN** | (optional) Slack token to invite hackers automatically on confirmation. You can obtain it [here](https://api.slack.com/custom-integrations/legacy-tokens) |
| **SL_TEAM** | (optional) Slack team name (xxx on xxx.slack.com) |
| **DROPBOX_OAUTH2_TOKEN** | (optional) Enables DropBox as file upload server instead of local computer. |
| **SL_BOT_ID** | (optional) Slack bot ID to send messages from. |
| **SL_BOT_TOKEN** | (optional) Slack bot token to send messages. |
| **SL_BOT_CHANNEL** | (optional) General channel to refer from the bot messages. |
| **SL_BOT_DIRECTOR1** | (optional) User ID of one of the directors. |
| **SL_BOT_DIRECTOR2** | (optional) User ID of the other director. |
| **MLH_CLIENT_SECRET** | (optional) Enables MyMLH as a sign up option. Format is `client_id@client_secret` |
| **CAS_SERVER** | (optional) Enables login for other platforms |
| **GOOGLE_WALLET_APPLICATION_CREDENTIALS** | (optional) The path to the json key file containing all google-related API credentials |
| **GOOGLE_WALLET_ISSUER_ID** | (optional) The issuer ID of Google Wallet Pass API |
| **GOOGLE_WALLET_CLASS_SUFFIX** | (optional) The name of the class created at the [Google Wallet Console](https://pay.google.com/business/console/passes/) |

---

## Verifying Your Changes

After making code changes:

1. Restart the dev server (`Ctrl+C`, then `python manage.py runserver`)
2. Navigate to the affected page in the browser
3. If you changed a model, run `python manage.py makemigrations && python manage.py migrate`
4. If you changed CSS, hard-refresh the browser (Ctrl+Shift+R / Cmd+Shift+R)
