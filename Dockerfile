FROM python:3.12.3

WORKDIR /deploy
COPY requirements.txt .

RUN python3 -m pip install -r requirements.txt

COPY app.py .
COPY templates/ templates/
COPY dance-progress.db .

EXPOSE 5000

CMD flask --app app run -h 0.0.0.0 -p 5000
