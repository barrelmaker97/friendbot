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
RUN apk add --no-cache gcc musl-dev \
	&& pip install -r requirements.txt --no-cache-dir \
	&& apk del --no-cache gcc musl-dev

FROM dependencies as test
RUN pip install behave --no-cache-dir
COPY ./features /app/features
COPY ./test_data/actions /app/test_data/actions
COPY ./test_data/export /export_unzip
RUN behave

FROM dependencies as release
CMD ["gunicorn", "--access-logfile", "-", "-w", "2", "-k", "gthread", "--threads", "4", "-b", "0.0.0.0:5000", "-c", "gunicorn_config.py", "--worker-tmp-dir", "/dev/shm", "friendbot:app"]
