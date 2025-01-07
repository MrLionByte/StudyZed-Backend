FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN adduser -D -s /bin/sh studyzedUser

USER studyzedUser

EXPOSE 8000

COPY . /app
