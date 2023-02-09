FROM python:3.11.2-alpine
RUN adduser --disabled-password --gecos "" --uid "1234" "friendbot"
USER friendbot
WORKDIR /home/friendbot
ENV PATH="/home/friendbot/.local/bin:${PATH}"
COPY ./requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt \
	&& rm requirements.txt
EXPOSE 8000
HEALTHCHECK --interval=60s --timeout=3s --retries=1 CMD python healthcheck.py
ENV FRIENDBOT_LOG_LEVEL=info
CMD ["sh", "-c", "gunicorn --log-level ${FRIENDBOT_LOG_LEVEL} --preload -w 1 -k gthread --threads 4 -b 0.0.0.0:8000 --worker-tmp-dir /dev/shm friendbot:app"]
COPY ./example-data/export.zip ./export.zip
COPY ./healthcheck.py .
COPY ./friendbot/ ./friendbot
