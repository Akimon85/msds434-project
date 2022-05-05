#Module3

import os

from flask import Flask, request, jsonify
from google.cloud import bigquery

client = bigquery.Client()

query_job = client.query(
    """
    SELECT * 
    FROM `msds343-project.ZenDesk.model_eval`
    """
)
eval_results = query_job.result()

app = Flask(__name__)

@app.route('/')
def hello():

    return jsonify(eval_results)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
