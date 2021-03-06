# -*- coding: utf-8 -*-
"""Untitled22.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zGK3CvZ797Z0tSF-U-Tb8VAiBjIlZZ-y
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pandas import Series
# %matplotlib inline
import warnings

train = pd.read_csv('Train_SU63ISt.csv')
test = pd.read_csv("Test_0qrQsBZ.csv")

train.head(4)

train_original = train.copy()
test_original = test.copy()

train.columns,test.columns

train.dtypes, test.dtypes

train.shape, test.shape

"""**Feature Extraction**"""

train['Datetime'] = pd.to_datetime(train.Datetime, format='%d-%m-%Y %H:%M')
test['Datetime'] = pd.to_datetime(test.Datetime, format='%d-%m-%Y %H:%M')
train_original['Datetime'] = pd.to_datetime(train_original.Datetime, format='%d-%m-%Y %H:%M')
test_original['Datetime'] = pd.to_datetime(test_original.Datetime, format='%d-%m-%Y %H:%M')

train.head(4)

for i in(train, test, train_original, test_original):
  i['year'] = i.Datetime.dt.year
  i['month'] = i.Datetime.dt.month
  i['day'] = i.Datetime.dt.day
  i['Hour'] = i.Datetime.dt.hour

train.head(4)

train['day of week'] = train['Datetime'].dt.dayofweek
temp = train['Datetime']

train.head(4)

def applyer(row):
  if row.dayofweek == 5 or row.dayofweek == 6:
    return 1
  else:
    return 0

temp2 = temp.apply(applyer)
train['weekend'] = temp2
train.head(4)

train.index = train['Datetime']
df = train.drop('ID',1)
ts = df['Count']

plt.figure(figsize=(16,8))
plt.plot(ts, label='Passenger Count')
plt.title('Time Series')
plt.xlabel('Time(year-month)')
plt.ylabel('Passenger Count')
plt.legend(loc='best')

"""**Exploratory Analysis**"""

train.groupby('year')['Count'].mean().plot.bar()

train.groupby('month')['Count'].mean().plot.bar()

temp3 = train.groupby(['year', 'month'])['Count'].mean()
temp3.plot(figsize=(15,5), title ='Passenger Count(monthwise)')

train.groupby('day')['Count'].mean().plot.bar()

train.groupby('Hour')['Count'].mean().plot.bar()

train.groupby('weekend')['Count'].mean().plot.bar()

train.groupby('day of week')['Count'].mean().plot.bar()

train = train.drop('ID',1)

train.Timestamp = pd.to_datetime(train.Datetime, format='%d-%m-%Y %H:%M')
train.index = train.Timestamp

hourly = train.resample('H').mean()
daily = train.resample('D').mean()
weekly = train.resample('W').mean()
monthly = train.resample('M').mean()

hourly.shape, daily.shape, weekly.shape,  monthly.shape

fig, axs = plt.subplots(4,1)
hourly.Count.plot(figsize = (15,8), title = 'Hourly', fontsize = 14, ax=axs[0])
daily.Count.plot(figsize = (15,8), title = 'Daily', fontsize = 14, ax=axs[1])
weekly.Count.plot(figsize = (15,8), title = 'Weekly', fontsize = 14, ax=axs[2])
monthly.Count.plot(figsize = (15,8), title = 'Monthly', fontsize = 14, ax=axs[3])

test.Timestamp = pd.to_datetime(test.Datetime, format='%d-%m-%Y %H:%M')
test.index = test.Timestamp

test = test.resample('D').mean()
test.head(4)

train.Timestamp = pd.to_datetime(train.Datetime, format='%d-%m-%Y %H:%M')
train.index = train.Timestamp

train = train.resample('D').mean()
train.head(4)

"""**Data** **Split**"""

Train = train.loc['2012-08-25' : '2014-06-24']
valid = train.loc['2014-06-25' : '2014-09-25']

Train.Count.plot(figsize = (15,8), title = 'Daily Ridership', fontsize = 14, label='train')
valid.Count.plot(figsize = (15,8), title = 'Daily Ridership', fontsize = 14, label='valid')
plt.xlabel('Datetime')
plt.ylabel('Passenger Count') 
plt.legend(loc='best') 
plt.show()

"""**Naive** **Approach**"""

dd = np.asarray(Train.Count)
y_hat = valid.copy()
y_hat['naive'] = dd[len(dd)-1]
plt.figure(figsize=(12,8))
plt.plot(Train.index, Train['Count'], label='Train')
plt.plot(valid.index, valid['Count'], label='vaild')
plt.plot(y_hat.index, y_hat['naive'], label='naive forecast')
plt.legend(loc='best')
plt.title('Nive Forecast')
plt.show()

from sklearn.metrics import mean_squared_error
from math import sqrt
rmse = sqrt(mean_squared_error(valid.Count,y_hat.naive))
print(rmse)

"""**Moving Average**"""

y_hat_avg = valid.copy()
y_hat_avg['moving_avg_forecast'] = Train['Count'].rolling(10).mean().iloc[-1]
plt.figure(figsize=(15,5))
plt.plot(Train.index, Train['Count'], label='Train')
plt.plot(valid.index, valid['Count'], label='vaild')
plt.plot(y_hat.index, y_hat_avg['moving_avg_forecast'], label='naive forecast')
plt.legend(loc='best')
plt.title('Moving avg Forecast')
plt.show()

rmse = sqrt(mean_squared_error(valid.Count,y_hat_avg.moving_avg_forecast))
print(rmse)

"""**Simple Exponential Smoothing**"""

from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt
y_hat_avg = valid.copy()
fit2 = SimpleExpSmoothing(np.asarray(Train['Count'])).fit(smoothing_level =0.6, optimized =False)
y_hat_avg['SES'] = fit2.forecast(len(valid))
plt.figure(figsize=(16,8))
plt.plot(Train.index, Train['Count'], label='Train')
plt.plot(valid.index, valid['Count'], label='vaild')
plt.plot(y_hat.index, y_hat_avg['SES'], label='SES')
plt.legend(loc='best')
plt.show()

rmse = sqrt(mean_squared_error(valid.Count,y_hat_avg.SES))
print(rmse)

"""**Holt's Linear Model**"""

