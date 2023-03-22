import streamlit as st
from streamlit_echarts import st_echarts
import datetime
import pandas as pd
import plotly.express as px
import requests
import plotly.graph_objects as go
import datetime

def setPageConfig(pageName='Dashboard'):
    st.set_page_config(
   page_title=pageName,
   page_icon="💰",
   layout="wide",
   initial_sidebar_state="collapsed",
)

    st.markdown(
        """
        <style>
        footer {background-color: rgb(0,0,0); display: none !important}
        [data-testid="stHeader"] { background-color: rgb(0,0,0); }
        .block-container {
            padding: 2rem 4rem 0rem;
            background-color: rgb(0,0,0)
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def createCanvaForTicker(tickerArray, symbol):
    try:
        index = [x for x in tickerArray if x["symbol"] == symbol ][0]
    except:
        index = {'symbol': '', 'price': 0, 'change': '0'}
    ticker = index['symbol'].replace("-YR", 'Y').replace(" ", "")
    price = '${:0,.2f}'.format(index['price'])
    if ticker == 'EUR' or ticker == 'AUD' or ticker == 'CAD' or ticker == 'GBP' or ticker == 'JPY':
        price = '${:0,.4f}'.format(index['price'])
    change = index['change']
    wch_colour_box = (25, 74, 25)
    if change != '':
        if float(change.replace('%', '')) < 0:
            wch_colour_box = (148, 25, 25)
        change = '{:0,.2f}%'.format(float(change.replace('%', '')))
    wch_colour_font = (255, 255, 255)

    return f"""<p style='background-color: rgb({wch_colour_box[0]}, 
                                                {wch_colour_box[1]}, 
                                                {wch_colour_box[2]}); 
                            color: rgb({wch_colour_font[0]}, 
                                    {wch_colour_font[1]}, 
                                    {wch_colour_font[2]}); 
                            font-family:Arial Rounded MT Bold;
                            font-size: 36px;
                            text-align: center;
                            border-radius: 30px; 
                            padding-top: 18px; 
                            padding-bottom: 18px; 
                            line-height:77px;'>
                            {ticker}&nbsp;&nbsp;{change}
                            </style><BR><span style='font-size: 35px; 
                            margin-top: 0;'>{price}</style></span></p>"""
                            

def createTable(dataframe, fontSize='25px', fontFamily='Arial Rounded MT Bold', width='481px', padding='1px 5px', coloring=True):
    hide_table_row_index = """
                        <style>
                        table {margin-top: -29rem; width: %s;}
                        thead tr th:first-child {display:none}
                        thead tr {border-top: none !important}
                        tbody th {display:none}
                        tbody tr {border-top: none !important}
                        </style>
                        """ % (width)

    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    th_props = [('font-size', fontSize),
    ('text-align', 'center'),
    ('border', '0 !important'),
    ('font-weight', 'bold'),
    ('color', 'rgb(255,255,255)')]
                                    
    td_props = [('font-size', fontSize),
    ('border', '0 !important'),
    ('font-weight', 'bold'),
    ('font-family', fontFamily), ('outline', 'none'), ('padding', padding)]
                                            
    styles = [dict(selector="th", props=th_props),
    dict(selector="td", props=td_props)]

    if coloring:
        df2=dataframe.style.set_properties(**{'text-align': 'center'}).set_table_styles(styles).apply(upOrDown,axis=1)
    else:
        df2=dataframe.style.set_properties(**{'text-align': 'center'}).set_table_styles(styles)
    st.write(df2.to_html(escape=False, index=False), unsafe_allow_html=True)


def createTableEconomicTable(dataframe, fontSize='25px', fontFamily='Arial Rounded MT Bold', width='481px', padding='1px 25px', coloring=True):
    hide_table_row_index = """
                        <style>
                        table {margin-top: -29rem; margin-left: -7rem; width: %s important;}
                        thead tr th:first-child {display:none}
                        thead tr {border-top: none !important}
                        tbody th {display:none}
                        tbody tr {border-top: none !important}
                        </style>
                        """ % (width)

    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    th_props = [('font-size', fontSize),
    ('text-align', 'center'),
    ('border', '0 !important'),
    ('font-weight', 'bold'),
    ('color', 'rgb(255,255,255)')]
                                    
    td_props = [('font-size', fontSize),
    ('border', '0 !important'),
    ('font-weight', 'bold'),
    ('font-family', fontFamily), ('outline', 'none'), ('padding', padding)]
                                            
    styles = [dict(selector="th", props=th_props),
    dict(selector="td", props=td_props)]

    if coloring:
        df2=dataframe.style.set_properties(**{'text-align': 'center'}).set_table_styles(styles).apply(upOrDown,axis=1)
    else:
        df2=dataframe.style.set_properties(**{'text-align': 'center'}).set_table_styles(styles)
    st.write(df2.to_html(escape=False, index=False), unsafe_allow_html=True)

