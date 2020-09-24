# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 12:38:10 2020

@author: viceva
"""
import pickle
import pandas as pd

def feat_selection(df, features):   
    '''Returns a trimmed df with only the features needed for the model to work.'''
    loaded_features = pickle.load(open(features, 'rb'))
    df_subset=df[loaded_features.to_list()]
    return df_subset

def feature_check(df_subset, features):
    '''Returns dataframes tests_df with which patients need further testing and model_df for further prediction.'''
    tests_df=0
    model_df=0
    return tests_df, model_df

def predict_AD(model_df, model_path):
    '''Returns model predictions'''
    load_model = pickle.load(open(model_path, 'rb'))
    predictions = load_model.predict(model_df)
    predictions_df=pd.DataFrame({'Patient_ID': model_df.index, 'Include': predictions})
    predictions_df.Include.replace((1, 0),('Yes', 'No'), inplace=True)
    return predictions_df




