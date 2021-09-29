FROM python:3.9.7-alpine as base

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

FROM dependencies as production
USER 1234
EXPOSE 8000
HEALTHCHECK --interval=60s --timeout=3s --retries=1 CMD python healthcheck.py
ENV FRIENDBOT_LOG_LEVEL=info
CMD ["sh", "-c", "gunicorn --log-level ${FRIENDBOT_LOG_LEVEL} --preload -w 1 -k gthread --threads 4 -b 0.0.0.0:8000 --worker-tmp-dir /dev/shm friendbot:app"]
COPY ./healthcheck.py /app
COPY ./friendbot/ /app/friendbot
