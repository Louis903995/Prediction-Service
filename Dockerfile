FROM python:3.12.7-slim 

WORKDIR /app

COPY . /app

RUN pdm install
