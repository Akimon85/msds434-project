#Module5
import os
import pandas
import pyarrow
from flask import Flask, request, jsonify
from google.cloud import bigquery

app = Flask(__name__)
app.route('/')


client = bigquery.Client()

table = bigquery.TableReference.from_string(
    "msds343-project.ZenDesk.model_eval"
)
rows = client.list_rows(
    table,
  )

dataframe = rows.to_dataframe()

def hello():

    print(dataframe)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
