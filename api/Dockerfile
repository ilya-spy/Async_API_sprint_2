FROM python:3.9.12-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN groupadd -r web && useradd -r -g web web
RUN mkdir /home/web

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# allow access to app files for web user before switch into web
RUN chown web:web -R /app && chown web:web -R /home/web
USER web

CMD ["make", "run"]
