# syntax=docker/dockerfile:1

FROM node:22-slim AS build

WORKDIR /code

COPY package.json package-lock.json tsconfig.json /code/
COPY src/web /code/src/web

RUN npm install && npm run build

FROM python:3.12-alpine

# Install build dependencies
RUN apk add --no-cache gcc musl libffi postgresql tzdata
RUN ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime

# Set workdir
WORKDIR /code

# Copy requirements and install
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir -e .

# Copy app source and config
COPY src/app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY --from=build /code/dist ./dist

# Run the app with uvicorn
COPY <<-EOT /entrypoint.sh
#!/bin/sh

alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --proxy-headers --port 8000 --workers 4
EOT
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
