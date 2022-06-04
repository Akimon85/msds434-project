import os
from os.path import join, dirname, realpath
import pandas
from flask import Flask, request, jsonify, make_response, render_template_string, render_template, url_for, redirect
from google.cloud import bigquery
from werkzeug.utils import secure_filename

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
path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'uploads')
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def upload():
    return render_template('upload.html')

@app.route('/', methods=['POST'])
def uploadFiles():
    uploaded_file = request.files['file']
    if uploaded_file.filename !='':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(file_path)
        test_df = pd.read_csv(file_path)
        df_html = test_df.describe().to_html()
        resp = make_response(render_template_string(df_html))
        with open(file_path, "rb") as source_file:
            job = client.load_table_from_file(source_file, temp_table, job_config=job_config)
        job.result()

    #return redirect(url_for('index'))
    return resp



#def hello():

#    df_html = dataframe.describe().to_html()
#    resp = make_response(render_template_string(df_html))

#    return resp

if __name__ == "__bqml_pred__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
