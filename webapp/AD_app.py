# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 11:25:47 2020

@author: viceva
"""
import base64
import datetime
import io
# import xlsxwriter
# from flask import send_file
# import flask 

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_table
from src.predict_model import feat_selection, predict_AD

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Dash-AD'),
    html.Div(children='''
        A screening tool for Alzheimer's Disease
    '''),
    
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
    html.Div(id='output-data-upload'),

])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    #transform user df with load features and fit model
    df_subset=feat_selection(df, 'models/01prelim_features.sav')
    predictions=predict_AD(df_subset, 'models/01prelim_model.sav')

    return html.Div([
        dcc.RadioItems(options=[
          {'label': 'Condensed Data Table', 'value': 'Condensed'},
          {'label': 'Complete Data Table', 'value': 'Complete'},
          ], value='Condensed',
          labelStyle={'display': 'inline-block', 'width': '20%', 'margin':'auto', 'marginTop': 15, 'paddingLeft': 15},
          id='radio-button-table',          

          ),
        html.Div([
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
            
        ),
        
        html.Hr(),  # horizontal line


        # Download Button
        html.Div([
            html.A(html.Button('Download Data', id='download-button'), id='download-link')
        ]),
        #graphs
        dcc.Graph(
            id='example-graph',
            figure=px.bar(predictions.groupby('Include').count(),color_discrete_sequence=px.colors.qualitative.Antique)
           
            )
        ]),
    ])


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
                State('upload-data', 'last_modified')])

def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None: 
        children = [
            parse_contents(list_of_contents, list_of_names, list_of_dates)]
        return children

# Callback for  download

# Callback and update data table columns
# @app.callback(Output('data-table', 'columns'),
#     [Input('radio-button-table', 'value')])
# def update_columns(value):
#     if value == 'Complete':
#     	column_set=[{"name": i, "id": i, 'deletable': True} for i in columns_complete] + [{"name": j, "id": j, 'hidden': 'True'} for j in conditional_columns]
#     elif value == 'Condensed':
#         column_set=[{"name": i, "id": i, "deletable": True} for i in columns_condensed]
#     return column_set

if __name__ == '__main__':
    app.run_server(debug=True)