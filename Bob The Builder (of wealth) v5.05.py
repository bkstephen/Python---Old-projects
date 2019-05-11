print ("         _________________________________________________")
print ("              Bob The Builder (of wealth) - V5.04" )
print("     Financial Markets Trading Robot Created by STEFANOS BEKIARIS")
print ("         _________________________________________________")

import oandapyV20
from oandapyV20 import API
import oandapyV20.endpoints.pricing as pricing
import pandas as pd
import json
import requests
from oandapyV20.contrib.factories import InstrumentsCandlesFactory
import oandapyV20.endpoints.orders as orders
from oandapyV20.contrib.requests import MarketOrderRequest
from oandapyV20.contrib.requests import TakeProfitOrderRequest as TakeProfit
from oandapyV20.contrib.requests import StopLossOrderRequest as StopLoss
from oandapyV20.contrib.requests import TrailingStopLossOrderRequest as TrailingStop
import oandapyV20.endpoints.instruments as instruments
from datetime import date
import oandapyV20.endpoints.trades as trades
import sys
import datetime
import os 

today = str(date.today())

try:
#Define account paramaters
    access_token = # REPLACE THIS WITH API TOKEN FOR OANDA
    accountID = # REPLACE THIS WITH ACCOUNT ID FOR OANDA
    api = oandapyV20.API(access_token=access_token)
except:
    print("Problem with Access Token, AccountID or API.")


#Define the currencies the robot will scan and trade, add in the end of the list for more
currencies = ['USD_CHF','GBP_USD','USD_CAD','EUR_USD','USD_JPY','GBP_AUD','CAD_CHF','EUR_CHF','EUR_GBP','EUR_SGD','EUR_NZD','GBP_CHF','NZD_CAD']
buy = ['USD_CHF','GBP_USD','USD_CAD','EUR_USD','USD_JPY','GBP_AUD','CAD_CHF','EUR_CHF','EUR_GBP','EUR_SGD','EUR_NZD','GBP_CHF','NZD_CAD']
sell = ['USD_CHF','GBP_USD','USD_CAD','EUR_USD','USD_JPY','GBP_AUD','CAD_CHF','EUR_CHF','EUR_GBP','EUR_SGD','EUR_NZD','GBP_CHF','NZD_CAD'] 
count = len(currencies)

try:
    #_from = "2018-09-06T11:00:00Z"
    #_to="2018-09-06T13:16:00Z"
    a=today+"T00:00:00Z"
    b=today+"T06:30:00Z"
    _from = a
    _to = b
except:
    print("Trading session not in the proper timezone, please try later!")
    
def HighLow(instrument, api): #for finding High and Low prices in a time range
    granularity="M15"

    params ={        
                "from": _from,
                "granularity": granularity,
                "to": _to
            }
    for r in InstrumentsCandlesFactory(instrument=instrument,params=params):
        api.request(r)      
        close = r.response.get('candles')
        #print(json.dumps(r.response.get('candles'), indent=2))
        high = close[0]['mid']['h']
        low = close[0]['mid']['l']
        count = len(close)
        for i in range (0,count) :
            #print (close[i]['mid']['c'])
            x1 = close[i]['mid']['h']
            x2 = close[i]['mid']['l']
            if x1 > high :
                high = x1
            if x2 < low:
                low = x2
        #print ("---")        
        #print(high);
        #print(low);
        return (high, low)



def OrderBuy(currency,high,low,multiplier):
    
    if currency=="USD_JPY":
        qty = 2000
    else:
        qty = 3000

        
    mo = MarketOrderRequest(instrument=str(currency), units=qty)
    #print(json.dumps(mo.data, indent=4))
    r = orders.OrderCreate(accountID, data=mo.data)
    rv = api.request(r)
    idlist = r.response.get("lastTransactionID")
    print ("Transaction ID: " ,idlist)

    #TAKE PROFIT, STOP LOSS ON ORDER ID ABOVE
    tradeprice = r.response.get("orderFillTransaction")
    p = float(tradeprice["price"])    
    spread = high - low
    profitprice = p + spread*multiplier
    lossprice = p - spread*multiplier
    trailingStopDistance = spread*multiplier
    
    print ("Open Price: " ,p)
    print("Take Profit: ",profitprice)
    print ("Stop Loss: ", lossprice)
    profit = TakeProfit(tradeID=idlist,price=profitprice)
    #stoploss = StopLoss(tradeID=idlist, price=lossprice)
    stoploss = TrailingStop(tradeID=idlist, distance=trailingStopDistance)
    r1 = orders.OrderCreate(accountID, data=profit.data)
    r2 = orders.OrderCreate(accountID, data=stoploss.data)
    rv1=api.request(r1)
    rv2=api.request(r2)

