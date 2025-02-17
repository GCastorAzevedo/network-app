FROM python:3.12.9-alpine3.21 AS python-base

RUN pip install --upgrade pip

RUN pip install pipenv

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv install --system --deploy

FROM python-base AS whollygraph-api

WORKDIR /app

COPY ./common common
COPY ./graph_api graph_api
COPY ./graph_db graph_db

ENV PROJECT_NAME=whollygraph_api

SHELL [ "/bin/sh", "-c" ]
