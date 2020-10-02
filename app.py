# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 11:25:47 2020

@author: viceva
"""
import base64
import io
from urllib.parse import quote

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
import pandas as pd
from src.predict_model import feat_selection, predict_AD, feature_check, which_tests,predict_survival

dff = pd.read_csv('data/raw/dummy.csv')
csv_string = dff.to_csv(encoding='utf-8', index=False)
csv_string = "data:text/csv;charset=utf-8," + quote(csv_string)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True, prevent_initial_callbacks=True)

server = app.server

app.layout = html.Div(children=[
    html.H1(children='Target AD'),
    html.Div(children='''
        A screening tool to focus early clinical trials of Alzheimer's Disease. This tool predicts which mild cognitive impaired patients are most likely to develop Alzheimer's
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
    html.Div(
    [
        html.I("Variable coding search"),
        html.Br(),
        dcc.Input(id="input1", type="text", placeholder="", debounce=True),
        html.Div(id="output"),
    ]),
    
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
        ],style={'marginBottom': 50,'marginTop': 50}),
    
    html.Div([html.Div('''Select time to diagnosis (days). It will return the likelihood (0 to 1+) to be diagnosed with Alzheimer's at this timepoint'''),
    dcc.Slider(
        id='Time point',
        min=150,
        max=550,
        step=10,
        value=365,
           marks={
        150: '150',
        250: '250',
        350: '350',
        450: '450',
        550: '550',
        },
       tooltip = { 'always_visible': False, 'placement':'bottom' }
        ),
        
        html.Div(id='slider-output-container2'),
        ],style={'marginBottom': 50,'marginTop': 50}),
  
    html.Div(id='output-data-upload'),  
    
     # Hidden div inside the app that stores the intermediate value
    html.Div(id='intermediate-value', style={'display': 'none'}),
    
])
             
@app.callback(
    Output("output", "children"),
    [Input("input1", "value")],
)
def update_output(input1):
    if input1:
        dd= pd.read_csv('docs/rdd_datadictionary_uds.csv')
        answer=dd[['ShortDescriptor','AllowableCodes']].loc[dd.VariableName==input1]
        
        search_table = html.Div()
        search_table   = html.Div([
            dash_table.DataTable(
            data=answer.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in answer.columns],
            style_cell={
            'whiteSpace': 'normal',
            'height': 'auto',
            'maxWidth': 40,
            
            },
            style_table={
                'width': 800
                },
            ),
            html.Hr()
            ])
        return search_table         

def parse_contents(contents, filename, date):
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



@app.callback(Output('intermediate-value', 'children'),               
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])

def clean_data(contents, filename,date):
     if contents:
         df = parse_contents(contents, filename, date)
         return df.to_json(orient='split')


@app.callback(Output('output-data-upload', 'children'),
              [Input('intermediate-value', 'children'),
               Input('Model precision', 'value'),
               Input('Time point', 'value')])   

def update_table(jsonified_data, slider_value, time_value):
    
    if jsonified_data:
        table = html.Div()
    
        dff = pd.read_json(jsonified_data, orient='split')
        df_subset=feat_selection(dff, 'models/01final_features_res.sav')
        tests_df, model_df=feature_check(df_subset)
        predictions=predict_AD(model_df, 'models/rf_best.sav', slider_value)
        surv_df=predict_survival(model_df, 'models/surv_model.sav', threshold=time_value)
        
        merged_ps=predictions.join(surv_df.set_index('Patient_ID'), on='Patient_ID')
        merged_ps.loc[merged_ps['Include'] =='No', 'Likely diagnosis'] = 'NaN'
        
        needed_tests=which_tests(tests_df)
        merged_table=pd.concat([merged_ps,needed_tests])
        merged_table=merged_table.fillna('All completed')
        
        table = html.Div([
    
        dash_table.DataTable(
            data=merged_table.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in merged_table.columns],
            editable=True,
            id='data-table',
            style_data_conditional=[
                {
            'if': {
                'filter_query': '{Include} = Yes',                
            },
            'backgroundColor': 'rgb(179,226,205)',            
            },
            {
            'if': {
                'filter_query': '{Include} = tests_needed',                
            },
            'backgroundColor': 'rgb(253,205,172)',            
            }],
            
            style_table={
            'height': 400,
            #'overflowY': 'scroll',
            'width': 400
            },
            style_cell={
            'whiteSpace': 'normal',
            'height': 'auto',
            'minWidth': 70

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
        dcc.Graph(id='example-graph',
        figure=px.bar(merged_table[['Patient_ID', 'Include' ]].groupby('Include').count(),color_discrete_sequence=px.colors.qualitative.Pastel2))
        ])

        return table




if __name__ == '__main__':
    app.run_server(debug=True)