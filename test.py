
import urllib.request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import re
import requests
import datetime
import time
import random as rd

def getEarnings():
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


#https://cmegroup-tools.quikstrike.net/User/QuikStrikeTools.aspx?viewitemid=IntegratedFedWatchTool&userId=lwolf&jobRole=&company=&companyType=&userId=lwolf&jobRole=&company=&companyType=
#https://cmegroup-tools.quikstrike.net/User/QuikStrikeView.aspx?viewitemid=IntegratedFedWatchTool&userId=lwolf&userId=lwolf&jobRole=&jobRole=&company=&company=&companyType=&companyType=&insid=83966474&qsid=b3a73a0e-8ad8-4c71-b5c5-7bad9e8cdb62

def getCMEData():
    s = requests.Session()
    r = s.get('https://cmegroup-tools.quikstrike.net/User/QuikStrikeView.aspx?viewitemid=IntegratedFedWatchTool&userId=lwolf&userId=lwolf&jobRole=&jobRole=&company=&company=&companyType=&companyType=&insid=83966474&qsid=b3a73a0e-8ad8-4c71-b5c5-7bad9e8cdb62')
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


def scrape(url):
    session=requests.Session()
    session.headers.update(
            {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 OPR/94.0.0.0'})
    time.sleep(rd.randint(0,10))
    r=session.get(url,params={"_": int(time.time()*1000)})
    soup2 = BeautifulSoup(r.content, "html.parser")
    form = soup2.find(id='cmeIframe-jtxelq2f')
    print(form)
    return r

scrape('https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html')
getCMEData()
