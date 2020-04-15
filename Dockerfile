ARG BASE_IMAGE=python:3.8-alpine
FROM $BASE_IMAGE as base
COPY ./friendbot/ /app/friendbot
COPY ./healthcheck.py /app

FROM base as lint
RUN apk add --no-cache gcc musl-dev \
	&& pip install --upgrade pip --no-cache-dir \
	&& pip install black --no-cache-dir \
	&& apk del --no-cache gcc musl-dev
RUN black --check --diff /app

FROM base as dependencies
WORKDIR /app
COPY ./requirements.txt /app
RUN apk add --no-cache gcc musl-dev \
	&& pip install --upgrade pip --no-cache-dir \
	&& pip install -r requirements.txt --no-cache-dir \
	&& apk del --no-cache gcc musl-dev

FROM dependencies as test
RUN pip install behave --no-cache-dir
COPY ./features /app/features
COPY ./test_data/actions /app/test_data/actions
COPY ./test_data/export.zip /export
RUN behave

FROM dependencies as release
HEALTHCHECK --interval=30s --timeout=3s --start-period=0s --retries=0 CMD python healthcheck.py
CMD ["gunicorn", "--preload", "--access-logformat", "%(t)s %(p)s %(r)s %(s)s %(b)s %(a)s %(L)ss", "--access-logfile", "-", "-w", "2", "-k", "gthread", "--threads", "4", "-b", "0.0.0.0:5000", "--worker-tmp-dir", "/dev/shm", "friendbot:app"]
