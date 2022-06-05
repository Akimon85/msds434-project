import pandas as pd
import numpy as np
import os
import dash
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State

import dash_bootstrap_components as dbc
#import kaggle
import plotly.express as px

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from google.cloud import secretmanager
from sklearn.impute import SimpleImputer
#from sklearn.preprocessing import LabelEncoder
#from kaggle.api.kaggle_api_extended import KaggleApi
#print('\n'.join(f'{m.__name__}=={m.__version__}' for m in globals().values() if getattr(m, '__version__', None)))

from google.oauth2 import service_account
from google.cloud import bigquery
#key_path = "msds343-project-03476f47763b.json"
#credentials = service_account.Credentials.from_service_account_file(
#    key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],)
######get kaggle api token from GCP
#secrets = secretmanager.SecretManagerServiceClient(credentials=credentials)
#secrets = secretmanager.SecretManagerServiceClient()
#KAGGLE_TOKE = secrets.access_secret_version(request={"name":"projects/msds343-project/secrets/kaggle/versions/1"}).payload.data.decode("utf-8")
#json_object = json.loads(KAGGLE_TOKE)
#%env KAGGLE_USERNAME=json_object["username"]
#%env KAGGLE_KEY=json_object["key"]
#os.makedirs("~/.kaggle/")
#file = open('~/.kaggle/kaggle.json',"w")
#file.write(KAGGLE_TOKE)
#file.close()

#download data
#api = KaggleApi()
#api.authenticate()
#api.competition_download_files('spaceship-titanic', path='./')
#!kaggle competitions download -c 'spaceship-titanic'
#import shutil
#shutil.unpack_archive('spaceship-titanic.zip', '.')
data = pd.read_csv('train.csv')
#test = pd.read_csv('test.csv')


#preprocess data
imputer_cols = ["Age", "FoodCourt", "ShoppingMall", "Spa", "VRDeck" ,"RoomService"]
imputer = SimpleImputer(strategy='mean')
imputer.fit(data[imputer_cols])
data[imputer_cols] = imputer.transform(data[imputer_cols])
data["HomePlanet"].fillna('Z', inplace=True)
data[['Deck','Num','Side']] = data['Cabin'].str.split('/', expand=True)
data['cabin_p'] = data.loc[~data['Cabin'].isnull()].groupby('Cabin').cumcount() + 1
data['Total_Spending'] = data[['RoomService', 'FoodCourt', 'ShoppingMall', 'Spa', 'VRDeck']].sum(axis=1)
data['Spent_Money'] = np.where(data['Total_Spending']>0, True, False)

'''
test[imputer_cols] = imputer.transform(test[imputer_cols])
test["HomePlanet"].fillna('Z', inplace=True)
test[['Deck','Num','Side']] = test['Cabin'].str.split('/', expand=True)
test['cabin_p'] = test.loc[~test['Cabin'].isnull()].groupby('Cabin').cumcount() + 1
test['Total_Spending'] = test[['RoomService', 'FoodCourt', 'ShoppingMall', 'Spa', 'VRDeck']].sum(axis=1)
test['Spent_Money'] = np.where(test['Total_Spending']>0, True, False)
'''
features = ['CryoSleep','HomePlanet', 'VIP', 'Destination','Spent_Money']
opts = [{'label':i, 'value':i} for i in features]


#save data to BigQuery and Run ML
client = bigquery.Client(project="msds343-project")
'''
table_ref = client.dataset("ZenDesk").table("final")
table_ref2 = client.dataset("ZenDesk").table("test")

job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
#job_config.source_format = bigquery.SourceFormat.CSV
#job_config.skip_leading_rows = 1 # ignore the header
job_config.autodetect = True
client.load_table_from_dataframe(data, table_ref, job_config).result()
client.load_table_from_dataframe(test, table_ref2, job_config).result()

#%load_ext google.cloud.bigquery

query_job = client.query("""
    CREATE OR REPLACE MODEL `msds343-project.ZenDesk.final_model`
        OPTIONS(model_type='logistic_reg',labels=['Transported']) AS
    SELECT * FROM `msds343-project.ZenDesk.final`
    """)
query_job.result()


training_info = """
SELECT
  training_run,
  iteration,
  loss,
  eval_loss,
  duration_ms,
  learning_rate
FROM
  ML.TRAINING_INFO(MODEL `msds343-project.ZenDesk.final_model`)
ORDER BY iteration ASC
"""
training = client.query(training_info).to_dataframe()
'''
eval_model = """
    SELECT *
    FROM ML.EVALUATE(MODEL `msds343-project.ZenDesk.final_model`,
      (
      SELECT *
      FROM `msds343-project.ZenDesk.final`
      ))"""
