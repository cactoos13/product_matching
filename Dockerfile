# Use lightweight Python image based on Alpine
FROM python:3.11-alpine
#FROM python:3-11-slim

# Set environment variables
ENV POETRY_VERSION=1.8.2 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true

# Set working directory
WORKDIR /app

# Install system dependencies required for Poetry and building packages
RUN apk add --no-cache \
    curl \
    build-base \
    gcc \
    gfortran \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev \
    py3-pip \
    openblas-dev


# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files first (for better caching)
COPY pyproject.toml poetry.lock* /app/

# Install dependencies (without dev dependencies)
RUN poetry install --no-root --no-dev

# Copy application source code
COPY . /app/