def OrderSell(currency,high,low,multiplier):
    
    if currency=="USD_JPY":
        qty = -2000
    else:
        qty = -3000
    
    mo = MarketOrderRequest(instrument=str(currency), units=qty)
    #print(json.dumps(mo.data, indent=4))
    r = orders.OrderCreate(accountID, data=mo.data)
    rv = api.request(r)
    idlist = r.response.get("lastTransactionID")
    print ("Transaction ID: " ,idlist)

    #TAKE PROFIT, STOP LOSS ON ORDER ID ABOVE
    tradeprice = r.response.get("orderFillTransaction")
    p = float(tradeprice["price"])    
    spread = high - low
    profitprice = p - spread*multiplier
    lossprice = p + spread*multiplier
    trailingStopDistance = spread*multiplier
    
    print ("Open Price: " ,p)
    print("Take Profit: ",profitprice)
    print ("Stop Loss: ", lossprice)
    profit = TakeProfit(tradeID=idlist,price=profitprice)
    #stoploss = StopLoss(tradeID=idlist, price=lossprice)
    stoploss = TrailingStop(tradeID=idlist, distance=trailingStopDistance)
    r1 = orders.OrderCreate(accountID, data=profit.data)
    r2 = orders.OrderCreate(accountID, data=stoploss.data)
    rv1=api.request(r1)
    rv2=api.request(r2)
    
def currentPrice(currency):
    params = {
                "instruments": currency
            }
    r = pricing.PricingInfo(accountID=accountID, params=params)
    rv = api.request(r)
    candle = r.response.get('prices')
    ask = round(float(candle [0]['asks'][0]['price']),6)
    
    #print ("Ask: " , ask)
    return (ask)

#RSI CALCULATOR BELOW
def rsiCalculator(instrument, granularity, count):


    client = API(access_token="01535c6a20bf0c5b52a5b965ef43ec5d-ea7f04060daa73d34e0feb8528b8aca5")
    params = {
                "granularity": granularity,
                "count": count,
             }
    closing_prices = []
    i = 0 
    for r in InstrumentsCandlesFactory(instrument=instrument,params=params):
        client.request(r)
        values = r.response.get('candles')
        closing_prices.append(r.response.get('candles')[i]['mid']['c'])
        i=i+1
        #print (values[i]['mid']['c'])
        #print (json.dumps(r.response.get('candles'), indent=2))
    #print (closing_prices)
    gains = 0
    losses = 0
    gains_counter = 0
    losses_counter = 0
    for i in range (0,count-1):
        a = float(values[i]['mid']['c'])
        b = float(values[i+1]['mid']['c'])
        test = b - a
        if test >= 0:
            gains = gains + test
            gains_counter += 1
        else:
            losses = losses + test
            losses_counter += 1
        #print(values[i]['mid']['c'])

    avg_gains = gains/gains_counter
    avg_losses = -losses/losses_counter
    avg = avg_gains/avg_losses

    rsi = 100 - (100 /(1+avg))
    return (float(rsi))

#MOVING AVERAGE ESTIMATE, SUBJECT TO SMALL STANDARD OF ERROR
def movingAverage(instrument, granularity, count):

    count = count-1
    client = API(access_token="01535c6a20bf0c5b52a5b965ef43ec5d-ea7f04060daa73d34e0feb8528b8aca5")
    params = {
                "count": count,
                "granularity": granularity,
                }
    r = instruments.InstrumentsCandles(instrument=instrument,params=params)
    client.request(r)
    values = r.response.get('candles')
    sumList = 0
    for i in range (0,count):
        sumList = sumList + float (values[i]['mid']['c'])
           
    price = currentPrice(instrument)
    sumList = sumList + price      
    
    return (sumList/(count+1))

