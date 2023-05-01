FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY ./reqs/main.txt .
RUN pip install -U pip && \
    pip install --no-cache-dir -r main.txt

COPY ./entrypoint.sh .
RUN chmod +x /usr/src/app/entrypoint.sh

ENTRYPOINT [ "/bin/sh", "/usr/src/app/entrypoint.sh" ]