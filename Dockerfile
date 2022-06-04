#The official lightweight Python image from hub.docker.com
FROM python:3.9-slim


#ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
#WORKDIR /src
#COPY . /src
WORKDIR /app
COPY . main.py /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
#CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
CMD [ "main.py" ]
ENTRYPOINT [ "python" ]