temp = client.query(eval_model).to_dataframe()
eval_info = temp.copy()

pred = """
SELECT *
FROM ML.PREDICT(MODEL `msds343-project.ZenDesk.final_model`,
  (
  SELECT *
  FROM `msds343-project.ZenDesk.test`
    ))"""
temp = client.query(pred).to_dataframe()
predictions = temp.copy()
lst = [temp]
del temp
del lst


score = [d[0].get('prob') for d in predictions.predicted_Transported_probs]

#pred = predictions[['PassengerId','predicted_Transported']].rename(
#    columns={'predicted_Transported':'Transported'})
#pred.to_csv('submission.csv',index=False)
pred_df=pd.DataFrame()
pred_df['predicted_Transported'] = predictions['predicted_Transported']
pred_df['probability_Transported'] = score

#submit predictions to kaggle
#get_ipython().system('kaggle competitions submit -c spaceship-titanic -f submission.csv -m Sub1')
#sub_score = get_ipython().system('kaggle competitions submissions -c spaceship-titanic')
#sub_score = sub_score[2][60:67]
kaggle_score = "Kaggle Submission Score = 0.73322"

#Setup dash app
app = dash.Dash(__name__)
server = app.server

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

#Histogram of Age Distribution
fig = px.histogram(data_frame = data, 
                   x="Age",
                   color="Transported",
                   marginal="box",
                   nbins= 100,
                   width=1000, height=250,
                )
