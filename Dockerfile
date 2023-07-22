FROM python:3.8.17-slim-bullseye AS base

ENV VIRTUAL_ENV=/venv
ENV POETRY=/root/.local
ENV PATH="$POETRY/bin:$VIRTUAL_ENV/bin:$PATH"
ENV REKENBER_GSPREAD_LICENSE_PATH=/license.json

RUN apt-get update \
    && apt-get install -yqq \
        libpq5 \
        tk 

FROM base AS builder

RUN apt-get update \
    && apt-get install -yqq \
        curl \
        wget \
        git \        
        build-essential \
        libpq-dev 

RUN curl -sSL \
        https://install.python-poetry.org \
    | python -

RUN python -m venv $VIRTUAL_ENV

WORKDIR /install

COPY experiments-lib/pyproject.toml \
    experiments-lib/poetry.lock \
    experiments-lib/

RUN cd experiments-lib \
    && poetry export --without-hashes -f requirements.txt \
       | grep -v file:// > requirements.txt \
    && pip install -U pip \
    && pip install -r requirements.txt


FROM base AS final


COPY --from=builder $POETRY $POETRY
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV

WORKDIR /install

COPY experiments-lib/ experiments-lib/

RUN cd /install/experiments-lib && poetry build && pip install dist/*.whl --no-deps

WORKDIR /experiments
COPY Snakefile Snakefile
