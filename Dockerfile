FROM python:3.7-alpine

ENV EXPORT_DIR /export

WORKDIR /app

COPY ./requirements.txt /app

RUN pip install -r requirements.txt --no-cache-dir

COPY ./friendbot/ /app/friendbot

CMD ["gunicorn", "-w 4", "-b 0.0.0.0:5000", "friendbot:app"]