def upOrDown(data, upColor='rgb(54,171,56)', downColor='rgb(200,14,14)'):
    colorGreen = f'color: {upColor}'
    colorRed = f'color: {downColor}'
    change = float(data['Change'].replace('%',''))
    colorToPaint = colorGreen if change > 0 else colorRed
    return ['', '', colorToPaint]


def getCNBCPrices(etf):
    try:
        if(etf['curmktstatus'] == 'POST_MKT' or etf['curmktstatus'] == 'PRE_MKT'):
            change = etf['ExtendedMktQuote']['change_pct']
            if change == "UNCH":
                change = "0.00%"
            return {'symbol': getTickerForName(etf['shortName'], etf['symbol']), 'price': float(etf['ExtendedMktQuote']['last'].replace(',','').replace("%", "")), 'change': change}
        else:
            change = etf['change_pct']
            if change == "UNCH":
                change = "0.00%"
            return {'symbol': getTickerForName(etf['shortName'], etf['symbol']), 'price': float(etf['last'].replace(',','').replace("%", "")), 'change': change}
    except:
        return {'symbol': '', 'price': 0, 'change': float('0.00')}

def getTickerForName(name, symbol):
    if name == 'GOLD':
        name = 'GC'
    if name == 'OIL':
        name = 'CL'
    if name == 'WHEAT':
        name = 'ZW'
    if name == 'CORN':
        name = 'ZC'
    if name == 'SOYBEAN':
        name = 'ZS'
    if name == 'CADUSD':
        name = 'CAD'
    if name =='S&P FUT':
        name = 'ES'
    if name == 'NAS FUT':
        name = 'NQ'
    if name == 'RUS2K FUT':
        name = 'RTY'
    if name == 'VIX Index':
        name = symbol.replace("@", "")
    if name == 'USD INDEX':
        name = symbol.replace(".", "")
    name = name.replace('/USD', '')
    name = name.replace('USD', '')
    return name
    

def rederGauge(text, value, format, min, max, split, lowerRange, higherRange, key):
    color = 'rgb(255, 152, 48)'
    if float(value) < lowerRange:
        color = 'rgb(115, 191, 105)'
    if float(value) > higherRange:
        color = 'rgb(255, 62, 62)'
    option = {
    'series': [{
      'type': 'gauge',
      'center': ['50%', '70%'],
      'startAngle': 180,
      'endAngle': 0,
      'min': min,
      'max': max,
      'splitNumber': split,
      'itemStyle': {'color': color},
      'progress': {'show': True,'width': 15},
      'pointer': {'show': False},
      'axisLine': {'lineStyle': {  'width': 15}},
      'axisTick': {'distance': -25,'splitNumber': 5,'lineStyle': {  'width': 1,  'color': '#999'}},
      'splitLine': {'distance': -32,'length': 14,'lineStyle': {  'width': 2,  'color': '#999'}},
      'axisLabel': {'distance': -18,'color': '#999','fontSize': 12},
      'anchor': {'show': False},
      'title': {'show': False},
      'detail': {'valueAnimation': True,'width': '100%','lineHeight': 15,'borderRadius': 8,'offsetCenter': [0, '-15%'],'fontSize': 24,'fontWeight': 'bolder','formatter': value + format,'color': color},
      'data': [{'value': value}
      ]}]
    }

    st_echarts(option, height="180px", width='210px', key=key, renderer='canva')
    return st.markdown(f"<p style='text-align: center; width:210px; margin-top: -65px'><span style='text-align: center; font-size: 20px; margin-top: 0;'>{text}</style></span>", unsafe_allow_html=True)


def getInlfuxQuery(query, cookie):
    seconds_since_epoch = datetime.datetime.now().timestamp()
    timeForQuery = round((seconds_since_epoch * 1000) - 18000 * 1000)
    url = 'http://192.168.0.15:3000/api/datasources/proxy/1/query?db=influx&q=' + query + '%20%3E%3D%20' + str(timeForQuery) + 'ms&epoch=ms'
    response = requests.get(url, headers={'Cookie': cookie}).json()
    if 'results' in response.keys():
        value = response['results'][0]['series'][0]['values'][len(response['results'][0]['series'][0]['values']) - 1][1]
        if not value:
            value = response['results'][0]['series'][0]['values'][len(response['results'][0]['series'][0]['values']) - 2][1]
        return value
    else:
        return response

def loginGrafana():
    url = 'http://192.168.0.15:3000/login'
    response = requests.post(url, json={"user":"admin","password":"ËS´Q9H¿£'<xpóË@t;Õõ_"}).headers['Set-Cookie']
    return response