import statsmodels.api as sm
sm.tsa.seasonal_decompose(Train.Count).plot()
result = sm.tsa.stattools.adfuller(train.Count)
plt.show()

y_hat_avg = valid.copy()
fit1 = Holt(np.asarray(Train['Count'])).fit(smoothing_level =0.3, smoothing_slope =0.1)
y_hat_avg['Holt_linear'] = fit1.forecast(len(valid))
plt.figure(figsize=(16,8))
plt.plot(Train.index, Train['Count'], label='Train')
plt.plot(valid.index, valid['Count'], label='vaild')
plt.plot(y_hat.index, y_hat_avg['Holt_linear'], label='Holt_linear')
plt.legend(loc='best')
plt.show()

rmse = sqrt(mean_squared_error(valid.Count,y_hat_avg.Holt_linear))
print(rmse)

predict = fit1.forecast(len(test))
test['prediction'] = predict
print(test.head(4))
train_original['ratio'] = train_original['Count']/train_original['Count'].sum()
print(train_original.head(4))
temp = train_original.groupby(['Hour'])['ratio'].sum()
print(temp.head(4))
pd.DataFrame(temp,columns=['Hour', 'ratio']).to_csv('GROUPby.csv')

temp2 = pd.read_csv('GROUPby.csv')
temp2 = temp2.drop('Hour.1',1)

temp2.head(4)

merge = pd.merge(test, test_original, on=('day','month','year'), how='left')
print(merge.head(4))
merge['Hour'] = merge['Hour_y']
merge = merge.drop(['year', 'month', 'Datetime', 'Hour_x', 'Hour_y'], axis=1)
print(merge.head(4))
prediction = pd.merge(merge, temp2, on='Hour', how='left')
print(prediction.head(4))

