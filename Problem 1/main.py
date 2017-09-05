
# coding: utf-8

# In[1]:

import pandas as pd
import datetime as dt


# In[2]:

gdp_data = pd.read_csv('./real_gdp_data.csv', index_col=0, parse_dates=[0])
gdp_data.columns = ['GDP']


# In[3]:

sentiment_data = pd.read_csv('./mich_sentiment.csv', skiprows=[0, 1, 2, 4])
sentiment_data_dates = sentiment_data.dropna(subset=['Date'], axis=0).iloc[:1573]
sentiment_data_dates.loc[:, 'Date'] = pd.to_datetime(sentiment_data_dates['Date'])

sentiment_data_cleaned = sentiment_data_dates.set_index('Date')
sentiment_data_cleaned = sentiment_data_cleaned.iloc[:, :3].dropna(axis=0)

for c in sentiment_data_cleaned.columns:
    sentiment_data_cleaned.loc[:, c] = sentiment_data_cleaned[c].str.replace('%', '').astype(float)
    
sent_data_q = sentiment_data_cleaned.resample('Q').mean()
sent_data_q = sent_data_q.reset_index()
sent_data_q['Date'] = sent_data_q['Date'].apply(lambda x: x + dt.timedelta(days=1))
sent_data_q = sent_data_q.set_index('Date')


# In[4]:

final_data = pd.concat([sent_data_q, gdp_data],axis=1).dropna()


# In[5]:

from sklearn.linear_model import LinearRegression

X_data = final_data.iloc[:, :3]
y_data = final_data.iloc[:, -1]

lin_mod = LinearRegression()
_ = lin_mod.fit(X_data, y_data)

print('R-Squared of Linear Regression Model:', lin_mod.score(X_data, y_data))

