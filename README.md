### Northwestern MSDS434 - Analytics Application Engineering - Term Project
### Akira Noda - Spring 2022

This project was created to demonstrate proficiency with creating and deploying machine learning applications in the cloud. The program was written primarily in python and peforms the following tasks:

1.Retrieve a dataset from competition dataset from Kaggle servers, processes it in python, and uploads it to Google BigQuery.

2.Trains and evaluate a logistic regression classification model using Google BigQuery ML and make predications.

3.Submit predictions to kaggle competition and retrieve submission score.

4.Generate an interactive dashboard application using plotly.dash and deploy to the web via Google App Engine.

The app is currently deployed at https://msds343-project.uw.r.appspot.com/

### **Architecture Diagram**

![Slide1](https://user-images.githubusercontent.com/103208143/172032753-2421dbfd-ecac-4a04-aba4-522c55bd4ce6.JPG)

### **Source Code**
The source code for this project was written using Google Shell Editor, JupyterLab, and stored in GitHub repo https://github.com/Akimon85/msds434-project. GitHub Actions was used to run tests using pytest and pylint automatically when new code is pushed to the repo. The contents of the repo is pushed to Google Cloud Platform (GCP) as a docker container for deployment. This setup allows developers to test various aspects the source code for formatting issues, package dependency issues, and other bugs quickly and automatically whenever there is a new commit. This increases efficiency significanty by eliminating the time consuming need to manually create a virtual test environment locally each time.

Github actions workflow config file:
```python
name: Python application test with Gtihub Actions
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python 3.9
      uses: actions/setup-python@v1
      with:
        python-version: 3.8
    - name: Install dependencies
      run: |
       make install
    - name: Lint with pylint
      run: |
        make lint
    - name: Test with pytest
      run: |
        make test
    - name: Format code
      run: |
        make format
```

Dockerfile - this file ensures the program can be sahred and built in a reproducible manner anywhere.
```docker

FROM python:3.9-slim

WORKDIR /app
COPY . main.py /app/

RUN pip install -r requirements.txt
EXPOSE 8080
ENTRYPOINT [ "python" ]
CMD [ "main.py" ]
```
The "Makefile" contains code needed to create virtual envirnment and install of the packages as specified in "requirements.txt".

```python
pylint==2.13.5
pytest==7.1.1
black==22.3.0
pyarrow
db-dtypes
Flask
gunicorn
google-cloud-bigquery
google-cloud-bigquery-storage
google-cloud-secret-manager
sklearn
dash==2.4.1
dash-bootstrap-components==1.1.0
names==0.3.0
pandas==1.4.2
numpy==1.22.4
plotly==5.8.0
Werkzeug==2.0.3
kaggle
```

### **Data**
The dataset used for the ML portion of this project was from Kaggle's Spaceship Titanic Competiton, in which you are tasked with predicting which passengers were transported to another dimension when "the unwary Spaceship Titanic collided with a spacetime anomaly hidden within a dust cloud". 

![image](https://user-images.githubusercontent.com/103208143/172069867-f82bcb8e-88cf-47e4-8b44-2eee4eacba90.png)

The python backend main.py script retrieves a Kaggle API token store in Google Secret Manager and supplies it to the Kaggle API for authentication (without having to expose sensitive data in the source code), then it downloads the dataset from Kaggle servers in the form of a zip file. The zip archive is unpacked and the training and test sets are loaded into python pandas dataframes. The data is then cleaned using pandas & scikit-learn module and then imported into Google BigQuery tables via google-bigquery API.

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
API calls are made to BigQuery where SQL code is used to create and train a ML logistic regression classification model. Additional API calls are made to BigQuery to make predictions on the test set, and retrieve model evaluation results and predictions. The predictions are formatted and saved as a csv file using python, then submitted to Kaggled for scoring via the kaggled API. Finally, the submission score is retrived from using the kaggled API.

```python
#model training
query_job = client.query("""
    CREATE OR REPLACE MODEL `msds343-project.ZenDesk.final_model`
        OPTIONS(model_type='logistic_reg',labels=['Transported']) AS
    SELECT * FROM `msds343-project.ZenDesk.final`
    """)
query_job.result()

training_info = """
SELECT
  training_run,
  iteration,
  loss,
  eval_loss,
  duration_ms,
  learning_rate
FROM
  ML.TRAINING_INFO(MODEL `msds343-project.ZenDesk.final_model`)
ORDER BY iteration ASC
"""
training = client.query(training_info).to_dataframe()

eval_model = """
    SELECT *
    FROM ML.EVALUATE(MODEL `msds343-project.ZenDesk.final_model`,
      (
      SELECT *
      FROM `msds343-project.ZenDesk.final`
      ))"""
temp = client.query(eval_model).to_dataframe()
eval_info = temp.copy()

pred = """
SELECT *
FROM ML.PREDICT(MODEL `msds343-project.ZenDesk.final_model`,
  (
  SELECT *
  FROM `msds343-project.ZenDesk.test`
    ))"""
temp = client.query(pred).to_dataframe()
predictions = temp.copy()

```
### **Dashboard Application Deployment**
An interactive dashboard using various visualizations and prediction results were generated using plotly dash, and can be deployed with local host or on the web via Google Cloud Build & App Engine. The dashboard allows the end user to explore the data provided and review BigQueryML model metrics, predictions, and prediction accuracy.

Separate GCP projects were created as development and production environments, linked to the main and production branches, respectively, of the GitHub source code repository. This setup alows any changes to the source code to be tested and validated in a fully deployed cloud environment without affecting the existing version of the app hosted in the production environment.

*Note - The app config file must specify that a "FG_1G" GCP compute instance class is used to deploy the app. Otherwise, the default instance clas will be automatically provisioned, which does not contain enough memory for the app to run properly will either errors during app deployment or cause silent errors in the background that will prevent the web app from loading properly in a browser.
```python
#app.yml - App Config File

runtime: python39
instance_class: F4_1G
entrypoint: gunicorn -b 0.0.0.0:8080 main:server

```
Plotly-Dash App
![image](https://user-images.githubusercontent.com/103208143/172066428-07868c67-d14b-4ba9-af5f-acfe3716a70b.png)

![image](https://user-images.githubusercontent.com/103208143/172066449-f53159cc-0dd5-4e50-9dc0-1c041744c99c.png)

![image](https://user-images.githubusercontent.com/103208143/172066466-de7e0955-24fd-4297-a630-f6c89f2fb1c2.png)

### **Monitoring**

Google Cloud Operation Suite (stackdriver) is used to monitor various performance and cost metrics of the GCP project. 
Additionally, it was used to setup app uptime checks that automatically alerts the app owner via email when the app is down.

![image](https://user-images.githubusercontent.com/103208143/172067533-cf5f6975-697b-48f7-b255-662c2b3f7fce.png)

