#The official lightweight Python image from hub.docker.com
FROM python:3.10-slim-buster


ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app 
WORKDIR $APP_HOME
COPY . ./

RUN pip install Flask gunicorn panda numpy sklearn


CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app