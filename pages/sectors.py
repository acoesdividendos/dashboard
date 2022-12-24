import streamlit as st
from webull import webull
import helper
from streamlit_autorefresh import st_autorefresh


influxCoockie = '_pk_id.1.5336=b71512efe30a90c0.1671653720.; _pk_ses.1.5336=1; grafana_session=447786de724042161f11d364216bd5f8'
helper.setPageConfig('Sectors')
wb = webull()
col1, col2, col3, col4 = st.columns([3, 3, 3, 3], gap='medium')


def insertCharts():
    with col1:
        xopdata, xopTitle, xopColor =  getETFHistoryPrice('xop', 'Oil & Gas')
        helper.createChart(xopdata, xopTitle, 550, 300, xopColor, 20)
        tltdata, tltTitle, tltColor =  getETFHistoryPrice('tlt', 'TLT')
        helper.createChart(tltdata, tltTitle, 550, 300, tltColor, 20)
        xlidata, xliTitle, xliColor =  getETFHistoryPrice('xli', 'Industrial')
        helper.createChart(xlidata, xliTitle, 550, 300, xliColor, 20)
        xlpdata, xlpTitle, xlpColor =  getETFHistoryPrice('xlp', 'Consumer Staple')
        helper.createChart(xlpdata, xlpTitle, 550, 300, xlpColor, 20)

    with col2:
        glddata, gldTitle, gldColor =  getETFHistoryPrice('gld', 'Gold')
        helper.createChart(glddata, gldTitle, 550, 300, gldColor, 20)
        xledata, xleTitle, xleColor =  getETFHistoryPrice('xle', 'Energy')
        helper.createChart(xledata, xleTitle, 550, 300, xleColor, 20)
        xledata, xleTitle, xleColor =  getETFHistoryPrice('xlk', 'Technology')
        helper.createChart(xledata, xleTitle, 550, 300, xleColor, 20)
        xlydata, xlyTitle, xlyColor =  getETFHistoryPrice('xly', 'Consumer Discretionary')
        helper.createChart(xlydata, xlyTitle, 550, 300, xlyColor, 20)

    with col3:
        slvdata, slvTitle, slvColor =  getETFHistoryPrice('slv', 'Silver')
        helper.createChart(slvdata, slvTitle, 550, 300, slvColor, 20)
        xlfdata, xlfTitle, xlfColor =  getETFHistoryPrice('xlf', 'Financials')
        helper.createChart(xlfdata, xlfTitle, 550, 300, xlfColor, 20)
        xludata, xluTitle, xluColor =  getETFHistoryPrice('xlu', 'Utilities')
        helper.createChart(xludata, xluTitle, 550, 300, xluColor, 20)
        xlvdata, xlvTitle, xlvColor =  getETFHistoryPrice('xlv', 'Health Care')
        helper.createChart(xlvdata, xlvTitle, 550, 300, xlvColor, 20)

    with col4:
        vwodata, vwoTitle, vwoColor =  getETFHistoryPrice('vwo', 'Emerging Markets')
        helper.createChart(vwodata, vwoTitle, 550, 300, vwoColor, 20)
        xlcdata, xlcTitle, xlcColor =  getETFHistoryPrice('xlc', 'Communication')
        helper.createChart(xlcdata, xlcTitle, 550, 300, xlcColor, 20)
        xlredata, xlreTitle, xlreColor =  getETFHistoryPrice('xlre', 'Real Estate')
        helper.createChart(xlredata, xlreTitle, 550, 300, xlreColor, 20)
        xlbdata, xlbTitle, xlbColor =  getETFHistoryPrice('xlb', 'Materials')
        helper.createChart(xlbdata, xlbTitle, 550, 300, xlbColor, 20)


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




if __name__ == '__main__':
    #try:
        insertCharts()
        st_autorefresh(interval=50000, limit=100000, key="fizzzbuzzcounter")
    #except:
    #    print('error')

        





