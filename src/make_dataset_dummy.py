# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 11:02:26 2020
Make dummy test dataset
@author: viceva
"""
import pandas as pd
import numpy as np
from predict_model import feat_selection


def do_shuffle(df):
    df_copy=df.copy()
    df_copy.drop(['NACCID'], axis=1, inplace=True)
    df_copy=df_copy.replace(regex='([a-zA-Z])', value=0)
    result = df_copy.copy().values
    np.random.shuffle(result.flat)
    result=pd.DataFrame(data=result, columns=df_copy.columns.tolist()) 
    result=result.fillna(1)
    result= result.apply(pd.to_numeric,errors='coerce')
    result_NaN = result.mask(np.random.random(result.shape)<0.005)

    return result_NaN


def main(inputfilepath, output_filepath, size=100, selection=None, selection_path=None):
    """ Runs data processing scripts to turn subset of interim (subset, unprocessed) data from (../interim) into
        dummy data to test (saved in ../processed).
    """
    df=pd.read_csv(inputfilepath)
    if (df.loc[:, df.columns.str.startswith('Unnamed')]).shape[1]!=0:
        df = df.loc[:, ~df.columns.str.startswith('Unnamed')]       


    df_dummy=df.sample(n = size)
    df_dummy=do_shuffle(df_dummy)
    df_dummy.reset_index(inplace=True, drop=True)
    df_dummy['NACCID']=df_dummy.index
    df_dummy.to_csv(output_filepath,index=False)
    
    if (selection != None) & (selection_path != None):
        df_dummy_subset=feat_selection(df_dummy, selection)
        new_col=df_dummy['NACCID']
        df_dummy_subset.insert(loc=0, column='NACCID', value=new_col)
        df_dummy_subset.to_csv(selection_path,index=False)


if __name__ == '__main__':
    main('../data/interim/AD_MCI.csv','../data/interim/dummy_test.csv',100, '../models/01final_features_broad.sav','../data/raw/dummy.csv')