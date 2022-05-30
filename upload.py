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