import streamlit as st
import pandas as pd
import numpy
from webull import webull
import math
from datetime import datetime
import helper
from streamlit_autorefresh import st_autorefresh
import yfinance as yf
import requests
from fredapi import Fred
import urllib
import urllib.request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import arrow
fred = Fred(api_key='6d08d5b6749aad4b7ae0e4c1dcfca79c')


influxCoockie = '_pk_id.1.5336=b71512efe30a90c0.1671653720.; _pk_ses.1.5336=1; grafana_session=447786de724042161f11d364216bd5f8'
helper.setPageConfig('Economy')
wb = webull()
col1, col2, col3, col4, col5, col6 = st.columns([5, 5, 1, 1, 1, 2], gap='medium')
yChartsHeaders = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 OPR/93.0.0.0'}


def insertCharts():
    with col1:
        currentYield, currentYieldTitle = getFredDataHistory('T10Y2Y', 'Current Yield', 3600, percentage=True)
        helper.createChartEconomy(currentYield, currentYieldTitle, 750, 300, titleFonteSize=20, yFormat=".2%")
        fedBalanceSheet, balanceSheetTitle = getFredDataHistory('WALCL', 'Fed Balance Sheet', 750, milify=True, multiplier=1000000)
        helper.createChartEconomy(fedBalanceSheet, balanceSheetTitle, 750, 300, titleFonteSize=20, yFormat="$.2s")
        cpi, cpiTitle = getFredDataHistory('MEDCPIM158SFRBCLE', 'Consumer Price Index', 168, percentage=True)
        helper.createChartEconomy(cpi, cpiTitle, 750, 300, titleFonteSize=20, yFormat=".2%")
        aud, audTitle = getYtDataHistory()
        helper.createChartEconomy(aud, audTitle, 750, 300, titleFonteSize=20, yFormat="$.2f")

    with col2:
        employmentData, employmentTitle = getFredDataHistory('ADPMNUSNERNSA', 'Total Private Employment', 168, milify=True, multiplier=1)
        helper.createChartEconomy(employmentData, employmentTitle.replace('$', ''), 750, 300, titleFonteSize=20, yFormat=".2s")
        employmentData, employmentTitle = getFredDataHistory('UNRATE', 'Unemployment Rate', 168, percentage=True)
        helper.createChartEconomy(employmentData, employmentTitle, 750, 300, titleFonteSize=20, yFormat=".2%")
        gdp, gdpTitle = getFredDataHistory('GDP', 'Gross Domestic Product', 100, milify=True, multiplier=1000000000)
        helper.createChartEconomy(gdp, gdpTitle, 750, 300, titleFonteSize=20, yFormat="$.2s")
        tbills, tbillsTitle = getFredDataHistory('DTB1YR', 'Tbills Yield', 1750, percentage=True)
        helper.createChartEconomy(tbills, tbillsTitle, 750, 300, titleFonteSize=20, yFormat=".2%")

    with col3:
        st.markdown(f"<p style='text-align: center; font-famlily: Arial Rounded MT Bold; font-weight: bold;'><span style='font-size: 20px'></style>&nbsp;</span></p>", unsafe_allow_html=True)
        bearishValue, bearishChange =  getExposureIndicators('AUSISB')
        st.metric('Bearish', bearishValue, bearishChange)
        putCall, putCallTitle = getYCharts('ACBOEEPCR','Put & Call Ratio')
        helper.createChartEconomy(putCall, putCallTitle, 750, 300, titleFonteSize=20, yFormat=".2f")
        exposureIndex, exposureIndexTitle = getYCharts('ANAAIM','Exposure Index', '3')
        helper.createChartEconomy(exposureIndex, exposureIndexTitle, 750, 300, titleFonteSize=20, yFormat=".3")
        economicEvents = getEconomicEvents()
        helper.createTable(economicEvents, '15px', 'Arial', '756px', '1px 1px', False)

    with col4:
        st.markdown(f"<p style='text-align: right; font-famlily: Arial Rounded MT Bold; font-weight: bold;'><span style='font-size: 20px'>Market</style></span></p>", unsafe_allow_html=True)
        neutalValue, neutalChange =  getExposureIndicators('AUSISN')
        st.metric('Neutral', neutalValue, neutalChange)

    with col5:
        st.markdown(f"<p style='text-align: left; font-famlily: Arial Rounded MT Bold; font-weight: bold; '><span style='font-size: 20px'></style>Sentiment</span></p>", unsafe_allow_html=True)
        bulishValue, bulishChange =  getExposureIndicators('AUSISBNW')
        st.metric('Bullish', bulishValue, bulishChange)
    
    with col6:
        fearGreed, rating = getCnnFear()
        helper.rederGaugeFear(rating.title(), '{:.2f}'.format(fearGreed), '', 0, 100, 10, 'fearGreed')


