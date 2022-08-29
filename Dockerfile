FROM python:3.8-slim-buster

RUN mkdir /app
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python3", "pizza-discord-bot.py"]