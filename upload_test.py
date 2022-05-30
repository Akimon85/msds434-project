import pandas as pd
from sklearn import datasets
from google.cloud import bigquery
import os
from flask import Flask, request, jsonify


# load a toy dataset
data = datasets.load_boston()
boston_df = pd.DataFrame(data["data"], columns=data["feature_names"])

# save as CSV
boston_df.to_csv("boston.csv", index=False)

client = bigquery.Client(project="msds343-project")

table_ref = client.dataset("ZenDesk").table("boston")

job_config = bigquery.LoadJobConfig()
job_config.source_format = bigquery.SourceFormat.CSV
job_config.skip_leading_rows = 1 # ignore the header
job_config.autodetect = True

from google.cloud import bigquery

import os

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def hello():

    with open("boston.csv", "rb") as source_file:
        job = client.load_table_from_file(
        source_file, table_ref, job_config=job_config
    )

    # job is async operation so we have to wait for it to finish
    job.result()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))


