FROM python:3.9.7-alpine as base

FROM base as dependencies
COPY ./requirements.txt /
COPY ./install.sh /
RUN /install.sh
WORKDIR /home/friendbot
USER friendbot
EXPOSE 8000
HEALTHCHECK --interval=60s --timeout=3s --retries=1 CMD python healthcheck.py
ENV FRIENDBOT_LOG_LEVEL=info
CMD ["sh", "-c", "gunicorn --log-level ${FRIENDBOT_LOG_LEVEL} --preload -w 1 -k gthread --threads 4 -b 0.0.0.0:8000 --worker-tmp-dir /dev/shm friendbot:app"]
COPY ./healthcheck.py .
COPY ./friendbot/ ./friendbot
