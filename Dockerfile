ARG BASE_IMAGE=python:3.8-alpine
FROM $BASE_IMAGE as base

FROM base as lint
RUN apk add --no-cache --virtual .deps gcc musl-dev \
	&& pip install --upgrade pip --no-cache-dir \
	&& pip install black --no-cache-dir
COPY ./friendbot/ /app/friendbot
RUN black --check --diff /app && touch /lint-success

FROM base as dependencies
WORKDIR /app
COPY ./requirements.txt /app
RUN apk add --no-cache --virtual .deps g++ \
	&& pip install --upgrade pip --no-cache-dir \
	&& pip install -r requirements.txt --no-cache-dir \
	&& apk del --no-cache .deps \
	&& apk add --no-cache libstdc++

FROM dependencies as test
ENV SLACK_SIGNING_SECRET=abcdef12345abcdef12345abcdef1234
RUN pip install behave --no-cache-dir
COPY ./features /app/features
COPY ./test_data/actions /app/test_data/actions
COPY ./test_data/export.zip /
COPY ./friendbot/ /app/friendbot
RUN behave && touch /test-success

FROM dependencies as production
EXPOSE 6000
COPY --from=lint /lint-success /
COPY --from=test /test-success /
HEALTHCHECK --interval=60s --timeout=3s --retries=1 CMD python healthcheck.py
CMD ["gunicorn", "--preload", "-w", "2", "-k", "gthread", "--threads", "4", "-b", "0.0.0.0:6000", "--worker-tmp-dir", "/dev/shm", "friendbot:app"]
COPY ./healthcheck.py /app
COPY ./friendbot/ /app/friendbot