#EXPOTENTIAL MOVING AVERAGE CALCULATOR GIVEN count PERIODS
def EMA(instrument, granularity, count):
    ma = movingAverage(instrument, granularity, count)
    smoothing = 2/(1+count)
    ema = (currentPrice(instrument)*smoothing)+(ma*(1-smoothing))
    return (ema)

#CHECKS IF CURRENCY ALREADY HAS A TRADE OPEN
def checkOpenTrades(currency):
    r = trades.OpenTrades(accountID=accountID)
    api.request(r)
    a = r.response.get('trades')
    for i in range (0,len(a)):
        if currency in a[i]['instrument']:
            return (True)        
    return (False)

# CHECK IF CURRENCY HAS BEEN BOUGHT ALREADY BASED ON THE LIST: buy
def BuyCheck(currency):

    if currency in buy:
        buy.remove(currency)
        return (True)
    else:
        return (False)
    
# CHECK IF CURRENCY HAS BEEN SOLD ALREADY BASED ON THE LIST: sell
def SellCheck(currency):

    if currency in sell:
        sell.remove(currency)
        return (True)
    else:
        return (False)

#RUNS UNTIL IT IS 17:16
hour = int(datetime.datetime.now().hour)
minute = int(datetime.datetime.now().minute)
if hour==17:
    h = 31 - minute
else:
    h = 17*60-hour*60+31-minute
if h > 0:
    while hour !=17 or minute != 30:
        hour = int(datetime.datetime.now().hour)
        minute = int(datetime.datetime.now().minute)
        if hour==17:
            m = 31 - minute
        else:
            m = 17*60-hour*60+31-minute
        if h == m:
            h = h - 1
            print("Minutes Until Start of Trading: ",m)
    
    

#RUNS ONLY ONCE AT THE BEGGING
for i in range (0,len(currencies)):
    if checkOpenTrades(currencies[i])==True:
        buy.remove(currencies[i])
        
for i in range (0,len(currencies)):
    if checkOpenTrades(currencies[i])==True:
        sell.remove(currencies[i])
        

#CHECKS THE RANGE FOR WHICH THE CURRENCY TRADED DURING LONDON TZ
for i in range (0,len(currencies)):
    try:
        print (currencies[i])
        high = round(float(HighLow(currencies[i],api)[0]),6)
        low = round(float(HighLow(currencies[i],api)[1]),6)
        check = high - low
        if check>=0.05:
            sell.remove(currencies[i])
            buy.remove(currencies[i])
            
    except:
        print ("Error occured while conducting pre checks")
print ("ALGORITHM IS RUNNING")            
#execution of code bellow:    

while 0 < 1:
    
    for n in range (0,count): #prints low high for all currencies

        try:
            high = round(float(HighLow(currencies[n],api)[0]),6)
            low = round(float(HighLow(currencies[n],api)[1]),6)
            current_price = currentPrice(currencies[n])
            #print (currencies[n])
            #print ("Current price: ",current_price, "| Highest in range: ",high,"| Lowest in range: ", low )
            #print ("Highest in range: ",high)
            #print ("Lowest in range: ", low)
        except:
            print ("Problem with retrieving High, Low or Current price occured")
        try:
            if current_price > (high+(high*0.0003)) and current_price > movingAverage(currencies[n],"M15",100):
                if BuyCheck(currencies[n])==True:
                    print (currencies[n])
                    OrderBuy(currencies[n],high,low,0.5)


        except:
            print ("Problem with the Buy checks, Buy orders occured")
        try:    
            if current_price < (low-(low*0.0003)) and current_price < movingAverage(currencies[n],"M15",100):
                if SellCheck(currencies[n])==True:
                    print (currencies[n])
                    OrderSell(currencies[n],high,low,0.5)

        except:
            print("Problem with the Sell checks, Sell orders occured")
    
    #restarts program at 4AM
    #hour = int(datetime.datetime.now().hour)
    #if hour == 4:
        #python = sys.executable
        #os.execl(python, python, * sys.argv)
                    
        
#CREATED BY STEFANOS BEKIARIS

    









            
    




