import streamlit as st
import pandas as pd
import requests
from webull import webull
from fredapi import Fred
import helper
import numpy
import math
from streamlit_autorefresh import st_autorefresh
from bs4 import BeautifulSoup
fred = Fred(api_key='6d08d5b6749aad4b7ae0e4c1dcfca79c')


influxCoockie = '_pk_id.1.5336=b71512efe30a90c0.1671653720.; _pk_ses.1.5336=1; grafana_session=447786de724042161f11d364216bd5f8'
helper.setPageConfig()
wb = webull()
col1, col2, col3, col4, col5, col6, col7, col8, col9= st.columns([4, 4, 4, 4, 4, 3, 3, 3, 3], gap='medium')
col10, col11, col12, col13 = st.columns([3, 3, 3, 2])


def getPricesForCanvas():
    tickerArray = []
    url = 'https://quote.cnbc.com/quote-html-webservice/restQuote/symbolType/symbol?symbols=@VX.1%7C@VX.2%7C@VX.3%7CUS2Y%7CUS5Y%7CUS10Y%7CUS20Y%7C@W.1%7C@S.1%7C@C.1%7CCADUSD=%7CJPYUSD=%7CGBP=%7CEUR=%7CAUD=%7CPLTR%7CAAPL%7CAMZN%7CGOOG%7CTSLA&requestMethod=itv&noform=1&partnerId=2&fund=1&exthrs=1&output=json&events=1'
    request = requests.get(url)
    data = request.json()['FormattedQuoteResult']['FormattedQuote']
    for ticker in data:
        tickerFormatted = helper.getCNBCPrices(ticker)
        tickerArray.append(tickerFormatted)
    insertCanvasForTikers(tickerArray)


def insertCanvasForTikers(tickerArray):
    #print(tickerArray)
    vix1 = [x for x in tickerArray if x["symbol"] == 'VX.1' ][0]
    vix2 = [x for x in tickerArray if x["symbol"] == 'VX.2' ][0]
    vix3 = [x for x in tickerArray if x["symbol"] == 'VX.3' ][0]
    vixSpread1 = {'symbol': '-VX.1/VX.2', 'price': - vix1['price'] + vix2['price'], 'change': ''}
    vixSpread2 = {'symbol': '-VX.2/VX.3', 'price': - vix2['price'] + vix3['price'], 'change': ''}
    fedFundRateValue = getFredDataHistory('DFF', 1)['close'][0]
    fedFundRate = {'symbol': 'FUND-RATE', 'price': fedFundRateValue, 'change': ''}
    with col1:
        st.markdown(helper.createCanvaForTicker(vix1), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == 'US 2-YR' ][0]), unsafe_allow_html=True)

    with col2:
        st.markdown(helper.createCanvaForTicker(vix2), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == 'US 5-YR' ][0]), unsafe_allow_html=True)

    with col3:
        st.markdown(helper.createCanvaForTicker(vix3), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == 'US 10-YR' ][0]), unsafe_allow_html=True)

    with col4:
        st.markdown(helper.createCanvaForTicker(vixSpread1), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == 'US 20-YR' ][0]), unsafe_allow_html=True)

    with col5:
        st.markdown(helper.createCanvaForTicker(vixSpread2), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(fedFundRate), unsafe_allow_html=True)


def insertCharts():
    with col10:
        fiveYearYield, fiveYearYieldTitle = getFredDataHistoryForChart('DGS5', 'Current Yield', 10000, percentage=True)
        fedFundRate, fedFundRateTitle = getFredDataHistoryForChart('DFF', 'Current Yield', 10000, percentage=True)
        resultDF = pd.concat([fiveYearYield, fedFundRate], axis=1, join="outer")
        teste = pd.merge(fiveYearYield, fedFundRate, how='inner', on='time')
        #print(teste)
        helper.createChartEconomy2(teste, fiveYearYieldTitle, 750, 300, titleFonteSize=20, yFormat=".2%")

    with col11:
        dataf =  wb.get_bars('VIX', None,'d1', 120, 1)
        #helper.createChart(dataf, 'VIX')

    with col12:
        columns = ['open_time','open', 'high', 'low', 'close', 'volume','close_time', 'qav','num_trades','taker_base_vol','taker_quote_vol', 'ignore']
        binanceAPI = requests.get('https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=170')
        bitcoinData = binanceAPI.json()
        bitcoindf = pd.DataFrame(bitcoinData, columns=columns, dtype=float)
        bitcoindf.index = [pd.to_datetime(x, unit='ms').strftime('%Y-%m-%d %H:%M:%S') for x in bitcoindf.open_time]
        helper.createChart(bitcoindf, 'BTC')


def getFredDataHistory(ticker, nTimes, multiplier=1, percentage=False):
    data = fred.get_series_latest_release(ticker)
    data_df = data[-nTimes:].copy()
    data_df = data_df.dropna()
    values = numpy.array(data_df.values * multiplier)
    dates = numpy.array(data_df.index.values)
    currentValue = data_df[len(data_df)-1]
    if percentage:
        values  = [x / 100 for x in values]
        currentValue = '{:.2f}%'.format(currentValue)
    finaldf = pd.DataFrame(list(zip(dates, values))) 
    finaldf.reset_index(inplace=True)
    finaldf.columns =['index', 'time', 'close']
    return finaldf


def getCMEData():
    s = requests.Session()
    r = s.get('https://cmegroup-tools.quikstrike.net/User/QuikStrikeTools.aspx?viewitemid=IntegratedFedWatchTool&userId=lwolf&jobRole=&company=&companyType=&userId=lwolf&jobRole=&company=&companyType=')
    soup2 = BeautifulSoup(r.content, "html.parser")
    #print(soup2)
    table = soup2.find("table", class_="grid-thm grid-thm-v2 w-lg")
    if table:
        rows = table.findAll('tr', {"class":""})
        for tr in rows:
            cols = tr.find_all('td')
            if cols:
                range = cols[0].text
                probab = cols[1].text
                print(range, '- ', probab)


def getFredDataHistoryForChart(ticker, title, nTimes, multiplier=1, milify=False, percentage=False):
    data = fred.get_series_latest_release(ticker)
    data_df = data[-nTimes:].copy()
    data_df = data_df.dropna()
    values = numpy.array(data_df.values * multiplier)
    dates = numpy.array(data_df.index.values)
    currentValue = data_df[len(data_df)-1]
    if milify:
        currentValue = millify(currentValue * multiplier) 
    if percentage:
        values  = [x / 100 for x in values]
        currentValue = '{:.2f}%'.format(currentValue)
    finaldf = pd.DataFrame(list(zip(dates, values))) 
    finaldf.reset_index(inplace=True)
    finaldf.columns =['index', 'time', 'close']
    currentTitle = title + ' ' + str(currentValue)
    return finaldf, currentTitle


def millify(n):
    millnames = ['$',' K$',' M$',' B$',' T$']
    n = float(n)
    millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
    text = '{:.0f}{}'.format(n / 10**(3 * millidx), millnames[millidx])

    return text.replace(' ', '')


if __name__ == '__main__':
    #try:
        getPricesForCanvas()
        getCMEData()
        insertCharts()
        #st_autorefresh(interval=50000, limit=100000, key="fizzbuzzcounter")
    #except:
    #    print('error')

        





