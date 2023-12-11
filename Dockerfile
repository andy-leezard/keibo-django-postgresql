# Pull the official base image
FROM python:3.11.4-alpine3.18
LABEL maintainer="https://github.com/AndyLeezard"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Update (refresh) the index of available packages
RUN apk update

# Install build-base and linux-headers
RUN apk add --upgrade --no-cache build-base linux-headers

# Install the PostgreSQL client
RUN apk add --no-cache postgresql-client

# Install temporary build dependencies
RUN apk add --no-cache --virtual .tmp-deps \
        postgresql-dev musl-dev

# Install Python dependencies from requirements.txt
COPY ./requirements.txt /requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /requirements.txt

# Remove temporary build dependencies
RUN apk del .tmp-deps

# Copy the required files
COPY ./app /app
WORKDIR /app

# Create directories for static and media files
RUN mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media

# Create a non-root user for the container
RUN adduser --disabled-password --no-create-home appuser

# Create a non-root user and change ownership
RUN chown -R appuser:appuser /vol && \
    chmod -R 755 /vol

COPY ./scripts /scripts
# Grant executable permissions to scripts
RUN chmod -R +x /scripts

USER appuser

CMD ["../scripts/run.sh"]