prediction['Count'] = prediction['prediction']*prediction['ratio']*24
prediction['ID'] = prediction['ID_y']

submission = prediction.drop(['ID_x','day','ID_y','prediction', 'Hour', 'ratio'], axis=1)
pd.DataFrame(submission, columns=['ID', 'Count']).to_csv('Holt_linear.csv', index=False)

submission

"""**Holt's Winter Model**"""

y_hat_avg = valid.copy()
fit1 = ExponentialSmoothing(np.asarray(Train['Count']),seasonal_periods=7, trend= 'add', seasonal='add').fit()
y_hat_avg['Holt_Winter'] = fit1.forecast(len(valid))
plt.figure(figsize=(16,8))
plt.plot(Train.index, Train['Count'], label='Train')
plt.plot(valid.index, valid['Count'], label='vaild')
plt.plot(y_hat.index, y_hat_avg['Holt_Winter'], label='Holt_Winter')
plt.legend(loc='best')
plt.show()

rmse = sqrt(mean_squared_error(valid.Count,y_hat_avg.Holt_Winter))
print(rmse)

predict = fit1.forecast(len(test))
test['prediction'] = predict
print(test.head(4))
merge = pd.merge(test, test_original, on=('day','month','year'), how='left')
print(merge.head(4))
merge['Hour'] = merge['Hour_y']
merge = merge.drop(['year', 'month', 'Datetime', 'Hour_x', 'Hour_y'], axis=1)

prediction = pd.merge(merge, temp2, on='Hour', how='left')
print(prediction.head(4))
prediction['Count'] = prediction['prediction']*prediction['ratio']*24
prediction['ID'] = prediction['ID_y']

submission = prediction.drop(['ID_x','day','ID_y','prediction', 'Hour', 'ratio'], axis=1)
pd.DataFrame(submission, columns=['ID', 'Count']).to_csv('Holt_Winter.csv', index=False)

submission

"""**Stationary Check**"""

