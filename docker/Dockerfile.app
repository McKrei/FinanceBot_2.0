FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt update -y && \
    apt install -y python3-dev \
    gcc \
    musl-dev

RUN pip install --upgrade pip

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
EXPOSE 2313

# CMD ["tail", "-f", "/dev/null"]
CMD ["bash", "-c", "cd finance && python manage.py runbot"]
# CMD ["bash", "-c", "cd finance && python manage.py runserver 0.0.0.0:2313"]
