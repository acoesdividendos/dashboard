
import urllib.request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import re
import datetime

try:
    returnArray = []
    uri = 'https://www.investing.com/earnings-calendar/'
    req = urllib.request.Request(uri)
    req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36')
    result = ''
    response = urllib.request.urlopen(req)
    html = response.read()
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find('table', {"id": "earningsCalendarData"})
    tbody = table.find('tbody')
    rows = tbody.findAll('tr')
    today = datetime.datetime.now().strftime("%A, %B %d, %Y").replace(' 0', ' ')

    for tr in rows:
        if "theDay" in str(tr):
            date = tr.text.strip()
        
        if "theDay" not in str(tr):
            company = tr.find('td', {"class": "earnCalCompany"})
            a = company.find('a')
            ticker = a.text.strip()
            span = company.find('span')
            name = span.text.strip()

            act = tr.find('td', {"class": re.compile(r'eps_actual')})
            actual = act.text.strip()

            fore = tr.find_all('td', {"class": "leftStrong"})[0]
            forecast = fore.text.replace("/", '').strip()

            revAct = tr.find('td', {"class": re.compile(r'rev_actual')})
            revActual = revAct.text.strip()

            revFore = tr.find_all('td', {"class": "leftStrong"})[1]
            revForecast = revFore.text.replace("/", '').strip()

            mktCap = tr.find('td', {"class": "right"})
            marketCap = mktCap.text.strip()

            time = tr.find('td', {"class": "time"})
            if 'After' in str(time):
                actTime = '🌙'
                readTime = 0
            if 'Before' in str(time):
                actTime = '☀'
                readTime = 1

            if date == today and 'B' in str(marketCap) and float(marketCap.replace('B', '')) > 5:
                returnArray.append({
                    'Name': name,
                    'Ticker': ticker,
                    'Actual EPS': actual,
                    'Forecats EPS': forecast,
                    'Actual Revenue': revActual,
                    'Forecats Revenue': revForecast,
                    'Time': actTime,
                    'readTime': readTime
                })

    newlist = sorted(returnArray, key=lambda x: x["readTime"], reverse=True)
    for item in newlist:
        space = '\n **↳** '
        actTime = item['Time']
        ticker = item['Ticker']
        name = item['Name']
        actual = item['Actual EPS']
        forecast = item['Forecats EPS']
        revActual = item['Actual Revenue']
        revForecast = item['Forecats Revenue']
        result = result + '\n' + f'{actTime} {ticker} | {name}  {space} **Act. EPS {actual}** | Est. EPS {forecast} {space} **Act. Rev {revActual}** | Est. Rev {revForecast}'  + '\n'
    print(result)
except HTTPError as error:
    print ("Oops... Get error HTTP {}".format(error.code))