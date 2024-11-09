FROM python:3.12.3

WORKDIR /deploy
COPY requirements.txt .

RUN python3 -m pip install -r requirements.txt

ENV STORAGE_DIR=storage
RUN mkdir storage

# need to copy dance-progress into storage dir

COPY app.py .
COPY templates/*.html templates/


ARG PORT
ENV PORT=${PORT}

EXPOSE $PORT

COPY scrape.py .

CMD gunicorn -w 1 app:app -b linedance-tracker:$PORT
