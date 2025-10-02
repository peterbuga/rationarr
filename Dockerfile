# syntax=docker/dockerfile:1

FROM node:22-slim AS build

WORKDIR /code

COPY package.json package-lock.json eslint.config.mjs /code/
COPY src/web /code/src/web

RUN npm install && npm run build

FROM python:3.12-alpine

ENV HOMEDIR=/code \
    APP_USER=rationarr \
    LANGUAGE=C.UTF-8 \
	LANG=C.UTF-8 \
	LC_ALL=C.UTF-8 \
    LC_CTYPE=C.UTF-8 \
    LC_MESSAGES=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/code

RUN adduser ${APP_USER} -d ${HOMEDIR} --gecos '' --disabled-password --uid 1000

# gcc libffi postgresql musl
RUN apk add --no-cache tzdata curl
RUN ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime

WORKDIR $HOMEDIR

COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir -e .

COPY src/app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY --from=build /code/src/web/out ./dist

COPY <<-EOT /entrypoint.sh
#!/bin/sh

alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --proxy-headers --port 8000 --workers 4
EOT
RUN chmod +x /entrypoint.sh

USER ${APP_USER}
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
