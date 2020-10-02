# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 12:38:10 2020

@author: viceva
"""
import pickle
import pandas as pd
import numpy as np


def feat_selection(df, features):   
    '''Returns a trimmed df with only the features needed for the model to work.'''
    loaded_features = pickle.load(open(features, 'rb'))
    df_subset=df[loaded_features.to_list()]
    return df_subset

def feature_check(df_subset):
    '''Returns dataframes tests_df with which patients need further testing and model_df for further prediction.'''
    tests_df=df_subset[df_subset.isnull().any(axis=1)]
    model_df=df_subset.dropna()
    return tests_df, model_df

def predict_AD(model_df, model_path, threshold = .5):
    '''Returns model predictions'''
    load_model = pickle.load(open(model_path, 'rb'))
    #predictions = load_model.predict(model_df)     
    predicted_proba = load_model.predict_proba(model_df)
    predictions = (predicted_proba [:,1] >= threshold).astype('int')
    predictions_df=pd.DataFrame({'Patient_ID': model_df.index, 'Include': predictions})
    predictions_df.Include.replace((1, 0),('Yes', 'No'), inplace=True)
    return predictions_df

def which_tests(tests_df):
    '''Returns df with tests needed'''
    needed_tests=pd.DataFrame(index=tests_df.index)
    needed_tests['Patient_ID']=tests_df.index
    needed_tests['Include']= 'tests_needed'
    needed_tests['Likely diagnosis']= 'NaN'
    needed_tests['tests_needed'] = tests_df.isna().dot(tests_df.columns+',').str.rstrip(',') 

    return needed_tests

def predict_survival(model_df, model_path, threshold=365):
    '''Returns model predictions'''
    load_model = pickle.load(open(model_path, 'rb'))
    predicted_proba = load_model.predict_cumulative_hazard_function(model_df, return_array=True)
    times=load_model.event_times_ 
    time_idx=(np.abs(times - threshold)).argmin()
    predictions = predicted_proba[:,time_idx]
    predictions=predictions.round(2)
    surv_df=pd.DataFrame({'Patient_ID': model_df.index, 'Likely diagnosis': predictions})
    return surv_df

#testing snippets
# df=pd.read_csv('../data/interim/dummy_test.csv')
# df_subset=feat_selection(df, '../models/01final_features_res.sav')
# tests_df, model_df=feature_check(df_subset)
# predictions=predict_AD(model_df, '../models/rf_grid_search_sub.sav')
# surv_df=predict_survival(model_df, '../models/surv_model.sav')
# merged_ps=predictions.join(surv_df.set_index('Patient_ID'), on='Patient_ID')
# merged_ps.loc[merged_ps['Include'] =='No', 'Time to diagnosis'] = 'NaN'
        
# needed_tests=which_tests(tests_df)
# a=pd.concat([predictions,needed_tests])
# a=a.fillna('All completed')
