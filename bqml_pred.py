#Module5
import os
import pandas
from flask import Flask, request, jsonify
from google.cloud import bigquery

client = bigquery.Client()
table = bigquery.TableReference.from_string(
    "msds343-project.ZenDesk.model_eval"
)
rows = client.list_rows(
    table,
  )
dataframe = rows.to_dataframe()

app = Flask(__name__)
@app.route('/')

def hello():

    dt_html = dataframe.describe().to_html()
    resp = make_response(render_template_string(df_html))

    return resp

if __name__ == "__bqml_pred__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