from statsmodels.tsa.stattools import adfuller
def test_stationarity(timeseries):
    
    #Determing rolling statistics
    rolmean = timeseries.rolling(24).mean()
    rolstd = timeseries.rolling(24).std()

    #Plot rolling statistics:
    orig = plt.plot(timeseries, color='blue',label='Original')
    mean = plt.plot(rolmean, color='red', label='Rolling Mean')
    std = plt.plot(rolstd, color='black', label = 'Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean & Standard Deviation')
    plt.show(block=False)
    
    #Perform Dickey-Fuller test:
    print ('Results of Dickey-Fuller Test:')
    dftest = adfuller(timeseries, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    for key,value in dftest[4].items():
        dfoutput['Critical Value (%s)'%key] = value
    print (dfoutput)

from matplotlib.pylab import rcParams
rcParams['figure.figsize'] = 20,10
test_stationarity(train_original['Count'])

"""**Removing Trend**"""

Train_log = np.log(Train['Count'])
valid_log = np.log(valid['Count'])

moving_avg = Train_log.rolling(24).mean()
plt.plot(Train_log)
plt.plot(moving_avg, color='red')
plt.show()

train_log_moving_avg_diff = Train_log - moving_avg
train_log_moving_avg_diff.dropna(inplace = True)
test_stationarity(train_log_moving_avg_diff)

train_log_diff = Train_log - Train_log.shift(1)
test_stationarity(train_log_diff.dropna())

"""**Removing Seasonality**"""

from statsmodels.tsa.seasonal import seasonal_decompose
decomposition = seasonal_decompose(pd.DataFrame(Train_log).Count.values, freq = 24)

trend = decomposition.trend
seasonal = decomposition.seasonal
residual = decomposition.resid

plt.subplot(411)
plt.plot(Train_log, label='Original')
plt.legend(loc='best')
plt.subplot(412)
plt.plot(trend, label='Trend')
plt.legend(loc='best')
plt.subplot(413)
plt.plot(seasonal,label='Seasonality')
plt.legend(loc='best')
plt.subplot(414)
plt.plot(residual, label='Residuals')
plt.legend(loc='best')
plt.tight_layout()
plt.show()

train_log_decompose = pd.DataFrame(residual)
train_log_decompose['date'] = Train_log.index
train_log_decompose.set_index('date', inplace = True)
train_log_decompose.dropna(inplace=True)
test_stationarity(train_log_decompose[0])

"""**ACF, PACF**"""

from statsmodels.tsa.stattools import acf, pacf
lag_acf = acf(train_log_diff.dropna(), nlags=25)
lag_pacf = pacf(train_log_diff.dropna(), nlags=25, method='ols')

plt.plot(lag_acf)
plt.axhline(y=0,linestyle='--',color='gray')
plt.axhline(y=-1.96/np.sqrt(len(train_log_diff.dropna())),linestyle='--',color='gray')
plt.axhline(y=1.96/np.sqrt(len(train_log_diff.dropna())),linestyle='--',color='gray')
plt.title('Autocorrelation Function')

plt.plot(lag_pacf)
plt.axhline(y=0,linestyle='--',color='gray')
plt.axhline(y=-1.96/np.sqrt(len(train_log_diff.dropna())),linestyle='--',color='gray')
plt.axhline(y=1.96/np.sqrt(len(train_log_diff.dropna())),linestyle='--',color='gray')
plt.title('Partial Autocorrelation Function')
plt.tight_layout()

"""**AR Model**"""

from statsmodels.tsa.arima_model import ARIMA
model = ARIMA(Train_log, order=(2, 1, 0))  
results_AR = model.fit(disp=-1)  
plt.plot(train_log_diff.dropna())
plt.plot(results_AR.fittedvalues, color='red')
plt.title('RSS: %.4f'% sum((results_AR.fittedvalues-train_log_diff.dropna())**2))

AR_predict = results_AR.predict(start='2014-06-25', end='2014-09-25')
AR_predict = AR_predict.cumsum().shift().fillna(0)
AR_predict1 = pd.Series(np.ones(valid.shape[0])*np.log(valid['Count'])[0], index = valid.index)
AR_predict1  = AR_predict1.add(AR_predict, fill_value=0)
AR_predict = np.exp(AR_predict1)

plt.plot(valid['Count'], label = 'Valid')
plt.plot(AR_predict, color='red', label = 'Predict')
plt.title('RMSE: %.4f'% (np.sqrt(np.dot(AR_predict, valid['Count']))/valid.shape[0]))

AR_predict_test = results_AR.forecast(len(test))
test['prediction'] = predict
merge = pd.merge(test, test_original, on=('day','month','year'), how='left')
merge['Hour'] = merge['Hour_y']
merge = merge.drop(['year', 'month', 'Datetime', 'Hour_x', 'Hour_y'], axis=1)
prediction = pd.merge(merge, temp2, on='Hour', how='left')

prediction['Count'] = prediction['prediction']*prediction['ratio']*24
prediction['ID'] = prediction['ID_y']
submission = prediction.drop(['ID_x','day','ID_y','prediction', 'Hour', 'ratio'], axis=1)
pd.DataFrame(submission, columns=['ID', 'Count']).to_csv('AR.csv', index=False)

"""**MA Model**"""

model = ARIMA(Train_log, order=(0, 1, 2))  
results_MA = model.fit(disp=-1)  
plt.plot(train_log_diff.dropna())
plt.plot(results_MA.fittedvalues, color='red')
plt.title('RSS: %.4f'% sum((results_MA.fittedvalues-train_log_diff.dropna())**2))

MA_predict = results_MA.predict(start='2014-06-25', end='2014-09-25')
MA_predict = MA_predict.cumsum().shift().fillna(0)
MA_predict1 = pd.Series(np.ones(valid.shape[0])*np.log(valid['Count'])[0], index = valid.index)
MA_predict1  = MA_predict1.add(MA_predict, fill_value=0)
MA_predict = np.exp(MA_predict1)

plt.plot(valid['Count'], label = 'Valid')
plt.plot(MA_predict, color='red', label = 'Predict')
plt.title('RMSE: %.4f'% (np.sqrt(np.dot(MA_predict, valid['Count']))/valid.shape[0]))

MA_predict_test = results_MA.forecast(len(test))
test['prediction'] = predict
merge = pd.merge(test, test_original, on=('day','month','year'), how='left')
merge['Hour'] = merge['Hour_y']
merge = merge.drop(['year', 'month', 'Datetime', 'Hour_x', 'Hour_y'], axis=1)
prediction = pd.merge(merge, temp2, on='Hour', how='left')

prediction['Count'] = prediction['prediction']*prediction['ratio']*24
prediction['ID'] = prediction['ID_y']
submission = prediction.drop(['ID_x','day','ID_y','prediction', 'Hour', 'ratio'], axis=1)
pd.DataFrame(submission, columns=['ID', 'Count']).to_csv('MA.csv', index=False)

"""**Combined Model**"""

model = ARIMA(Train_log, order=(2, 1, 2))  
results_ARIMA = model.fit(disp=-1)  
plt.plot(train_log_diff.dropna())
plt.plot(results_ARIMA.fittedvalues, color='red')
plt.title('RSS: %.4f'% sum((results_ARIMA.fittedvalues-train_log_diff.dropna())**2))

def check_prediction_diff(predict_diff, given_set):
  predict_diff = predict_diff.cumsum().shift().fillna(0)
  predict_base = pd.Series(np.ones(given_set.shape[0])*np.log(given_set['Count'])[0], index = given_set.index)
  predict_log  = predict_base.add(predict_diff, fill_value=0)
  predict = np.exp(predict_log)
  plt.plot(given_set['Count'], label = 'given_set')
  plt.plot(predict, color='red', label = 'Predict')
  plt.title('RMSE: %.4f'% (np.sqrt(np.dot(predict, given_set['Count']))/given_set.shape[0]))
  plt.show()

def check_prediction_log(predict_log, given_set):
  predict = np.exp(predict_log)
  plt.plot(given_set['Count'], label = 'given_set')
  plt.plot(predict, color='red', label = 'Predict')
  plt.title('RMSE: %.4f'% (np.sqrt(np.dot(predict, given_set['Count']))/given_set.shape[0]))
  plt.show()

ARIMA_predict_diff = results_ARIMA.predict(start='2014-06-25', end='2014-09-25')
check_prediction_diff(ARIMA_predict_diff,valid)

"""**SARIMAX**"""

import statsmodels.api as sm

y_hat_avg = valid.copy()
fit1 = sm.tsa.statespace.SARIMAX(Train.Count, order=(2,1,4), seasonal_order=(0,1,1,7)).fit()
y_hat_avg['SARIMA'] = fit1.predict(start='2014-06-25', end='2014-09-25', dynamic=True)
plt.figure(figsize=(16,8))
plt.plot(Train['Count'], label='Train')
plt.plot(valid['Count'], label='vaild')
plt.plot(y_hat_avg['SARIMA'], label='SARIMA')
plt.legend(loc='best')
plt.show()

rmse = sqrt(mean_squared_error(valid.Count,y_hat_avg.SARIMA))
print(rmse)

predict = fit1.predict(start='2014-09-26', end='2015-04-26', dynamic=True)
test['prediction'] = predict
merge = pd.merge(test, test_original, on=('day','month','year'), how='left')
merge['Hour'] = merge['Hour_y']
merge = merge.drop(['year', 'month', 'Datetime', 'Hour_x', 'Hour_y'], axis=1)
prediction = pd.merge(merge, temp2, on='Hour', how='left')

prediction['Count'] = prediction['prediction']*prediction['ratio']*24
prediction['ID'] = prediction['ID_y']
submission = prediction.drop(['ID_x','day','ID_y','prediction', 'Hour', 'ratio'], axis=1)
pd.DataFrame(submission, columns=['ID', 'Count']).to_csv('SARIMA.csv', index=False)

submission