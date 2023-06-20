FROM python:3.10-alpine

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "main:app" ,"--bind", "0.0.0.0:80"]
