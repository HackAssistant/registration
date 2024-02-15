FROM python:3.10-alpine

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Upgrade pip before installing dependencies
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
# Add bin to path to avoid wanring
ENV PATH="/home/biene/.local/bin:${PATH}"
# Disable cache because it won't be used because it will be installed only when creating image
RUN pip install --no-cache-dir -r requirements.txt

# Mounts the application code to the image
COPY . code
WORKDIR /code

# Generate static files in the container
RUN python manage.py collectstatic --noinput

# Add crons from crontab django module to system cron
RUN python manage.py crontab add
