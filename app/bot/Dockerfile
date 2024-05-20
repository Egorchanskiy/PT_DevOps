FROM python:3.10-alpine

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY ./bot.py /app

CMD python3 bot.py
