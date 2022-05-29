#Module5
import os
from os.path import join, dirname, realpath
import pandas
from flask import Flask, request, jsonify, make_response, render_template_string, render_template, url_for, redirect
from google.cloud import bigquery

client = bigquery.Client()
table = bigquery.TableReference.from_string(
    "msds343-project.ZenDesk.model_eval"
)
rows = client.list_rows(
    table,
  )
dataframe = rows.to_dataframe()

temp_table = bigquery.TableReference.from_string(
    "msds343-project.ZenDesk.temp"
)

job_config = bigquery.LoadJobConfig()
job_config.source_format = bigquery.SourceFormat.CSV
job_config.autodetect = True

app = Flask(__name__)
UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/', methods=['POST'])
def uploadFiles():
    uploaded_file = request.files['file']
    if uploaded_file.filename !='':
        #file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        #uploaded_file.save(uploaded_file.filename)
        with open(uploaded_file, "rb") as source_file:
            job = client.load_table_from_file(source_file, temp_table, job_config=job_config)
        job.result()
        print("Loaded {} rows into {}:{}.")

    return redirect(url_for('index'))

def main():
    return "Akira Noda - MSDS434 Project - Customer Support Ticket Type Prediction"

def hello():

    df_html = dataframe.describe().to_html()
    resp = make_response(render_template_string(df_html))

    return resp

if __name__ == "__bqml_pred__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
