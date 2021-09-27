FROM python:3.9.7-alpine3.13 as base

FROM base as dependencies
WORKDIR /app
COPY ./requirements.txt /app
COPY ./test_data/export.zip /test-export.zip
RUN apk add --no-cache --virtual .deps g++ \
	&& pip install --upgrade pip --no-cache-dir \
	&& pip install -r requirements.txt --no-cache-dir \
	&& apk del --no-cache .deps \
	&& apk add --no-cache libstdc++ \
	&& adduser \
	--disabled-password \
	--gecos "" \
	--no-create-home \
	--uid "1234" \
	"1234"

FROM dependencies as test
ENV FRIENDBOT_SECRET_FILE=./test-secret
ENV FRIENDBOT_EXPORT_ZIP=/test-export.zip
RUN pip install behave --no-cache-dir
COPY ./test_data/test-secret ./test-secret
COPY ./features /app/features
COPY ./test_data/actions /app/test_data/actions
COPY ./friendbot/ /app/friendbot
RUN behave --no-logcapture && touch /test-success

FROM dependencies as production
USER 1234
EXPOSE 8000
COPY --from=test /test-success /
HEALTHCHECK --interval=60s --timeout=3s --retries=1 CMD python healthcheck.py
ENV FRIENDBOT_LOG_LEVEL=info
CMD ["sh", "-c", "gunicorn --log-level ${FRIENDBOT_LOG_LEVEL} --preload -b 0.0.0.0:8000 --worker-tmp-dir /dev/shm friendbot:app"]
COPY ./healthcheck.py /app
COPY ./friendbot/ /app/friendbot
