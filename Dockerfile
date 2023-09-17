FROM python:3.11-buster

ENV PYTHONUNBUFFERED 1

RUN pip3 install --upgrade pip
RUN pip3 install gunicorn

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
# WORKDIR /app

RUN python3 manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "retrato.wsgi:application"]
# CMD ["python3", "manage.py", "runserver", "--settings=retrato.config.gdrive_settings", "0.0.0.0:8000"]
