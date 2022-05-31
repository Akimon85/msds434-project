import pandas as pd
import csv
df=pd.read_csv('/..local/example.csv')
df.to_gbq(full_table_id, project_id=project_id)

from google.cloud import bigquery
import pandas as pd
df=pd.read_csv('/..local/filename.csv')
client = bigquery.Client()
dataset_ref = client.dataset('my_dataset')
table_ref = dataset_ref.table('new_table')
client.load_table_from_dataframe(df, table_ref).result()



@app.route('/')
def hello():

    #with open("boston.csv", "rb") as source_file:
        job = client.load_table_from_file(
        source_file, table_ref, job_config=job_config
    )
    # job is async operation so we have to wait for it to finish
    job.result()
    with open("target.csv", "rb") as source_file:
        job = client.load_table_from_file(
        source_file, table_ref, job_config=job_config
    )
    job.result()






if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

