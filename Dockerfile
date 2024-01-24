FROM python:3.10-alpine

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Add cron job file to the container
COPY cronjob /etc/cron.d/cronjob
RUN chmod 0644 /etc/cron.d/cronjob

# Apply cron job
RUN crontab /etc/cron.d/cronjob

# Run the cron service in the background
RUN crond

# Create biene user to not install requirements via root
RUN addgroup -S biene && adduser -S biene -G biene
# Use biene as the default user
USER biene

# Upgrade pip before installing dependencies
RUN pip install --upgrade pip
COPY --chown=biene:biene requirements.txt requirements.txt
# Add bin to path to avoid wanring
ENV PATH="/home/biene/.local/bin:${PATH}"
# Disable cache because it won't be used because it will be installed only when creating image
RUN pip install --no-cache-dir -r requirements.txt

# Mounts the application code to the image
COPY --chown=biene:biene . code
WORKDIR /code

# Generate static files in the container
RUN python manage.py collectstatic --noinput