def getPrometheusQuery(query, cookie):
    endTime = datetime.datetime.now().timestamp()
    startTime = endTime - 18000
    url = 'http://192.168.0.15:9090/api/v1/query_range?query=' + query + '&start=' + str(startTime) + '&end=' + str(endTime) + '&step=14'
    response = requests.get(url, headers={'Cookie': cookie}).json()
    value = response['data']['result'][0]['values'] [len(response['data']['result'][0]['values']) - 1][1]
    if not value:
        value = response['data']['result'][0]['values'] [len(response['data']['result'][0]['values']) - 2][1]
    return float(value)


def createWattSpan(value, text):
    color = 'rgb(115, 191, 105)'
    if float(value) < 0:
        color = 'rgb(115, 191, 105)'
    if float(value) > 0:
        color = 'rgb(255, 62, 62)'
    value = '{:0,.0f} W'.format(float(value))
    st.markdown(f"<p style='text-align: center; font-famlily: Arial Rounded MT Bold'><span style='font-size: 18px'>{text}</style></span><br><span style='font-size: 36px; color: {color}'>{value}</span></p>", unsafe_allow_html=True)
    

def rederAreaChart(cookie):
    dfSheely1 = getArraysForAreaChart('selly1_power', cookie)
    dfSheely2 = getArraysForAreaChart('selly2_power', cookie)
    dfSheely1['Value2'] = dfSheely2['Value'].to_numpy()
    dfSheely1.rename(columns = {'Value':'Production', 'Value2':'Consumption'}, inplace=True)
    fig = go.Figure(layout=dict(width=877, height=330))
    fig.add_trace(go.Scatter(x=dfSheely1['Time'], y=dfSheely1['Consumption'], fillcolor='rgba(255, 62, 62, 0.5)', fill='tozeroy', mode='none', name='Consumption', showlegend=False))
    fig.add_trace(go.Scatter(x=dfSheely1['Time'], y=dfSheely1['Production'], fillcolor='rgb(115, 191, 105)', fill='tozeroy', mode='none', name='Production', showlegend=False))
    fig.update_layout(margin=dict(l=10, r=10, t=0, b=0), paper_bgcolor="rgb(0,0,0)", title_font_family='Arial Rounded MT Bold', plot_bgcolor="rgb(0,0,0)", font_color="rgb(255,255,255)", xaxis=dict(showgrid=False, linecolor="rgba(255,255,255, 0.5)", showline=True, tickfont = dict(size=14)), yaxis=dict(showgrid=True, showline=True, linecolor="rgba(255,255,255, 0.5)", gridcolor="rgba(255,255,255, 0.2)", tickfont = dict(size=14)), font_family="Arial Rounded MT Bold", yaxis_title=None, xaxis_title=None, xaxis_tickformat = '%Hh %d-%b', title_font_size=25)
    st.plotly_chart(fig)


def createChart(dataf, title, width=640, height=449, titleColor="rgb(255,255,255)", titleFonteSize=25):
    dataf.reset_index(inplace=True)
    dataf = dataf.rename(columns = {'index':'timestamp'})
    dataf = dataf.rename(columns={'timestamp': 'time'})
    fig = px.line(dataf, x="time", y="close", title=title, width=width, height=height)
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=0), paper_bgcolor="rgb(0,0,0)", title_font_family='Arial Rounded MT Bold', plot_bgcolor="rgb(0,0,0)", font_color="rgb(255,255,255)", title_font_color=titleColor,  xaxis=dict(showgrid=False, linecolor="rgba(255,255,255, 0.5)", showline=True, tickfont = dict(size=14)), yaxis=dict(showgrid=True, showline=True, linecolor="rgba(255,255,255, 0.5)", gridcolor="rgba(255,255,255, 0.2)", tickfont = dict(size=14)), yaxis_tickformat = '$', font_family="Arial Rounded MT Bold", yaxis_title=None, xaxis_title=None, xaxis_tickformat = '%b-%Y', title_font_size=titleFonteSize, title={'text': title,'y':0.94,'x':0.5,'xanchor': 'center','yanchor': 'top'})
    fig.data[0].line.color = "#d76c21"
    fig.data[0].line.width = 2
    st.plotly_chart(fig)


def createChartEconomy(dataf, title, width=640, height=449, titleColor="rgb(255,255,255)", titleFonteSize=25, yFormat='$'):
    fig = px.line(dataf, x="time", y="close", title=title, width=width, height=height)
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=0), paper_bgcolor="rgb(0,0,0)", title_font_family='Arial Rounded MT Bold', plot_bgcolor="rgb(0,0,0)", font_color="rgb(255,255,255)", title_font_color=titleColor,  xaxis=dict(showgrid=False, linecolor="rgba(255,255,255, 0.5)", showline=True, tickfont = dict(size=14)), yaxis=dict(showgrid=True, showline=True, linecolor="rgba(255,255,255, 0.5)", gridcolor="rgba(255,255,255, 0.2)", tickfont = dict(size=14)), yaxis_tickformat = yFormat, font_family="Arial Rounded MT Bold", yaxis_title=None, xaxis_title=None, xaxis_tickformat = '%b-%Y', title_font_size=titleFonteSize, title={'text': title,'y':0.94,'x':0.5,'xanchor': 'center','yanchor': 'top'})
    fig.data[0].line.color = "#d76c21"
    fig.data[0].line.width = 2
    st.plotly_chart(fig)


