FROM python:3.11

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

EXPOSE 4000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "4000", "--workers", "1"]