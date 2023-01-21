import streamlit as st
import pandas as pd
import requests
import datetime
import helper
import urllib
from fredapi import Fred
import numpy
import urllib.request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import arrow
from streamlit_autorefresh import st_autorefresh
fred = Fred(api_key='6d08d5b6749aad4b7ae0e4c1dcfca79c')


influxCoockie = '_pk_id.1.5336=ed6cf3ec48bfd1c5.1670520315.; _pk_ses.1.5336=1; grafana_session=a4bc6a97aadf000d67beb72c4f6063ec'
helper.setPageConfig()
col1, col2, col3, col4, col5, col6, col7, col8, col9= st.columns([4, 4, 4, 4, 4, 3, 3, 3, 3], gap='medium')
col10, col11, col12, col13 = st.columns([5, 5, 3, 2])


def getPricesForCanvas():
    tickerArray = []
    url = 'https://quote.cnbc.com/quote-html-webservice/restQuote/symbolType/symbol?symbols=SPY%7CQQQ%7CIWM%7CTLT%7C.VIX%7C@CL.1%7C@GC.1%7C@W.1%7C@S.1%7C@C.1%7CCADUSD=%7CJPYUSD=%7CGBP=%7CEUR=%7CAUD=%7CPLTR%7CAAPL%7CAMZN%7CGOOG%7CTSLA%7C.DXY%7C@VX.1%7C@VX.2%7C@VX.3%7CUS2Y%7CUS5Y%7CUS10Y%7CUS20Y%7C@W.1%7C@S.1%7C@C.1%7C@SP.1&requestMethod=itv&noform=1&partnerId=2&fund=1&exthrs=1&output=json&events=1'
    if not helper.time_in_range():
        url = 'https://quote.cnbc.com/quote-html-webservice/restQuote/symbolType/symbol?symbols=@SP.1%7C@ND.1%7C@TFS.1%7CTLT%7CSPY%7C.VIX%7C@CL.1%7C@GC.1%7C@W.1%7C@S.1%7C@C.1%7CCADUSD=%7CJPYUSD=%7CGBP=%7CEUR=%7CAUD=%7CPLTR%7CAAPL%7CAMZN%7CGOOG%7CTSLA%7C.DXY%7C@VX.1%7C@VX.2%7C@VX.3%7CUS2Y%7CUS5Y%7CUS10Y%7CUS20Y%7C@W.1%7C@S.1%7C@C.1&requestMethod=itv&noform=1&partnerId=2&fund=1&exthrs=1&output=json&events=1'
    request = requests.get(url)
    data = request.json()['FormattedQuoteResult']['FormattedQuote']
    for ticker in data:
        tickerFormatted = helper.getCNBCPrices(ticker)
        tickerArray.append(tickerFormatted)
    insertCanvasForTikers(tickerArray)


def clockAndWeather():
    fontSize = '27px'
    date_time = datetime.datetime.now().strftime("%d-%m %H:%M:%S")
    date,time = date_time.split()
    queryWeather = 'SELECT%20mean(%22temperature%22)%20FROM%20%22weather%22%20WHERE%20time'
    lastTemp = helper.getInlfuxQuery(queryWeather, influxCoockie)
    queryUpTime = 'node_time_seconds%7Binstance%3D%22node_exporter%3A9100%22%2Cjob%3D%22node_exporter%22%7D+-+node_boot_time_seconds%7Binstance%3D%22node_exporter%3A9100%22%2Cjob%3D%22node_exporter%22%7D'
    upTime = helper.getPrometheusQuery(queryUpTime, influxCoockie)
    upTime = '{:0,.2f} days'.format(float(upTime / 3600 / 24))
    runningContainersQuery = 'engine_daemon_container_states_containers%7Bstate%3D%7E%22running%22%7D'
    runningContainers = helper.getPrometheusQuery(runningContainersQuery, influxCoockie)
    stoppedContainersQuery = 'engine_daemon_container_states_containers%7Bstate%3D%7E%22stopped%22%7D'
    stoppedContainers = helper.getPrometheusQuery(stoppedContainersQuery, influxCoockie)
    color = helper.getTempColor(lastTemp)
    with col9:
        st.markdown(f"<p style='text-align: center; margin-top:40px; font-famlily: Arial Rounded MT Bold';><span style='font-size: {fontSize}; margin-top: 0;'>{time}</style></span><br><span style='text-align: center; font-size: {fontSize}; margin-top: 0;'>{date} | </style></span></style><span style='color: {color}; font-size: {fontSize}; margin-top: 0;'>{'{:0,.2f}°C'.format(lastTemp)}</style></span></p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-famlily: Arial Rounded MT Bold;'>Up Time</style></span><br><span style='font-size: {fontSize}; margin-top: 0;'>{upTime}</style></span></p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-famlily: Arial Rounded MT Bold;'><span style='font-size: 18px'>Stopped Contaienrs</style></span><br><span style='font-size: 36px; color: rgb(255, 62, 62)'>{int(stoppedContainers)}</span></p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-famlily: Arial Rounded MT Bold; margin-top:-15px'><span style='font-size: 18px'>Running Contaienrs</style></span><br><span style='font-size: 36px; color: rgb(115, 191, 105)'>{int(runningContainers)}</span></p>", unsafe_allow_html=True)


