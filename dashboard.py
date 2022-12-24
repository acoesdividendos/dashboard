import streamlit as st
import pandas as pd
import requests
from webull import webull
import datetime
import helper
from streamlit_autorefresh import st_autorefresh


influxCoockie = '_pk_id.1.5336=b71512efe30a90c0.1671653720.; _pk_ses.1.5336=1; grafana_session=447786de724042161f11d364216bd5f8'
helper.setPageConfig()
wb = webull()
col1, col2, col3, col4, col5, col6, col7, col8, col9= st.columns([4, 4, 4, 4, 4, 3, 3, 3, 3], gap='medium')
col10, col11, col12, col13 = st.columns([3, 3, 3, 2])


def getPricesForCanvas():
    tickerArray = []
    url = 'https://quote.cnbc.com/quote-html-webservice/restQuote/symbolType/symbol?symbols=SPY%7CQQQ%7CIWM%7CTLT%7C.VIX%7C@CL.1%7C@GC.1%7C@W.1%7C@S.1%7C@C.1%7CCADUSD=%7CJPYUSD=%7CGBP=%7CEUR=%7CAUD=%7CPLTR%7CAAPL%7CAMZN%7CGOOG%7CTSLA&requestMethod=itv&noform=1&partnerId=2&fund=1&exthrs=1&output=json&events=1'
    if not helper.time_in_range():
        url = 'https://quote.cnbc.com/quote-html-webservice/restQuote/symbolType/symbol?symbols=@SP.1%7C@ND.1%7C@TFS.1%7CTLT%7C.VIX%7C@CL.1%7C@GC.1%7C@W.1%7C@S.1%7C@C.1%7CCADUSD=%7CJPYUSD=%7CGBP=%7CEUR=%7CAUD=%7CPLTR%7CAAPL%7CAMZN%7CGOOG%7CTSLA&requestMethod=itv&noform=1&partnerId=2&fund=1&exthrs=1&output=json&events=1'
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
    with col6:
        queryCPUUsage = 'SELECT(%22usage_idle%22)%20FROM%20%22cpu%22%20WHERE%20(%22cpu%22%20%3D%20%27cpu-total%27)%20AND%20time'
        cpuUsage = helper.getInlfuxQuery(queryCPUUsage, influxCoockie) * -1 + 100
        queryCPUTemp = 'SELECT%20%22temp_input%22%20FROM%20%22sensors%22%20WHERE%20time'
        cpuTemp = helper.getInlfuxQuery(queryCPUTemp, influxCoockie)
        helper.rederGauge('CPU Usage','{:0,.2f}'.format(cpuUsage), '%', 0, 100, 10, 50, 80, 'cpu_usage')
        helper.rederGauge('CPU Temp','{:0,.2f}'.format(cpuTemp), '°C', 0, 110, 10, 50, 80, 'cpu_temp')
        dataf =  wb.get_bars('SPY', None,'d1', 120, 1)
        helper.rederAreaChart(dataf, influxCoockie)
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


def insertCanvasForTikers(tickerArray):
    spyTicker = 'SPY'
    qqqTicker = 'QQQ'
    iwmTicker = 'IWM'
    if not helper.time_in_range():
        spyTicker = 'ES'
        qqqTicker = 'NQ'
        iwmTicker = 'RTY'

    with col1:
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == spyTicker ][0]), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == 'EUR' ][0]), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == 'CL' ][0]), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == 'PLTR' ][0]), unsafe_allow_html=True)

    with col2:
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == qqqTicker ][0]), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == 'GBP' ][0]), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == 'GC' ][0]), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == 'AAPL' ][0]), unsafe_allow_html=True)

    with col3:
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == iwmTicker ][0]), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == 'CAD' ][0]), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == 'ZW' ][0]), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == 'AMZN' ][0]), unsafe_allow_html=True)

    with col4:
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == 'TLT' ][0]), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == 'AUD' ][0]), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == 'ZC' ][0]), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == 'GOOG' ][0]), unsafe_allow_html=True)

    with col5:
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == 'VIX' ][0]), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == 'JPY' ][0]), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == 'ZS' ][0]), unsafe_allow_html=True)
        st.markdown(helper.createCanvaForTicker([x for x in tickerArray if x["symbol"] == 'TSLA' ][0]), unsafe_allow_html=True)


def insertCharts():
    with col10:
        dataf =  wb.get_bars('SPY', None,'d1', 120, 1)
        helper.createChart(dataf, 'SPY')

    with col11:
        dataf =  wb.get_bars('VIX', None,'d1', 120, 1)
        helper.createChart(dataf, 'VIX')

    with col12:
        columns = ['open_time','open', 'high', 'low', 'close', 'volume','close_time', 'qav','num_trades','taker_base_vol','taker_quote_vol', 'ignore']
        binanceAPI = requests.get('https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=170')
        bitcoinData = binanceAPI.json()
        bitcoindf = pd.DataFrame(bitcoinData, columns=columns, dtype=float)
        bitcoindf.index = [pd.to_datetime(x, unit='ms').strftime('%Y-%m-%d %H:%M:%S') for x in bitcoindf.open_time]
        helper.createChart(bitcoindf, 'BTC')


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


if __name__ == '__main__':
    #try:
        clockAndWeather()
        getPricesForCanvas()
        insertCryptoTable()
        insertCharts()
        insertGauges()
        st_autorefresh(interval=50000, limit=100000, key="fizzbuzzcounter")
    #except:
    #    print('error')

        





