# Northwestern MSDS434 - Akira Noda
# Analytics Application Engineering- Term Project - June 2022

This project was created to demonstrate proficiency with creating and deploying machine learning applications in the cloud. The program was written primarily in python and does the following:

1.Retrieve a dataset from Kaggled servers, processes it in python, and uploads it to Google BigQuery.

2.Trains and evaluate a logistic regression classification model using Google BigQuery ML and make predications.

3.Submit predictions to kaggle competition and retrieve submission score.

4.Generate an interactive dashboard application using plotly.dash and deploy to the web via Google App Engine.

The app is currently deployed at https://msds343-project.uw.r.appspot.com/

### **Architecture Diagram**

![Slide1](https://user-images.githubusercontent.com/103208143/172032753-2421dbfd-ecac-4a04-aba4-522c55bd4ce6.JPG)

### **Source Code**
The source code for this project was written using Google Shell Editor, JupyterLab, and stored in GitHub repo https://github.com/Akimon85/msds434-project. GitHub Actions was used to run tests using pytest and pylint automatically when new code is pushed to the repo. The contents of the repo is pushed to Google Cloud Platform (GCP) as a docker container for deployment.
```docker
#Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . main.py /app/

RUN pip install -r requirements.txt
EXPOSE 8080
ENTRYPOINT [ "python" ]
CMD [ "main.py" ]
```
### **Data**
The dataset used for the ML portion of this project was from Kaggle's Spaceship Titanic Competiton, in which you are tasked with predicting which passengers were transported to another dimension when "the unwary Spaceship Titanic collided with a spacetime anomaly hidden within a dust cloud". The python backend main.py script retrieves a Kaggle API token store in Google Secret Manager and supplies it to the Kaggle API for authentication, then it downloads the dataset from Kaggle servers. The data is cleaned using python pandas & scikit-learn modules and then imported into Google BigQuery tables via google-bigquery API.
```python
client = bigquery.Client(project="msds343-project")
table_ref = client.dataset("ZenDesk").table("final")
table_ref2 = client.dataset("ZenDesk").table("test")
job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
job_config.autodetect = True
client.load_table_from_dataframe(data, table_ref, job_config).result()
client.load_table_from_dataframe(test, table_ref2, job_config).result()
```

### **ML Modeling and Prediction**
API calls are made to BigQuery to create and training a logistic regression classification model. Then model evaluation results and test set predictions are generated via GCP BigQuery API. The predictions are formatted and saved as a csv file using python, then submitted to Kaggled for scoring via the kaggled API.
```python
query_job = client.query("""
    CREATE OR REPLACE MODEL `msds343-project.ZenDesk.final_model`
        OPTIONS(model_type='logistic_reg',labels=['Transported']) AS
    SELECT * FROM `msds343-project.ZenDesk.final`
    """)
query_job.result()
```
### **Dashboard Application Deployment**
An interactive dashboard using various visualizations and prediction results were generated using plotly dash, and can be deployed with local host or on the web via Google Cloud Build & App Engine. Two separate GCP projects were created as development and production environments, linked to two branches of the GitHub source code repo. 
```python
#app.yml - App Config File

runtime: python39
instance_class: F4_1G
entrypoint: gunicorn -b 0.0.0.0:8080 main:server
```
![image](https://user-images.githubusercontent.com/103208143/172066428-07868c67-d14b-4ba9-af5f-acfe3716a70b.png)

![image](https://user-images.githubusercontent.com/103208143/172066449-f53159cc-0dd5-4e50-9dc0-1c041744c99c.png)

![image](https://user-images.githubusercontent.com/103208143/172066466-de7e0955-24fd-4297-a630-f6c89f2fb1c2.png)

### **Monitoring**

Google Cloud Operation Suite (stackdriver) is used to monitor various performance and cost metrics of the GCP project and setup app uptime alerts.
![image](https://user-images.githubusercontent.com/103208143/172067533-cf5f6975-697b-48f7-b255-662c2b3f7fce.png)

