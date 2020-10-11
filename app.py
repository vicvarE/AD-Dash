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
    html.H1(children='Target AD',style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
    html.Div(children='''
        A batch screening tool to focus early clinical trials of Alzheimer's Disease. This tool predicts which mild cognitive impaired patients are most likely to develop Alzheimer's
    ''',style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'padding': 10}),
    html.P(['1) Download the template below to structure your data. The template contains dummy values for you to replace, test names should not be changed. If you are unfamiliar with the test name, use the Variable Lookup search.',  html.Br()], style = {'width': '80%',  'align-items': 'center', 'justify-content': 'center','margin': '20px','margin-left': '135px' ,'display': 'flex'}),
    html.A(
    'Download Template',
    id='download-link',
    download="template.csv",
    href=csv_string,
    target="_blank"
    , style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
    
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            '2) Upload your .csv or .xlm patient file: Drag and Drop or ',
            html.A('Select Files'),'. After dropping your file, a table and chart with results will be displayed'
        ]),
        style={
            'width': '80%',
            'align-items': 'center', 'justify-content': 'center',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '20px' ,
            'margin-left': '135px',
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
   
    
    html.Div([html.Div('''3) OPTIONAL. Select model threshold. Lower values will include more patients into the pool, but increases false negatives. Default value is optimized for tradeoff.'''),
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
        ],style={'marginBottom': 50,'marginTop': 50,'width': '80%', 'margin-left': '135px'}),
    
    html.Div([html.Div('''4) Select time from first visit in days. It will update the likelihood (ranging form 0-not very likely to 1-very likely) for a patient to be diagnosed with Alzheimer's by this timepoint.'''),
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
        ],style={'marginBottom': 50,'marginTop': 50, 'width': '80%', 'margin-left': '135px'}),
          
                       
       html.Div(id='output-data-upload',
     style = {'width': '100%', 'align-items': 'center', 'justify-content': 'center', 'margin-left': '205px'}),  
       
             
       html.Div([
        html.I(["Variable Lookup:",html.Br(), "Input the name of the variable you want more information about.A description and accepted values for this test will be displayed"]),
        html.Br(),
        dcc.Input(id="input1", type="text", placeholder="", debounce=True),

        html.Div(id="output", style = {'width': '100%', 'margin': '5px', 'margin-left': '185px'}),
    ] , style = {'width': '100%', 'align-items': 'center', 'justify-content': 'center','textAlign': 'center'}, className="one column"),
  

    
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
            #html.Hr()
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
        
        merged_ps=predictions.join(surv_df.set_index('Patient ID'), on='Patient ID')
        merged_ps.loc[merged_ps['Include'] =='No', 'Likely diagnosis'] = 'Not applicable'
        
        needed_tests=which_tests(tests_df)
        merged_table=pd.concat([merged_ps,needed_tests])
        merged_table=merged_table.fillna('All completed')
        
        figure=px.bar(merged_table[['Patient ID', 'Include' ]].groupby('Include').count(),color_discrete_sequence=px.colors.qualitative.Pastel2)
        figure.update_layout(showlegend=False)
        
        table = html.Div([html.P('Note: Patients hihlighted in green can be selected for the clinical trial. If Orange, the tests indicated need to be performed before a prediction can be given. The table can be sorted, filtered, modified and downloaded. The distribution is shown in the graph', style = {'width': '70%'}),
    
        html.Div([dash_table.DataTable(
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
                'filter_query': '{Include} = `Tests needed`',                
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
            'minWidth': 80,
            'textAlign': 'left'

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
           
            
        ], className="four columns"),
        

        html.Div([dcc.Graph(id='example-graph',
        figure=figure),
        ], className="five columns")
        
        ], style={ 'margin-bottom':'55px'})
        return table




if __name__ == '__main__':
    app.run_server(debug=True)