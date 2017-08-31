# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 22:59:05 2017

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

#%%
# fetching data from Google Finance.

# import pandas_datareader as data
#tickers = stocks
#data_soruce='google'
#
#start_date = '2015-01-01'
#end_date = '2016-12-31'
#
#panel_data = data.DataReader(tickers, data_source=data_soruce, start=start_date,
#                             end=end_date)
#close_prices = panel_data.loc['Close']
#num_nulls = close_prices.isnull().sum(axis=0)
#min_nulls = num_nulls.min()
#cols = (num_nulls == min_nulls)
#
#close_prices_cleaned = close_prices.loc[:, cols]
#close_prices_new = close_prices_cleaned.dropna(axis=0)
#close_prices_new.to_csv('./spx_cleaned.csv')

#%%

import pandas as pd
close_prices = pd.read_csv('./spx_cleaned.csv', index_col=0, parse_dates=[0])
stock_returns = close_prices.pct_change()[1:]

interval_vol = stock_returns.rolling(window=252).std().dropna(axis=0).resample('M').mean()
vol_ranks = interval_vol.rank(axis=1)
num_stocks = vol_ranks.shape[1]
cutoff_rank = int(num_stocks / 10)

stocks_dict = {}
tot_returns = list(range(interval_vol.shape[0] - 1))

for i, idx in enumerate(interval_vol.index[:-1]):
    data_idx = vol_ranks.iloc[i]
    stocks_idx = data_idx[data_idx <= cutoff_rank]
    stocks_dict[i] = stocks_idx.index.tolist()
    start_dt, end_dt = interval_vol.index[i], interval_vol.index[i+1]
    
    period_returns = stock_returns.loc[start_dt:end_dt, stocks_dict[i]]
    period_mean = period_returns.mean(axis=1)
    tot_returns[i] = (period_mean + 1).prod() - 1
