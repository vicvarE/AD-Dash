# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 11:25:47 2020

@author: viceva
"""
import base64
import datetime
import io
import os
from urllib.parse import quote

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
import pandas as pd
from src.predict_model import feat_selection, predict_AD, feature_check

dff = pd.read_csv('data/raw/dummy.csv')
csv_string = dff.to_csv(encoding='utf-8', index=False)
csv_string = "data:text/csv;charset=utf-8," + quote(csv_string)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True, prevent_initial_callbacks=True)

server = app.server

app.layout = html.Div(children=[
    html.H1(children='Dash-AD'),
    html.Div(children='''
        A screening tool for Alzheimer's Disease
    '''),
    html.P(['Upload your .csv or .xlm below.', html.Br(), 
            'Use the following template (contains dummy values):']),
    html.A(
    'Download Template',
    id='download-link',
    download="template.csv",
    href=csv_string,
    target="_blank"
    ),
    
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
    
    html.Div([html.Div('''Select model threshold. Lower values will include more patients into the pool, but increases false negatives. Default value is optimized for tradeoff.'''),
    dcc.Slider(
        id='Model precision',
        min=0.25,
        max=.75,
        step=.001,
        value=.5,
           marks={
        .25: '.25',
        .35: '.35',
        .45: '.45',
        .55: '.55',
        .65: '.65',
        .75: '.75',

        },
       tooltip = { 'always_visible': False, 'placement':'bottom' }
        ),
        html.Div(id='slider-output-container'),
        ]),
    html.Div(id='output-data-upload'),  
    dcc.Graph(id='example-graph'),
     # Hidden div inside the app that stores the intermediate value
    html.Div(id='intermediate-value', style={'display': 'none'}),
    
])
             
             

def parse_contents(contents, filename,date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'txt' or 'tsv' in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), delimiter = r'\s+')
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df   



@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])   

def update_table(contents, filename,date):
    table = html.Div()

    if contents:
        df = parse_contents(contents, filename, date)
            #transform user df with load features and fit model
        copy_df=df.copy()
        df_subset=feat_selection(copy_df, 'models/01final_features_res.sav')
        tests_df, model_df=feature_check(df_subset)
        predictions=predict_AD(model_df, 'models/rf_best.sav')
        
        table = html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=predictions.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in predictions.columns],
            editable=True,
            id='data-table',
            style_data_conditional=[
                {
            'if': {
                'filter_query': '{Include} = Yes',                
            },
            'backgroundColor': 'darkseagreen',            
            }],
            
            style_table={
            'height': 400,
            #'overflowY': 'scroll',
            'width': 400
            },
            style_cell={
            'whiteSpace': 'normal',
            'height': 'auto',
            },
            style_filter = {'height':'25px'},    
            filter_action="native",
            fixed_rows={'headers': True},
            sort_action="native",
            page_action='native',
            sort_mode="multi",
            export_columns='all',
            export_format='csv',
            export_headers ='names',
            
        ),
        
        html.Hr(),  # horizontal line
       
        ])

    return table

@app.callback(Output('intermediate-value', 'children'),               
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])

def clean_data(contents, filename,date):
     if contents:
         df = parse_contents(contents, filename, date)
         return df.to_json(orient='split')

@app.callback(Output('example-graph', 'figure'),  
              [Input('intermediate-value', 'children'),
               Input('Model precision', 'value')])
# def update_table(jsonified_cleaned_data):
def update_graph(jsonified_data, slider_value):
    dff = pd.read_json(jsonified_data, orient='split')
    df_subset=feat_selection(dff, 'models/01final_features_res.sav')
    tests_df, model_df=feature_check(df_subset)
    predictions=predict_AD(model_df, 'models/rf_best.sav', slider_value)
        
    figure=px.bar(predictions.groupby('Include').count(),color_discrete_sequence=px.colors.qualitative.Antique)

    return figure


# def update_table(jsonified_cleaned_data):
#     dff = pd.read_json(jsonified_cleaned_data, orient='split')
#     table = create_table(dff)
#     return table


if __name__ == '__main__':
    app.run_server(debug=True)