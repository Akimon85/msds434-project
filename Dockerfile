#The official lightweight Python image from hub.docker.com
FROM python:3.9-slim


ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
COPY . /src
WORKDIR /src



RUN pip install -r requirements.txt
#EXPOSE 8080
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
