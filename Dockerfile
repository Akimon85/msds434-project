#The official lightweight Python image from hub.docker.com
FROM python:3.9-slim


#ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
#WORKDIR /src
#COPY . /src
WORKDIR /app
COPY . main.py /app/
COPY . train.csv /app/
COPY . test.csv /app/

RUN pip install -r requirements.txt

#CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:server
#CMD exec gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 8 --timeout 0 main:server


EXPOSE 8080

ENTRYPOINT [ "python" ]

CMD [ "main.py" ]
