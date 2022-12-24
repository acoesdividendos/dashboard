FROM python:3.8

WORKDIR /app

ADD . /app

RUN pip3 install -r requirements.txt