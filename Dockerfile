FROM python:3.7-alpine

ENV EXPORT_DIR /export

RUN pip install friendbot gunicorn --no-cache-dir

CMD ["gunicorn", "-w 4", "-b 0.0.0.0:5000", "friendbot:app"]
