import requests as re
from bs4 import BeautifulSoup
import json
import csv
import os
import yfinance as yf
import time
import pandas as pd
from flask import Flask, request, jsonify,Response

app = Flask(__name__)

requestHeader={
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
  'accept-language': 'en-US,en;q=0.9',
  'cache-control': 'no-cache',
  'pragma': 'no-cache',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
}

def getSummary(ticker):
    while True:
        page=re.get('https://finance.yahoo.com/quote/'+ticker,headers=requestHeader)
        pageParser=BeautifulSoup(page.content,'html.parser')
        try:
          summaryDiv=pageParser.find('div',{'id':'quote-summary'})
          leftTableTr=summaryDiv.find('div',{'data-test':'left-summary-table'}).find('table').findAll('tr')
          rightTableTr=summaryDiv.find('div',{'data-test':'right-summary-table'}).find('table').findAll('tr')
        except AttributeError:
          print('.',end='')
          continue
        break
    dataDict={}
    dataDict['Ticker']=ticker
    for row in leftTableTr+rightTableTr:
        name,value=row.findAll('td')
        dataDict[name.text.strip()]=value.text.strip()
    return dataDict


@app.route('/api/v1/summary/', methods=['GET'])
def summary():
    # Retrieve the name from url parameter
    ticker = request.args.get("ticker", None)
    response=getSummary(ticker)
    return jsonify(response)

@app.route('/api/v1/historical-data/', methods=['GET'])
def getHistoricalData():
    ticker = request.args.get("ticker", None)
    tick = yf.Ticker(ticker)
    try:
      df=tick.history(period="max")
    except ValueError as e:
      if 'No data found, symbol may be delisted' in str(e):
          return Response({'error':ticker+' not found'}, status=404, mimetype='application/json')
      df=tick.history(period="5Y")
    print(df.head())
    return Response(df.to_json(orient='table',index=True), status=200, mimetype='application/json')
      
@app.route('/', methods=['GET'])
def index():
    return "<h1>Welcome to our server !!, Please use the API to do tasks</h1>"

if __name__ == '__main__':
    app.run()
