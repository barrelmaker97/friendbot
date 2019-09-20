FROM python:3.7-alpine

ENV EXPORT_DIR /export

WORKDIR /app

COPY ./friendbot/ /app/friendbot
COPY ./requirements.txt /app

WORKDIR /app

RUN pip install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "-w 4", "-b 0.0.0.0:5000", "friendbot:app"]
