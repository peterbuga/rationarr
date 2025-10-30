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

RUN addgroup -g 1000 ${APP_USER} && \
    adduser -h ${HOMEDIR} -G ${APP_USER} -u 1000 -D ${APP_USER}

# gcc libffi postgresql musl
RUN apk add --no-cache tzdata curl
RUN ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime

WORKDIR $HOMEDIR

COPY --chown=${APP_USER}:${APP_USER} pyproject.toml README.md ./
RUN pip install --no-cache-dir -e .

COPY --chown=${APP_USER}:${APP_USER} src/app/ ./app/
COPY --chown=${APP_USER}:${APP_USER} alembic/ ./alembic/
COPY --chown=${APP_USER}:${APP_USER} alembic.ini .
COPY --chown=${APP_USER}:${APP_USER} --from=build /code/src/web/out ./dist

COPY --chown=${APP_USER}:${APP_USER} <<-EOT /entrypoint.sh
#!/bin/sh

alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --proxy-headers --port 8000 --workers 4
EOT
RUN chmod +x /entrypoint.sh

USER ${APP_USER}
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
