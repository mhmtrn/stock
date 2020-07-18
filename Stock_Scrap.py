# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import bs4
import requests
import urllib.request
import time
import numpy as np
from bs4 import BeautifulSoup
import lxml.html as lh
import re
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns

os.getcwd()
os.chdir("/Users/mturan/Desktop/Scripts/_StocksFinancials")
os.getcwd()



""" SCRAP ISYATIRIM'S PAGE OF TARIHSEL FIYAT BILGILERI (HISTORICAL PRICES)
    OF STOCKS"""
    
url = "https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/Tarihsel-Fiyat-Bilgileri.aspx"

response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

# soup.findAll('title=')


""" EXTRACT STOCK NAMES AS A LIST"""
    
lst = []
for i in range(len(soup.findAll('option'))):
    lst.append(soup.findAll('option')[i])


name_list = []
for i in range(len(soup.findAll('option'))):
    name_list.append(re.findall('".+?"',str(soup.findAll('option')[i])))

stock_names = []
for i in range(len(name_list)):
    try:
        stock_names.append(name_list[i][0][1:-1])
    except:
        pass

# ilgisiz olanları kaldır. uzunluk 4'ten küçük veya 5'ten büyükse.
stocks = []
for i in range(len(stock_names)):
    if len(stock_names[i]) <4 or len(stock_names[i]) > 5:
        continue
    else:
        stocks.append(stock_names[i])
  
      
# remove duplicates
len(stocks)
stocks = set(stocks)
stocks_names = list(stocks)
len(stocks_names)


""" 
TABLE SCRAP 

    extract stock prices in historical

"""
stocks_accumulated = []
counter = 0 
print("number of stocks : " + str(len(stocks)))

start_date = "01-01-2001"
end_date = "09-10-2019"

for i in stocks_names[:]:
    
    url = "https://www.isyatirim.com.tr/_layouts/15/Isyatirim.Website/Common/Data.aspx/HisseTekil?hisse=" + i + "&startdate=" + start_date + "&enddate=" + end_date
    
    Headers = {'Host': 'www.isyatirim.com.tr', 
           'Accept': '*/*', 
           'Connection': 'keep-alive', 
           'Accept-Language': 'en-us', 
           'Accept-Encoding': 'br, gzip, deflate', 
           'Cookie': '_ga=GA1.3.532701509.1566455787; _gat=1; _gid=GA1.3.2130997093.1567427056; TS01c8ca37=0157130bb9d25cf109d2172544ea2492aced148b417a0488f51cee8a38ed67c3073a9e0dab3d80a1b1168cf6cc03003d493edc4619c1bf1b58f6978d5989d6aeb9c3a099eaf4b3e0b1fd0d1547573b5f1d9c0970d1ec3ca543a52b87388040d889d444106a7ffc914d482b4bcf753d7a2131a4712c; mi=-2; u=a; BehaviorPad_Profile=ab342505-762b-4043-a59b-85dd4d32b86d; BIGipServer~P_ISYATIRIM~POOL-ISYATIRIM-HTTP=34031882.20480.0000',
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15',
           'Referer': 'https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/Tarihsel-Fiyat-Bilgileri.aspx',
           'X-Requested-With': 'XMLHttpRequest'}
    
    res = requests.get(url, headers = Headers)
    
    page = res.text
    
    decodedData = json.loads(page)
    
    stock_details = decodedData["value"]

    stocks_accumulated.append(stock_details)
    
    counter += 1
    print(counter)
        

""" 
BATCH AND STORE (PICKLE) 

    batch stock price as pickle

"""
  
# convert frame and store in a list
stocks_list = []

for i in range(len(stocks_accumulated)):
    stocks_list.append(pd.DataFrame(stocks_accumulated[i]))

# all stocks stored in an union frame
stocks_frames = pd.concat(stocks_list)

stocks_frames.to_pickle("stocks")

stocks = pd.read_pickle("stocks")



"""
Get financials of stocks
"""

# FINANCIALS MASS

stocks_financials = []

period_1_year = 2018
period_1_month = 12

period_2_year = 2017
period_2_month = 12

period_3_year = 2016
period_3_month = 12

period_4_year = 2015
period_4_month = 12


