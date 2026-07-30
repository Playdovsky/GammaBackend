FROM python:3.14-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

RUN apt-get update -y && apt-get install -y sqlite3

COPY . /app/

CMD ["fastapi", "run", "--host", "0.0.0.0", "--port", "80"]

# To run locally use: docker run --env-file .env --name gamma-backend -p 80:80 playdovsky/gamma-backend