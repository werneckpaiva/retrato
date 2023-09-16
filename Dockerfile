FROM python:3.11 AS builder

ENV PYTHONUNBUFFERED 1

WORKDIR ./
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