p1 = str(period_1_year) + "/" + str(period_1_month)
p2 = str(period_2_year) + "/" + str(period_2_month)
p3 = str(period_3_year) + "/" + str(period_3_month)
p4 = str(period_4_year) + "/" + str(period_4_month)

os.chdir("/Users/mturan/Desktop/Scripts/_StocksFinancials")

stocks_remaining = stocks_names[:]
for i in stocks_names[:]:
    name = str(i)
    
    url1 = "https://www.isyatirim.com.tr/_layouts/15/IsYatirim.Website/Common/Data.aspx/MaliTablo?companyCode=" + str(i) + "&exchange=TRY&financialGroup=XI_29&year1=" + str(period_1_year) + "&period1=" + str(period_1_month) + "&year2=" + str(period_2_year) + "&period2=" + str(period_2_month) + "&year3=" + str(period_3_year) + "&period3=" + str(period_3_month) + "&year4=" + str(period_4_year) + "&period4=" + str(period_4_month) + "&_=1570187610788"
    url2 = "https://www.isyatirim.com.tr/_layouts/15/IsYatirim.Website/Common/Data.aspx/MaliTablo?companyCode=" + str(i) + "&exchange=TRY&financialGroup=UFRS&year1="  + str(period_1_year) + "&period1=" + str(period_1_month) + "&year2=" + str(period_2_year) + "&period2=" + str(period_2_month) + "&year3=" + str(period_3_year) + "&period3=" + str(period_3_month) + "&year4=" + str(period_4_year) + "&period4=" + str(period_4_month) + "&_=1570199146767" \

    options = [url1, url2]
    
    for i in options:
        url = i
    
        Headers = {"Host": "www.isyatirim.com.tr",
                   "Accept": "*/*",
                   "Connection": "keep-alive",
                   "Accept-Language": "en-us",
                   "Accept-Encoding": "br, gzip, deflate",
                   "Cookie": "_ga=GA1.3.532701509.1566455787; _gid=GA1.3.366033970.1570178655; TS01c8ca37=0157130bb9e12efc5030f34306638932f8a8224690dd378e6bcadfa11a504b7ba19b4b992eba02d50b6d450bca5627eb0d585c27bec3b76281e47aa257fcd9ed7c33684f60649b295c72a77fd2f84abda66275484e4942a7b956de1a27fe6434c4f4d0b0c5515c2c13333fc4a9d26d70fba3fd1962; mi=-2; u=a; BehaviorPad_Profile=ab342505-762b-4043-a59b-85dd4d32b86d; BIGipServer~P_ISYATIRIM~POOL-ISYATIRIM-HTTP=34031882.20480.0000",
                   "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15",
                   "Referer": "https//www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/Sirket-Karti.aspx?hisse=" + str(i),
                   "X-Requested-With": "XMLHttpRequest"}
        
        
        
        res = requests.get(url, headers = Headers)
        
        page = res.text
        
        decodedData = json.loads(page)
        
        Tables = decodedData["value"]
        
        financials = []
        for i in Tables:
            financials.append(i.values())
            
        
        financials = list(financials)
        
        financials_ = []
        for i in financials:
            financials_.append(list(i)[1:])
            
        
        p1 = str(period_1_year) + "/" + str(period_1_month)
        p2 = str(period_2_year) + "/" + str(period_2_month)
        p3 = str(period_3_year) + "/" + str(period_3_month)
        p4 = str(period_4_year) + "/" + str(period_4_month)
        
        
        labels = ['account', 'account_eng', p1, p2, p3, p4]
        
        df = pd.DataFrame.from_records(financials_, columns=labels)  
        
        df = df.fillna(0)
        
        accounts = df.iloc[:,:2]
        accounts_values = df.iloc[:,2:].astype(str).astype(int)
        
        account = pd.concat([accounts, accounts_values], axis=1)
        
        os.chdir("/Users/mturan/Desktop/Scripts/_StocksFinancials")
        if account.shape[0] > 0:
            account["stock_name"] = name
            stocks_financials.append(account)
            writer = pd.ExcelWriter(str(name) + ".xlsx")
            account.to_excel(writer, "financials", index = False)
            writer.save()
        
    stocks_remaining.remove(name)
    
