import pandas as pd
from sklearn import datasets
from google.cloud import bigquery
import os
from flask import Flask, request, jsonify
import dash
from dash import Dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

# load a toy dataset
data = datasets.load_boston()
boston_df = pd.DataFrame(data["data"], columns=data["feature_names"])
boston_target = pd.DataFrame(data["target"])

# save as CSV
boston_df.to_csv("boston.csv", index=False)
boston_target.to_csv("target.csv", index=False)

client = bigquery.Client(project="msds343-project")
table_ref = client.dataset("ZenDesk").table("boston")
job_config = bigquery.LoadJobConfig()
job_config.source_format = bigquery.SourceFormat.CSV
job_config.skip_leading_rows = 1 # ignore the header
job_config.autodetect = True

theme = dbc.themes.LUX
css = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'
app = dash.Dash(__name__, external_stylesheets=[theme, css])

########################## Navbar ##########################
# Input
# Output
navbar = dbc.Nav(className="nav nav-pills", children=[
    ## logo/home
    dbc.NavItem(html.Img(src=app.get_asset_url("logo.PNG"), height="40px")),
    ## about
    dbc.NavItem(html.Div([
        dbc.NavLink("About", href="/", id="about-popover", active=False),
        dbc.Popover(id="about", is_open=False, target="about-popover", children=[
            dbc.PopoverHeader("How it works"), dbc.PopoverBody(config.about)
        ])
    ])),
    ## links
    dbc.DropdownMenu(label="Links", nav=True, children=[
        dbc.DropdownMenuItem([html.I(className="fa fa-linkedin"), "  Contacts"], href=config.contacts, target="_blank"), 
        dbc.DropdownMenuItem([html.I(className="fa fa-github"), "  Code"], href=config.code, target="_blank")
    ])
])

# Callbacks
@app.callback(output=[Output(component_id="about", component_property="is_open"), 
                      Output(component_id="about-popover", component_property="active")], 
              inputs=[Input(component_id="about-popover", component_property="n_clicks")], 
              state=[State("about","is_open"), State("about-popover","active")])
def about_popover(n, is_open, active):
    if n:
        return not is_open, active
    return is_open, active
def function():
    return 0
########################## Body ##########################
# Input
inputs = dbc.FormGroup([
    html.Div(id='hide-seek', children=[
        dbc.Label("Riverfront Property", html_for="CHAS"), 
        dcc.Slider(id="CHAS", min=0, max=1, step=1, value=0, 
                   tooltip={'always_visible':False}),
        dbc.Label("Average Number of Rooms Per Dwelling", html_for="RM"), 
        dcc.Slider(id="RM", min=1, max=10, step=1, value=5, 
                   tooltip={'always_visible':False})
    ], style={'display':'block'})
])
# Output
body = dbc.Row([
        ## input
        dbc.Col(md=3, children=[
            inputs
        ]),
        ## output
        dbc.Col(md=9, children=[

        ])
])
# Callbacks
@app.callback()
def function():
    return 0
########################## App Layout ##########################
app.layout = dbc.Container(fluid=True, children=[
    html.H1("name", id="nav-pills"),
    navbar,
    html.P(
        children="Akira Noda - MSDS434 Project"
        "Predict Boston Housing Prices"
    ),
    dcc.Graph(
            figure={
                "data": [
                    {
                        "x": data["Date"],
                        "y": data["AveragePrice"],
                        "type": "lines",
                    },
                ],
                "layout": {"title": "Average Price of Avocados"},
            },
        ),
    html.Br(),html.Br(),html.Br(),
    body
])
########################## Run ##########################

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))


