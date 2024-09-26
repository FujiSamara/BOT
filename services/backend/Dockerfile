FROM python:latest

ADD . /app

ADD templates /app/templates

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "manage.py"]