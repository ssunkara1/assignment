# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 19:45:30 2017

@author: srinivas
"""

## get spx stocks from list.
file_handle = open('./spx_tickers.txt', 'r')

arr = file_handle.readlines()
file_handle.close()
stocks = []

for a in arr:
    a_clean = a.strip().replace("'", '')
    stocks = stocks + (a_clean.split(','))
    
stocks = [s.strip() for s in stocks]
###############################################################################     
#%%

import pandas_datareader as data
tickers = stocks
data_soruce='google'

start_date = '2010-01-01'
end_date = '2017-07-31'

panel_data = data.DataReader(tickers, data_source=data_soruce, start=start_date,
                             end=end_date)
close_prices = panel_data.loc['Close']
num_nulls = close_prices.isnull().sum(axis=0)
close_prices_cleaned = close_prices
close_prices_cleaned.to_csv('./spx_cleaned_total_all.csv')

###############################################################################
#%%
index = ['spy']
data_soruce='google'

start_date = '2010-06-28'
end_date = '2017-07-31'

index_data = data.DataReader(index, data_source=data_soruce, start=start_date,
                             end=end_date)
index_prices = index_data.loc['Close']
index_prices.to_csv('./index_total.csv')