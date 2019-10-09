ARG BASE_IMAGE
FROM $BASE_IMAGE as base
COPY ./Dockerfile ./qemu-arm-static* /usr/bin/
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install -r requirements.txt --no-cache-dir
COPY ./friendbot/ /app/friendbot

FROM base As lint
RUN pip install black
RUN black --check --diff /app

FROM base As test
COPY ./features /app/features
COPY ./test_data /app/test_data
ENV EXPORT_DIR /app/test_data/export
RUN pip install behave
RUN behave

FROM base as release
ENV EXPORT_DIR /export
CMD ["gunicorn", "-w 4", "-b 0.0.0.0:5000", "friendbot:app"]
