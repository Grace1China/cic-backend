FROM python:3.6-alpine3.9

WORKDIR /var/www/html
COPY . .
RUN pip install pipenv\
    && pipenv sync

EXPOSE 80 80
CMD ["python", "manage.py", "runserver"]