def insertGauges():
    try:
        with col6:
            queryCPUUsage = 'SELECT(%22usage_idle%22)%20FROM%20%22cpu%22%20WHERE%20(%22cpu%22%20%3D%20%27cpu-total%27)%20AND%20time'
            cpuUsage = helper.getInlfuxQuery(queryCPUUsage, influxCoockie) * -1 + 100
            queryCPUTemp = 'SELECT%20%22temp_input%22%20FROM%20%22sensors%22%20WHERE%20time'
            cpuTemp = helper.getInlfuxQuery(queryCPUTemp, influxCoockie)
            helper.rederGauge('CPU Usage','{:0,.2f}'.format(cpuUsage), '%', 0, 100, 10, 50, 80, 'cpu_usage')
            helper.rederGauge('CPU Temp','{:0,.2f}'.format(cpuTemp), '°C', 0, 110, 10, 50, 80, 'cpu_temp')
            helper.rederAreaChart(influxCoockie)
            helper.getArraysForAreaChart('selly1_power', influxCoockie)
        with col7:
            queryRAMUsage = 'SELECT%20%22used_percent%22%20FROM%20%22mem%22%20WHERE%20time'
            ramUsage = helper.getInlfuxQuery(queryRAMUsage, influxCoockie)
            queryDisksage = 'SELECT%20%22used_percent%22%20FROM%20%22disk%22%20WHERE%20time'
            diskUsage = helper.getInlfuxQuery(queryDisksage, influxCoockie)
            helper.rederGauge('RAM Usage','{:0,.2f}'.format(ramUsage), '%', 0, 100, 10, 50, 80, 'cpu_usage1')
            helper.rederGauge('Disk Used OS','{:0,.2f}'.format(diskUsage), '%', 0, 100, 10, 50, 80, 'cpu_usage4')
        with col8:
            sysLoadQuery = 'avg%28node_load15%7Binstance%3D%22node_exporter%3A9100%22%2Cjob%3D%22node_exporter%22%7D%29+%2F++count%28count%28node_cpu_seconds_total%7Binstance%3D%22node_exporter%3A9100%22%2Cjob%3D%22node_exporter%22%7D%29+by+%28cpu%29%29+*+100'
            sysLoad = helper.getPrometheusQuery(sysLoadQuery, influxCoockie)
            productionQuery = 'selly1_power'
            production = helper.getPrometheusQuery(productionQuery, influxCoockie)
            consumptionQuery = 'selly2_power'
            consumption = helper.getPrometheusQuery(consumptionQuery, influxCoockie)
            helper.rederGauge('Sys Load (15m avg)','{:0,.2f}'.format(sysLoad), '%', 0, 100, 10, 50, 80, 'cpu_usage3')
            helper.createWattSpan(production, 'Production')
            helper.createWattSpan(consumption, 'Consumption')
    except:
        next


def insertCanvasForTikers(tickerArray):
    try:
        fedFundRateValue = getFredDataHistory('DFF', 1)['close'][0]
    except:
        fedFundRateValue = 0
    fedFundRate = [{'symbol': 'FUND-RATE', 'price': fedFundRateValue, 'change': ''}]
    qqqTicker = 'QQQ'
    iwmTicker = 'IWM'
    if not helper.time_in_range():
        qqqTicker = 'NQ'
        iwmTicker = 'RTY'

    with col1:
        st.markdown(helper.createCanvaForTicker(tickerArray, 'ES'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'SPY'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'EUR'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'CL'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'PLTR'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'US 2-YR'), unsafe_allow_html=True)

    with col2:
        st.markdown(helper.createCanvaForTicker(tickerArray, qqqTicker), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'VIX'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'GBP'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'GC'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'AAPL'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'US 5-YR'), unsafe_allow_html=True)

    with col3:
        st.markdown(helper.createCanvaForTicker(tickerArray, iwmTicker), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'VX.1'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'CAD'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'ZW'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'AMZN'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'US 10-YR'), unsafe_allow_html=True)

    with col4:
        st.markdown(helper.createCanvaForTicker(tickerArray, 'TLT'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'VX.2'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'AUD'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'ZC'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'GOOG'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'US 20-YR'), unsafe_allow_html=True)

    with col5:
        st.markdown(helper.createCanvaForTicker(tickerArray, 'DXY'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'VX.3'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'JPY'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'ZS'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(tickerArray, 'TSLA'), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker(fedFundRate, 'FUND-RATE'), unsafe_allow_html=True)


def insertCryptoTable():
    with col13:
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
        helper.createTable(dataframe)


def getEconomicEvents():
    with col12:
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

        economicEvents = pd.DataFrame.from_records(returnArray)
        helper.createTableEconomicTable(economicEvents, '15px', 'Arial', '580px', '1px 1px', False)


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


if __name__ == '__main__':
    #try:
        clockAndWeather()
        getPricesForCanvas()
        getEconomicEvents()
        insertCryptoTable()
        insertGauges()
        st_autorefresh(interval=50000, limit=100000, key="fizzbuzzcounter")
    #except:
    #    print('error')

        