def getETFHistoryPrice(ticker, symbolText):
    etfData =  wb.get_bars(ticker, None,'d1', 90, 1)
    lastPrice = etfData["close"].iloc[-1]
    lastClose = etfData["close"].iloc[-2]
    change = float(lastPrice - lastClose)
    changePercent = change / lastClose
    lastPrice = '${:.2f}'.format(lastPrice)
    color='rgb(255,255,255)'
    if changePercent > 0:
        color = 'rgb(115, 191, 105)'
    if changePercent < 0:
        color = 'rgb(255, 62, 62)'
    changePercent = '{0:.2%}'.format(changePercent)
    title = symbolText + ' ' + str(lastPrice) + ' (' + str(changePercent) + ')'
    return etfData, title, color


def getFredDataHistory(ticker, title, nTimes, multiplier=1, milify=False, percentage=False):
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


def getYtDataHistory():
    audjpy = yf.Ticker("AUDUSD%3DX")
    data = audjpy.history(period="max")
    data_df = data[-360:].copy()
    data_df.reset_index(inplace=True)
    data_df = data_df.rename(columns = {'Date':'time'})
    data_df = data_df.rename(columns={'Close': 'close'})
    currentValue= ''
    currentTitle = 'AUDJPY ' + str(currentValue) + ' | AUDJPY > 79 Risk on | < 76 Risk off'
    return data_df, currentTitle


def getYCharts(ticker, title, timeframe='1'):
    values = []
    dates = []
    URL = 'https://ycharts.com/charts/fund_data.json?annotations=&annualizedReturns=false&calcs=&chartType=interactive&chartView=&correlations=&dateSelection=range&displayDateRange=false&displayTicker=false&endDate=&format=real&legendOnChart=false&note=&partner=basic_2000&quoteLegend=false&recessions=false&scaleType=linear&securities=id%3AI%3' + ticker + '%2Cinclude%3Atrue%2C%2C&securityGroup=&securitylistName=&securitylistSecurityId=&source=false&splitType=single&startDate=&title=&units=false&useCustomColors=false&useEstimates=false&zoom=' + timeframe + '&redesign=true&chartCreator=&maxPoints=661'
    response = requests.get(URL, headers=yChartsHeaders).json()
    rawData = response['chart_data'][0][0]['raw_data']
    for data in rawData:
        dates.append(datetime.fromtimestamp(data[0] / 1000))
        values.append(data[1])
    finaldf = pd.DataFrame(list(zip(dates, values))) 
    finaldf.reset_index(inplace=True)
    finaldf.columns =['index', 'time', 'close']
    currentValue = response['chart_data'][0][0]['last_value']
    currentTitle = title + ' ' + str(currentValue)
    return finaldf, currentTitle


def getExposureIndicators(ticker):
    URL = 'https://ycharts.com/charts/fund_data.json?annotations=&annualizedReturns=false&calcs=&chartType=interactive&chartView=&correlations=&dateSelection=range&displayDateRange=false&displayTicker=false&endDate=&format=real&legendOnChart=false&note=&partner=basic_2000&quoteLegend=false&recessions=false&scaleType=linear&securities=id%3AI%3' + ticker + '%2Cinclude%3Atrue%2C%2C&securityGroup=&securitylistName=&securitylistSecurityId=&source=false&splitType=single&startDate=&title=&units=false&useCustomColors=false&useEstimates=false&zoom=1&redesign=true&chartCreator=&maxPoints=661'
    response = requests.get(URL, headers=yChartsHeaders).json()
    rawData = response['chart_data'][0][0]['raw_data']
    lastValue = rawData[len(rawData) - 1][1]
    previousValue = rawData[len(rawData) - 2][1]
    change = '{0:.2%}'.format((lastValue - previousValue) / previousValue)
    return "{:.2f}".format(lastValue), change


