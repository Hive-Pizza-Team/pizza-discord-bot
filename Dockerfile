FROM python:3.11-buster

RUN mkdir /app
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED 1
CMD ["python3", "pizza-discord-bot.py"]