# syntax=docker/dockerfile:1
FROM python:3.9-slim-buster
WORKDIR /app
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
RUN apt-get update && apt-get install -y \
    sox \
    libsox-fmt-mp3 \
    && rm -rf /var/lib/apt/lists/* \
RUN hash -r
COPY . .
CMD ["python", "app.py"]
