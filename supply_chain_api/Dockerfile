FROM python:3.12.9-alpine3.21 AS python-base

RUN pip install --upgrade pip

RUN pip install pipenv

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv install --system --deploy

FROM python-base AS supply-chain-api

WORKDIR /app

COPY ./common common
COPY ./supply_chain_api supply_chain_api
COPY ./supply_chain_db supply_chain_db

ENV PROJECT_NAME=supply_chain_api

SHELL [ "/bin/sh", "-c" ]