def createChartEconomy2(dataf, title, width=640, height=449, titleColor="rgb(255,255,255)", titleFonteSize=25, yFormat='$'):
    fig = px.line(dataf, x="time", y=['close_x', 'close_y'], title=title, width=width, height=height)
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=0), paper_bgcolor="rgb(0,0,0)", title_font_family='Arial Rounded MT Bold', plot_bgcolor="rgb(0,0,0)", font_color="rgb(255,255,255)", title_font_color=titleColor,  xaxis=dict(showgrid=False, linecolor="rgba(255,255,255, 0.5)", showline=True, tickfont = dict(size=14)), yaxis=dict(showgrid=True, showline=True, linecolor="rgba(255,255,255, 0.5)", gridcolor="rgba(255,255,255, 0.2)", tickfont = dict(size=14)), yaxis_tickformat = yFormat, font_family="Arial Rounded MT Bold", yaxis_title=None, xaxis_title=None, xaxis_tickformat = '%b-%Y', title_font_size=titleFonteSize, title={'text': title,'y':0.94,'x':0.5,'xanchor': 'center','yanchor': 'top'})
    fig.data[0].line.color = "#d76c21"
    fig.data[0].line.width = 2
    st.plotly_chart(fig)


def getArraysForAreaChart(query, cookie):
    seconds_since_epoch = datetime.datetime.now().timestamp()
    startTime = (seconds_since_epoch) - 660000
    endTime = startTime + 660000
    url = 'http://192.168.0.15:9090/api/v1/query_range?query=' + query + '&start=' + str(startTime) + '&end=' + str(endTime) + '&step=60'
    response = requests.get(url, headers={'Cookie': cookie}).json()
    valuesShelly1 = response['data']['result'][0]['values']
    df = pd.DataFrame(data=valuesShelly1, columns=['Time', 'Value'])
    df['Time'] = df['Time'].apply(lambda x :datetime.datetime.fromtimestamp(x))
    df['Value'] = df['Value'].apply(lambda x :float(x))
    return df

def getTempColor(temp):
    color = 'rgb(34 112 245)'
    if temp > 7:
        color = '#ffc624' 
    if temp > 25:
        color = 'rgb(255 95 36)'
    return color


def time_in_range():
    start = datetime.time(14, 0, 0)
    end = datetime.time(21, 0, 0)
    current = datetime.datetime.now().time()
    return start <= current <= end


def rederGaugeFear(text, value, format, min, max, split, key):
    color = 'rgb(255, 152, 48)'
    if float(value) < 25:
        color = '#ff0000'
    if float(value) > 25 and float(value) < 45:
        color = 'rgb(255, 62, 62)'
    if float(value) > 45 and float(value) < 55:
        color = '#ffc624'
    if float(value) > 55 and float(value) < 75:
        color = 'rgb(115, 191, 105)'
    if float(value) > 75:
        color = 'rgb(9, 171, 59)'
    option = {
    'series': [{
      'type': 'gauge',
      'center': ['50%', '70%'],
      'startAngle': 180,
      'endAngle': 0,
      'min': min,
      'max': max,
      'splitNumber': split,
      'itemStyle': {'color': color},
      'progress': {'show': True,'width': 15},
      'pointer': {'show': False},
      'axisLine': {'lineStyle': {  'width': 15}},
      'axisTick': {'distance': -25,'splitNumber': 5,'lineStyle': {  'width': 1,  'color': '#999'}},
      'splitLine': {'distance': -32,'length': 14,'lineStyle': {  'width': 2,  'color': '#999'}},
      'axisLabel': {'distance': -18,'color': '#999','fontSize': 12},
      'anchor': {'show': False},
      'title': {'show': False},
      'detail': {'valueAnimation': True,'width': '100%','lineHeight': 15,'borderRadius': 8,'offsetCenter': [0, '-15%'],'fontSize': 24,'fontWeight': 'bolder','formatter': value + format,'color': color},
      'data': [{'value': value}
      ]}]
    }

    st_echarts(option, height="180px", width='210px', key=key, renderer='canva')
    return st.markdown(f"<p style='text-align: center; width:210px; margin-top: -65px;'><span style='text-align: center; font-size: 20px; margin-top: 0;'>{text}</style></span>", unsafe_allow_html=True)
