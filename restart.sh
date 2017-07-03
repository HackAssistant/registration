#!/bin/sh
echo "checking updates..."
./env/bin/pip install -r requirements.txt
echo "checking updates...done"
echo "migrating db..."
./env/bin/python manage.py migrate
echo "migrating db...done"
echo "collecting static..."
./env/bin/python manage.py collectstatic --no-input
echo "collecting static...done"
echo "removing all pyc..."
find . -name \*.pyc -delete
echo "removing all pyc...done"
echo "Deploy completed. The game is on!"
