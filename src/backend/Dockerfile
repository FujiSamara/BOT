FROM python:latest

ADD . /app

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "manage.py"]