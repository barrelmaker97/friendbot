ARG BASE_IMAGE=python:3.7-alpine
FROM $BASE_IMAGE as base
COPY ./friendbot/ /app/friendbot
COPY ./gunicorn_config.py /app

FROM base as lint
RUN pip install black --no-cache-dir
RUN black --check --diff /app

FROM base as dependencies
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install -r requirements.txt --no-cache-dir

FROM dependencies as test
COPY ./features /app/features
COPY ./test_data/actions /app/test_data/actions
COPY ./test_data/export /export_unzip
RUN pip install behave --no-cache-dir
RUN behave

FROM dependencies as release
CMD ["gunicorn", "-w 4", "-b 0.0.0.0:5000", "-c gunicorn_config.py", "friendbot:app"]
