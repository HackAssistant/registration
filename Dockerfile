FROM python:3.5.2

RUN apt-get -q update && apt-get install -y -q \
  sqlite3 --no-install-recommends \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV LANG C.UTF-8

RUN mkdir -p /app
WORKDIR /app

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
ADD . /app
EXPOSE 8000
CMD gunicorn -b :8000  -w 3 --log-file=gunicorn.log app.docker_wsgi:application

