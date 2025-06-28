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


# Expose FastAPI port
EXPOSE 8000

# Run the app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--proxy-headers", "--port", "8000", "--workers", "4"]
