ARG PYTHON_IMAGE

FROM alpine:3.14 as fetcher

RUN apk add --no-cache curl
RUN curl -sSL https://api.github.com/repos/gi0baro/poetry-bin/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/' > .poetry-bin_version
RUN curl -sSL https://github.com/gi0baro/poetry-bin/releases/download/$(cat .poetry-bin_version)/poetry-bin-$(cat .poetry-bin_version)-x86_64-unknown-linux-gnu.tar.gz > poetry-bin.tar.gz
RUN mkdir -p /opt/poetry_bin && tar xzf poetry-bin.tar.gz --directory /opt/poetry_bin

FROM python:${PYTHON_IMAGE}

COPY --from=fetcher /opt/poetry_bin /opt/poetry_bin

RUN ln -s /opt/poetry_bin/poetry /bin/poetry

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_NO_INTERACTION=1
