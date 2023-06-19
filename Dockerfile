# Pull the official base image
FROM python:3.11.4-alpine3.18
LABEL maintainer="https://github.com/AndyLeezard"

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy the required files
COPY ./requirements.txt /requirements.txt
COPY ./app /app
COPY ./scripts /scripts

WORKDIR /app
EXPOSE 8000

# Install and configure Git
RUN apk update && \
    apk add --no-cache curl git
RUN git config --global core.autocrlf input

# Create a virtual environment
RUN python -m venv /py

# Upgrade pip within the virtual environment
RUN /py/bin/pip install --upgrade pip

# Install the PostgreSQL client
RUN apk add --update --no-cache postgresql-client

# Install build dependencies for PostgreSQL and other packages
RUN apk add --update --no-cache --virtual .tmp-deps \
        build-base postgresql-dev musl-dev linux-headers

# Install Python dependencies from requirements.txt
RUN /py/bin/pip install -r /requirements.txt

# Remove temporary build dependencies
RUN apk del .tmp-deps

# Create a non-root user for the container
RUN adduser --disabled-password --no-create-home appuser

# Create directories for static and media files
RUN mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media

# Set ownership and permissions for directories
RUN chown -R appuser:appuser /vol && \
    chmod -R 755 /vol

# Grant executable permissions to scripts
RUN chmod -R +x /scripts

ENV PATH="/scripts:/py/bin:$PATH"

USER appuser

CMD ["run.sh"]