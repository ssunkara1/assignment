# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 22:59:05 2017

@author: srinivas
"""
import pandas as pd
import numpy as np

df_all = pd.read_csv('./spx_cleaned_total_all.csv', index_col=0, parse_dates=[0])
num_secs_null = df_all.isnull().sum(axis=1)
nan_dates = num_secs_null.index[num_secs_null == df_all.shape[1] - 1]
df_cleaned = df_all.drop(nan_dates, axis=0)

###############################################################################
#%%
index_data = pd.read_csv('./index_total.csv', index_col=0, parse_dates=[0])
index_agg = index_data.resample('M').last()
index_returns = index_agg.pct_change()[1:]

index_mean = index_returns.mean() * 12
index_std = index_returns.std() * np.sqrt(12)

###############################################################################
#%%

close_prices = df_cleaned.copy()
stock_returns = close_prices.pct_change()[1:]

## mean vol over the last 6 months; calculated for each month
interval_vol = stock_returns.rolling(window=126).std().resample('M').mean()
null_idxs = interval_vol.index[interval_vol.min(axis=1).isnull()]
interval_vol = interval_vol.drop(null_idxs, axis=0, errors='ignore')

agg_returns = pd.Series(index=interval_vol.index[:-1])

for i in range(len(interval_vol.index) - 1):
    start_dt, end_dt = interval_vol.index[i], interval_vol.index[i+1]
    weights = pd.Series(0., index=interval_vol.columns)
    
    vol_data = interval_vol.loc[start_dt]
    vol_cutoff = vol_data.quantile(0.1)
    
    weights[vol_data[vol_data < vol_cutoff].index] = 1.0
    weights = weights / weights.sum()
    
    period_returns = stock_returns.loc[start_dt:end_dt]
    period_agg_returns = period_returns.mul(weights, axis='columns').sum(axis=1)
    agg_returns.loc[start_dt] = (period_agg_returns + 1.).prod() - 1.
    
agg_mean = agg_returns.mean() * 12
agg_std = agg_returns.std() * np.sqrt(12)

###############################################################################
#%%

print('Benchmark: Mean Return: {0}, Vol: {1}, Sharpe Ratio: {2}'.format(index_mean,
      index_std, index_mean / index_std))
    
    
print('Strategy: Mean Return: {0}, Vol: {1}, Sharpe Ratio: {2}'.format(agg_mean,
      agg_std, agg_mean / agg_std))