fig.update_layout(
    title = "Distribution of Passenger Age",
    title_x = 0.5,
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

#3D Scatter Plot Of Passenger Location
'''
data['side_x'] = data['Side'].map({"P":"-1","S":"1"})
data_small = data.loc[~data['Cabin'].isnull()]
data_small['side_xx'] = np.log10(data_small['Num'].astype(int))*data_small['side_x'].astype(int)
fig2 = px.scatter_3d(data_small, x="side_xx", y="Num", z="Deck", size="cabin_p", 
                     color="Transported", hover_data=['Name','Cabin'],
                     category_orders={"Deck":['G','F','E','D','C','B','A','T']},
                     labels={"Num":"Cabin Number","side_xx":"<- Port Side             Starboard Side ->"},
                     range_x = [-4.5,4.5],title="Passenger Location On Ship",
                     width=1000, height=666, size_max=20,
                    )
'''
data['side_x'] = data['Side'].map({"P":"-1","S":"1"})
data = data.loc[~data['Cabin'].isnull()]
data['side_xx'] = np.log10(data['Num'].astype(int))*data['side_x'].astype(int)
fig2 = px.scatter_3d(data, x="side_xx", y="Num", z="Deck", size="cabin_p", 
                     color="Transported", hover_data=['Name','Cabin'],
                     category_orders={"Deck":['G','F','E','D','C','B','A','T']},
                     labels={"Num":"Cabin Number","side_xx":"<- Port Side             Starboard Side ->"},
                     range_x = [-4.5,4.5],title="Passenger Location On Ship",
                     width=1000, height=500, size_max=20,
                    )
fig2.update_layout(
    title_x = 0.5,
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text'],
    scene = dict(
        xaxis = dict(
             backgroundcolor="rgba(0, 0, 0,0)",
             gridcolor="white",
             showbackground=True,
             zerolinecolor="white",),
        yaxis = dict(
            backgroundcolor="rgba(0, 0, 0,0)",
            gridcolor="white",
            showbackground=True,
            zerolinecolor="white"),
        zaxis = dict(
            backgroundcolor="rgba(0, 0, 0,0)",
            gridcolor="white",
            showbackground=True,
            zerolinecolor="white",),),
)

fig4 = px.histogram(data_frame = pred_df, 
                   x="probability_Transported",
                   color="predicted_Transported",
                   marginal="box",
                   nbins= 100,
                   width=1000, height=300,
                )
fig4.update_layout(
    title = "Predictions & Prediction Probabilities",
    title_x = 0.5,
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']



'''
dff = data.copy()
df_trans = dff[dff['Transported']==1][['CryoSleep','Transported']]
df_not = dff[dff['Transported']==0][['CryoSleep', 'Transported']].rename(columns={'Transported':'Not Transported'})
df_trans = df_trans.CryoSleep.value_counts()
df_trans = pd.DataFrame(df_trans).reset_index().rename(columns={'index':'Transported'})
df_not = df_not.CryoSleep.value_counts()
df_not = pd.DataFrame(df_not).reset_index().rename(columns={'index':'Not Transported'})
df_not['CryoSleep_final'] = df_not['CryoSleep']
df_not['CryoSleep'] *= -1
counts = df_not['CryoSleep_final'].tolist() + df_trans['CryoSleep'].tolist()
end = max(counts)


fig3 = make_subplots(rows=1, cols=2, specs=[[{}, {}]], shared_yaxes=True, horizontal_spacing=0)
fig3.append_trace(go.Bar(x=df_not["CryoSleep"], y=df_not["Not Transported"], orientation='h', showlegend=True, text= df_not['CryoSleep_final'], name='Not Transported'),1,1)
fig3.append_trace(go.Bar(x=df_trans["CryoSleep"], y=df_trans["Transported"], orientation='h', showlegend=True, text= df_trans['CryoSleep'], name='Transported'),1,2)
fig3.update_xaxes(showgrid=False, range=[end*-1,0],row=1,col=1)
fig3.update_xaxes(showgrid=False, range=[0,end],row=1,col=2)
fig3.update_yaxes(showgrid=False, categoryorder='total ascending', 
                 ticksuffix=' ', showline=False)
fig3.update_traces(hovertemplate=None)
fig3.update_layout(
    title = "Number of Passengers Transported To Another Dimension",
    title_x = 0.5,
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text'],
    hovermode="y unified", 
    xaxis_title=" ", yaxis_title="CryoSleep ",
    legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="center", x=0.5),
    width=1000, height=360,
)
'''
fig3 = []
app.layout = html.Div(
            children=[
                html.H1(children="Titantic Spaceship"),
                html.P(children="Akira Noda - MSDS434 Project - Interdimensional Transportation Prediction"),
                html.P([
                    html.Label("Choose a feature"),
                    dcc.Dropdown(id = 'opt',
                                 options = opts,
                                 value = opts[0])
                    ], style = {'width': '400px',
                                'fontSize' : '20px',
                                'padding-left' : '50px',
                                'display': 'inline-block'}),
                dcc.Graph(id='bar',figure=fig3),
                html.Div([
                    dcc.Graph(id="histogram", figure=fig),
                    html.Br(),
                    dcc.Graph(id="3dplot", figure=fig2)
                ]),
                html.P(children=[html.H3("BigQueryML - Logistic Regression Classification Model Evaluation")]),
                dash_table.DataTable(eval_info.to_dict('records'), [{"name": i, "id": i} for i in eval_info.columns]),
                dcc.Graph(id='pred_host',figure=fig4),
                html.P(children=[html.H3(kaggle_score)])
            ])
   
@app.callback(
    Output('bar', 'figure'), 
    [Input('opt', 'value')]
     )
def update_figure(X):
                
        dff = data.copy()
        df_trans = dff[dff['Transported']==1][[X,'Transported']]
        df_not = dff[dff['Transported']==0][[X, 'Transported']].rename(columns={'Transported':'Not Transported'})
        df_trans = df_trans[X].value_counts()
        df_trans = pd.DataFrame(df_trans).reset_index().rename(columns={'index':'Transported'})
        df_not = df_not[X].value_counts()
        df_not = pd.DataFrame(df_not).reset_index().rename(columns={'index':'Not Transported'})
        df_not['x_final'] = df_not[X]
        df_not[X] *= -1
        counts = df_not['x_final'].tolist() + df_trans[X].tolist()
        end = max(counts)
        fig3a = make_subplots(rows=1, cols=2, specs=[[{}, {}]], shared_yaxes=True, horizontal_spacing=0)
        fig3a.append_trace(go.Bar(x=df_not[X], y=df_not["Not Transported"], orientation='h', showlegend=True, text= df_not['x_final'], name='Not Transported'),1,1)
        fig3a.append_trace(go.Bar(x=df_trans[X], y=df_trans["Transported"], orientation='h', showlegend=True, text= df_trans[X], name='Transported'),1,2)
        fig3a.update_xaxes(showgrid=False, range=[end*-1,0],row=1,col=1)
        fig3a.update_xaxes(showgrid=False, range=[0,end],row=1,col=2)
        fig3a.update_yaxes(showgrid=False, categoryorder='total ascending', 
                         ticksuffix=' ', showline=False)
        fig3a.update_traces(hovertemplate=None)
        fig3a.update_layout(
            title = "Number of Passengers Transported To Another Dimension",
            title_x = 0.5,
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text'],
            hovermode="y unified", 
            xaxis_title=" ", yaxis_title=X,
            legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="center", x=0.5),
            width=1000, height=300)
        fig = go.Figure(data=fig3a)
        return fig


#if __name__ == '__main__':
#    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
    
if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8080)
#    app.run_server(debug=False)      
