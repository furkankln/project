import numpy 
import pandas as pd
import pandas_ta as ta
import bitmex
import requests
import time
import json
import datetime

Id = "-------"
secretId = "--------"
baseURI = "https://www.bitmex.com/api/v1"
endpoint = "/trade/bucketed"
endpointTrade = "/trade"
symbol = 'ETH'

params = {'binSize':'1h', 'symbol':symbol, 'reverse':'true'}
params2 = {'symbol':symbol, 'count':'1', 'reverse':'true'}
isCloudBuy = False
isVolumeBuy = False
isMABuy = False
inPosition = False
cloudGapByPrice = 0.50



while(True):
    r = requests.get(baseURI + endpoint, params = params)
    candles = r.json()

    numpy.priceCandles = []

    for f in reversed(candles):
        numpy.priceCandles.append([f.get('high'), f.get('low'), f.get('close'), f.get('volume')])

    df = pd.DataFrame(data=numpy.priceCandles, columns=['high', 'low', 'close', 'volume'])

    # Tenkan-sen (Conversion Line)
    period9_high = df['high'].rolling(window=9).max()
    period9_low = df['low'].rolling(window=9).min()
    tenkan_sen = (period9_high + period9_low) / 2

    # Kijun-sen (Base Line)
    period26_high = df['high'].rolling(window=26).max()
    period26_low = df['low'].rolling(window=26).min()
    kijun_sen = (period26_high + period26_low) / 2

    # Senkou Span-A (Leading Span A)
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2)

    # Senkou Span-B (Leading Span B)
    period52_high = df['high'].rolling(window=52).max()
    period52_low = df['low'].rolling(window=52).min()
    senkou_span_b = ((period52_high + period52_low) / 2)

    # Calculate vwma20 and sma20
    vwma20 = ta.vwma(df['close'], df['volume'], length=20, offset=-3)
    sma20 = ta.sma(df['close'], length=20, offset=0)

  
       
    
    if vwma20.get(96) > sma20.get(96):
        isVolumeBuy = True
    else:
        isVolumeBuy = False
    
    if senkou_span_b.get(99) < senkou_span_a.get(99):
        isCloudBuy = True
    else:
        isCloudBuy = False

    if tenkan_sen.get(99) > kijun_sen.get(99):
        isMABuy = True
    else:
        isMABuy = False

    if isCloudBuy and isMABuy and not inPosition:
        print("BUY!!")
        r2 = requests.get(baseURI + endpointTrade, params = params2)
        with open('data.json', 'a') as file:
            json.dump({"buyedAt":r2.json()[0].get('price'),
                        "onDate":r2.json()[0].get('timestamp')}, file, indent=2)
        inPosition = True

    if (not isCloudBuy or not isMABuy) and inPosition:
        print("SELL!!")
        r2 = requests.get(baseURI + endpointTrade, params = params2)
        with open('data.json', 'a') as file:
            json.dump({"selledAt":r2.json()[0].get('price'),
                        "onDate":r2.json()[0].get('timestamp')}, file, indent=2)
        inPosition = False
   
    
    time.sleep(4)
