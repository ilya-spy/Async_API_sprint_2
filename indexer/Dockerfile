FROM python:3.9.12-buster
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN groupadd -r web && useradd -r -g web web && chown web:web -R /app

COPY --chown=web:web ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

USER web

COPY --chown=web:web ./ /app

CMD ["make", "load"]