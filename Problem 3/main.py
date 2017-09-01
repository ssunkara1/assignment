
# coding: utf-8

# In[1]:


import pandas as pd


# In[2]:


## Fetching the interest rate data:

long_term_libor = pd.read_csv('./long_term_libor.csv', parse_dates=[0], index_col=0)
rates_data = long_term_libor[['GBP12MD156N', 'USD12MD156N']]
rates_data = rates_data / 100.
rates_data['Date String'] = rates_data.reset_index()['DATE'].apply(lambda x: str(x.year) + ' Q' + str((x.month - 1) // 3 + 1)).values

rates = rates_data.groupby('Date String').mean()

## rate_diff is the difference in the LIBOR of GBP and USD
rate_diff = rates.diff(axis=1).iloc[:, -1]


# In[3]:


## Fetching inflation data:

uk_cpi_data = pd.read_csv('uk_cpi_history_reduced.csv', index_col=0)
uk_cpi_cleaned = uk_cpi_data.dropna().loc['1998 Q1':'2017 Q2']

us_cpi_data = pd.read_csv('us_cpi_history.csv', index_col=0, parse_dates=[0]).resample('Q').mean().reset_index()
us_cpi_data['Date Str'] = us_cpi_data['DATE'].apply(lambda x: str(x.year) + ' Q' + str((x.month - 1) // 3 + 1))
us_cpi_cleaned = us_cpi_data.set_index('Date Str').drop('DATE', axis=1)
us_cpi_cleaned = us_cpi_cleaned.loc['1998 Q1':'2017 Q2']

merged_cpi = uk_cpi_cleaned.merge(us_cpi_cleaned, left_index=True, right_index=True)
merged_cpi.columns = ['UK CPI', 'US CPI']

inflation_pct = merged_cpi.pct_change()[1:]
inflation_diff = inflation_pct.diff(axis=1).iloc[:, -1]


# In[6]:


## Fetching Currency data:

gbpusd_curncy = pd.read_csv('./gbpusd_curncy.csv', index_col=0, parse_dates=[0])

gbpusd_curncy = gbpusd_curncy.reset_index()
gbpusd_curncy['Date Str'] = gbpusd_curncy['index'].apply(lambda x: str(x.year) + ' Q' + str((x.month - 1) // 3 + 1)) 
gbpusd_curncy = gbpusd_curncy.groupby('Date Str').mean()


# In[7]:


merged_data = gbpusd_curncy.join(inflation_diff, how='inner').join(rate_diff, how='inner')
merged_data.columns = ['FX', 'Inflation', 'Nominal Rates']

import statsmodels.tsa.stattools as ts

print('******************************')
print('Stationarity tests of initial time series')
for c in merged_data.columns:
    adf_test_res = ts.adfuller(merged_data[c])
    print('ADF test P-value of {0} is: {1}'.format(c, adf_test_res[1]))


# In[36]:


X = merged_data.iloc[:, 1:]
y = merged_data.iloc[:, 0]

import statsmodels.api as sm
X_total = sm.add_constant(X)

ols_res = sm.OLS(y, X).fit()
adf_test = ts.adfuller(ols_res.resid)
print('ADF test P-value of Residuals is: {0}'.format(adf_test[1]))


# In[71]:


## pairs trading:
st_dev = ols_res.resid.std()
stan_resid = (ols_res.resid - ols_res.resid.mean())

import numpy as np
enter_cutoff = st_dev * 0.75
close_cutoff = 0.1
state = 'None' # this can be Long Short or None
start_val = 0.
close_val = 0.
returns = []

for i in stan_resid.index:
    entry = stan_resid.loc[i]
    
    if state == 'None':
        if entry > enter_cutoff:
            state = 'Short'
            start_val = entry
        elif entry < (-enter_cutoff):
            state = 'Long'
            start_val = entry
        else:
            start_val = 0.
            
    elif state == 'Short':
        if entry < close_cutoff:
            state = 'None'
            close_val = entry
            returns.append((start_val - close_val) / abs(start_val))

    elif state == 'Long':
        if entry > (close_cutoff * -1):
            state = 'None'
            close_val = entry
            returns.append((close_val - start_val) / abs(start_val))
            
## handle pnl at end of trading
if state != 'None':
    multiple = -1 if state == 'Short' else 1
    returns.append((entry - start_val) / abs(start_val) * multiple)
    
print('******************************')
print('Pairs Trading Strategy:')    
print('Mean Return: {:.2%}, Vol: {:.2%}'.format(np.mean(returns), np.std(returns)))