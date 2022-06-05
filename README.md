# Northwestern MSDS434 - Akira Noda
# Analytics Application Engineering- Term Project - June 2022

This project was created to demonstrate proficiency with creating and deploying machine learning applications in the cloud.


The application does the following:

1.Retrieve a Kaggle competition dataset via kaggle api.*

2.Clean and preprocess datasets in python and import datasets to google BigQuery tables via google-bigquery api.

4.Trains and evaluate a logistic regression classification model using Google BigQuery ML and make predications.

5.Retrieve model evaluation metrics and predictions from google BigQuery.

6.Retrieve kaggle API key from GCP Secrets API.*

7.Submit predictions to kaggle competition and retrieve submission score via kaggle api.*

8.Generate an interactive dashboard application using plotly.dash and deploy to the web via Google App Engine.

The app is currently deployed at https://msds343-project.uw.r.appspot.com/

### **Architecture Diagram**

![Slide1](https://user-images.githubusercontent.com/103208143/172032753-2421dbfd-ecac-4a04-aba4-522c55bd4ce6.JPG)

## Source Code & CI/CD
The source code for this project was written using Google Shell Editor, JupyterLab, and stored in GitHub repo https://github.com/Akimon85/msds434-project. GitHub Actions was used to run tests automatically at commits. 




