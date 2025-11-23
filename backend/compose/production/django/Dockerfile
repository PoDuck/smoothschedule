FROM python:3.11-slim-bullseye as python

# Python build stage
FROM python as python-build-stage

# Install build dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip wheel --wheel-dir /usr/src/app/wheels \
    -r /requirements/production.txt

# Python run stage
FROM python as python-run-stage

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV DJANGO_SETTINGS_MODULE config.settings.production

RUN apt-get update && apt-get install --no-install-recommends -y \
    # psycopg2 dependencies
    libpq-dev \
    # Translations dependencies
    gettext \
    # cleaning up unused files
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependency wheels from python-build-stage
COPY --from=python-build-stage /usr/src/app/wheels /wheels/

# use wheels to install python dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
    && rm -rf /wheels/

COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

WORKDIR /app

# copy application code to WORKDIR
COPY . /app

# collect static files
RUN python manage.py collectstatic --noinput

ENTRYPOINT ["/entrypoint"]
