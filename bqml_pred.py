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

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/', methods=['POST'])
def uploadFiles():
    uploaded_file = request.files['file']
    if uploaded_file.filename !='':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(file_path)
    return redirect(url_for('index'))

def main():
    return "Akira Noda - MSDS434 Project - Customer Support Ticket Type Prediction"

def hello():

    df_html = dataframe.describe().to_html()
    resp = make_response(render_template_string(df_html))

    return resp

if __name__ == "__bqml_pred__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