def getCnnFear():
    URL = 'https://production.dataviz.cnn.io/index/fearandgreed/graphdata'
    response = requests.get(URL, headers=yChartsHeaders).json()
    fearGreed = response['fear_and_greed']['score']
    rating = response['fear_and_greed']['rating']
    return fearGreed, rating


def getEconomicEvents2():
    returnArray = []
    binanceAPI = requests.get('https://api.binance.com/api/v3/ticker/24hr?symbols=["BTCUSDT","ETHUSDT","ADAUSDT","SOLUSDT","KDAUSDT","FLUXUSDT","BNBUSDT","NEARUSDT","AVAXUSDT"]')
    criptoData = binanceAPI.json()
    for crypto in criptoData:
                cryptoFormatted = {
                    'Symbol': crypto['symbol'].replace('USDT', ''),
                    'Price': '${:0,.2f}'.format(float(crypto['lastPrice'])),
                    'Change': '{:0,.2f}%'.format(float(crypto['priceChangePercent']))
                }
                returnArray.append(cryptoFormatted)
    reqKucoin = requests.get('https://api.kucoin.com/api/v1/market/stats?symbol=CRO-USDT')
    returnArray.append({
                    'Symbol': 'CRO',
                    'Price': '${:0,.3f}'.format(float(reqKucoin.json()['data']['last'])),
                    'Change': '{:0,.2f}%'.format(float(reqKucoin.json()['data']['changeRate']) * 100)
                    })

    dataframe = pd.DataFrame.from_records(returnArray)
    return dataframe


def getEconomicEvents():
    try:
        returnArray = []
        uri = 'http://investing.com/economic-calendar/'
        req = urllib.request.Request(uri)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36')
        result = ''
        response = urllib.request.urlopen(req)
        html = response.read()
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find('table', {"id": "economicCalendarData"})
        tbody = table.find('tbody')
        rows = tbody.findAll('tr', {"class": "js-event-item"})

        for tr in rows:
            _datetime = tr.attrs['data-event-datetime']
            
            time = arrow.get(_datetime, "YYYY/MM/DD HH:mm:ss").shift(hours=5).format("h:mm A")
            
            # print(time)
            cols = tr.find('td', {"class": "flagCur"})
            country = cols.text[-3:-1]

            impact = tr.find('td', {"class": "sentiment"})
            bull = impact.findAll('i', {"class": "grayFullBullishIcon"})
            impact = len(bull)

            event = tr.find('td', {"class": "event"})
            a = event.find('a')
            name = a.text.strip()

            fore = tr.find('td', {"class": "fore"})
            forecast = fore.text.strip()

            prev = tr.find('td', {"class": "prev"})
            previous = prev.text.strip()

            act = tr.find('td', {"class": "act"})
            actual = act.text.strip()
            if (country == 'US' and impact != 1) or ((country == 'EU' or country == 'GB' or country == 'JP') and impact == 3):
                returnArray.append({
                    'Country': country,
                    'Time': time,
                    'Name': name,
                    'Act.': actual,
                    'Est.': forecast,
                    'Prev.': previous
                })
    except HTTPError as error:
        print ("Oops... Get error HTTP {}".format(error.code))

    return pd.DataFrame.from_records(returnArray)
    


def millify(n):
    millnames = ['$',' K$',' M$',' B$',' T$']
    n = float(n)
    millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
    text = '{:.0f}{}'.format(n / 10**(3 * millidx), millnames[millidx])

    return text.replace(' ', '')


if __name__ == '__main__':
    #try:
        insertCharts()
        st_autorefresh(interval=50000, limit=100000, key="fizzzbuzzzcounter")
    #except:
    #    print('error')

        





