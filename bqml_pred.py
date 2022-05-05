#Module5
import os
import pandas as pd
from flask import Flask, request, jsonify
from google.cloud import bigquery

app = Flask(__name__)
app.route('/')


client = bigquery.Client()

query_string = """
SELECT * 
FROM `msds343-project.ZenDesk.model_eval`
"""

dataframe = (
    client.query(query_string)
    .result()
    .to_dataframe(
        create_bqstorage_client=True,
    )
)

def hello():

    print(dataframe)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
