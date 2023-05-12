FROM python:3.8
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "stac_validator:app" ,"--bind", "0.0.0.0:80"] (env) ivica@icepad-2:~/Coding/os/stac-validator-api$ 