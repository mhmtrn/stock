#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 13:30:20 2019

@author: mturan
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
import datetime
from datetime import date
from time import sleep


path = "/Users/mturan/Desktop/Scripts/stock_analysis"
# path = "/Users/mahmutturan/Desktop/Scripts/stock_analysis"

os.chdir(path)



"""
1) The paths above are different from where scripts are stored
because size of the data is too big to push to GIT

2) There are two different paths above since one is for personal pc,
the second one is business pc
"""


def get_stock_names():
    """
    - The purpose of this function is to
    extract all existing stock names as a list
    
    - Running the function is enough to scrap stock values from isyatirim.com
     
    - This function is mostly used under the other functions below
    
    """
    
    url = "https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/Tarihsel-Fiyat-Bilgileri.aspx"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    
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
            
    stocks_names = list(set(stocks))

    return stocks_names
    
   
def extract_stock_values(start_date: str, end_date: str, stocks_names: list):
    """
    The purpose is scrap values of the specified stock or stocks (should be type of list)
    
    Extract stock values based on:
    stocks whose named stated as a parameter (list form)
    between start_date and end_date
    """
    
    stocks_accumulated = []
    
    start_date = start_date
    end_date = end_date
        
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
        
    
    # convert frame and store in a list
    stocks_list = []
    for i in range(len(stocks_accumulated)):
        stocks_list.append(pd.DataFrame(stocks_accumulated[i]))
    # all stocks stored in an union frame
    stocks_frames = pd.concat(stocks_list)
    stocks_frames["HGDG_TARIH"] = pd.to_datetime(stocks_frames["HGDG_TARIH"],
                 format = "%d-%m-%Y")

    return stocks_frames


def all_stock_values(start_date = "01-01-1940"):
    """
    - The purpose is to scrap all stock values since the beginning.
    -- start_date parameter optinal and it is 01-01-1940 by default
       because there is no need for values before the date.
    
    - Extract all stock values as of stated date (or if not stated 01-01-1940)
    """
    
    today = date.today()
    new_end_date = today - datetime.timedelta(days=1)
    new_end_date = new_end_date.strftime("%d-%m-%Y")


    return extract_stock_values(start_date, new_end_date, get_stock_names())

    
def get_values_of_stock(stock_names: str, start_date = "01-01-1940"):
    """
    - The purpose is to get all stock values based on specified stock(s)
    -- Only difference from the function of "all_stock_values" is
       having stock_names. While the "all_stock_values" scrap all possible values
       for all possible stocks, this function is to scrap all possible values for
       only specified stock(s)
    """
    
    today = date.today()
    new_end_date = today - datetime.timedelta(days=1)
    new_end_date = new_end_date.strftime("%d-%m-%Y")


    return extract_stock_values(start_date, new_end_date, [stock_names])

        
def check_new_stocks():
    """
    - The purpose is to check if there is new stock.
    
    - Actual purpose of this function is to serve function of "update_stock_values"
    
    """
    stocks_new = []
    os.chdir(path)
    stocks = pd.read_pickle("stocks_values")
    for i in get_stock_names():
        if i not in list(set(stocks["HGDG_HS_KODU"])):
            stocks_new.append(i)      
            
    return stocks_new


def update_stock_values():
    """
    The purpose is to update stock values by
    - adding recent values
    - and adding new stocks (thanks to the function of "check_new_stocks")
    """
    os.chdir(path)
    stocks = pd.read_pickle("stocks_values")
    max_date = stocks["HGDG_TARIH"].max()
        # get recent date in existing stock values
    new_start_date = max_date + datetime.timedelta(days=1)
    
    # check whether new start date is today or not.
    today = datetime.datetime.today().strftime("%d-%m-%Y")
    new_start_date_check = new_start_date
    new_start_date_check = new_start_date_check.to_pydatetime().strftime("%d-%m-%Y")    
    if today == new_start_date_check:
        result = "please update tomorrow or later, existing values are already updated!"
    else: 
        new_start_date = new_start_date.strftime("%d-%m-%Y")
        # consider one day after as a new start date for scrapping
        new_values = all_stock_values(new_start_date)
        
        stocks = pd.concat([stocks, new_values])
        
        # it calls check_new_stocks function to check whether there is new stock or not
        new_buyers = check_new_stocks()
        if len(new_buyers) != 0:
            new_buyers_values = []
            for i in new_buyers:
                new_buyers_values.append(get_values_of_stock(str(i)))
            new_buyers_stock_values = pd.concat(new_buyers_values)
        
            stocks = pd.concat([stocks, new_buyers_stock_values])
        else:
            stocks = stocks
        
        result = stocks
    
    return result
    

def scrap_financials(period_1_year: int, period_1_month: int,
                     period_2_year: int, period_2_month: int,
                     period_3_year: int, period_3_month: int,
                     period_4_year: int, period_4_month: int):
    
    """
    get all financials for all stocks which are possible to extract
    from function of "get_stock_names" based on the terms stated
    """
    
    stocks_financials = []
    
    p1 = str(period_1_year) + "/" + str(period_1_month)
    p2 = str(period_2_year) + "/" + str(period_2_month)
    p3 = str(period_3_year) + "/" + str(period_3_month)
    p4 = str(period_4_year) + "/" + str(period_4_month)
    
    os.chdir("/Users/mturan/Desktop/Scripts/stock_analysis")
    
    stocks_remaining = get_stock_names()[:]
    for i in get_stock_names()[:]:
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
            
            if account.shape[0] > 0:
                account["stock_name"] = name
                stocks_financials.append(account)
    
        stocks_remaining.remove(name)
        
    stocks_financials = pd.concat(stocks_financials)
        
    return stocks_financials
       
    
def update_financials(year: int, month: int):
    """
    Purpose is to update existing fincnaials
    by adding newly announced ones
    
    The function check if the specified term is already exist
    - However, if the specified term exist for even one term,
      it brings "already exist". Dont forget!
      
    - Until finding an alternative way, wait for all financials be announced.
    """
    all_financials = pd.read_pickle("all_financials")
    
    term = str(year) + "/" + str(month)
    
    if term in list(all_financials):
        result = "already exist"
    else:
        stock_fs = scrap_financials(2016,12, 2017,12, 2018, 12, year, month)
        stock_fs.drop_duplicates(subset =["stock_name", 'account','account_eng'],
                        keep = "first", inplace = True)

        first_part = stock_fs.iloc[:,0:2]
        second_part = stock_fs.iloc[:,-2:]
        
        stock_fs = pd.concat([first_part, second_part], axis = 1)
        columns = ["stock_name", "account", "account_eng", list(stock_fs)[2]]
        
        stock_fs = stock_fs[columns]
        
        test_df = pd.merge(all_financials, stock_fs,  
                  how='left', on = ['stock_name', 'account','account_eng'])
 
        test_df.drop_duplicates(subset =["stock_name", 'account','account_eng'],
                                keep = "first", inplace = True)
        
        result = test_df
     
    return result
    
  
def get_stock_values_from_database(stock_name: "str"):
    """
    Purpose is to get values of specified stock from database
    instead of scrapping.
    Point is time efficiency
    """
    
    all_stock_value = pd.read_pickle("stocks_values")
    # all_stock_value = stocks
    stock = all_stock_value.loc[all_stock_value["HGDG_HS_KODU"] == stock_name]
    
    return stock


def get_stock_financials_from_database(stock_name: "str"):
    """
    Purpose is to get financials of specified stock from database
    instead of scrapping.
    Point is time efficiency
    """
    
    all_financials = pd.read_pickle("all_financials")
    stock = all_financials.loc[all_financials["stock_name"] == stock_name]
    
    return stock


# outdated
def clean_stock_raw_table(stock_name: str):
    """
    Purpose is to clean and prepared raw stock data for specified stock:
        - sort values by date
        - reset index
        - duplicate by dates (for certain period, there are two price in a day)
    """
    stock_values = get_stock_values_from_database(stock_name)
        # get stock values
    stock_values = stock_values.sort_values(by = "HGDG_TARIH")
        # sort by dates
    stock_values = stock_values[stock_values["HGDG_KAPANIS"] != 0]
        # drop zero columns (For some stocks -limited case-, there are zero days.)
    stock_values = stock_values.reset_index()
    del stock_values["index"]
    stock_values = stock_values.drop_duplicates(subset='HGDG_TARIH', keep="last")
        # drop duplicates (because of two closed in some dates)

    return stock_values


def values_all_stocks():
    """
    Purpose is to bring returns for all stocks in pviot format
    """
    all_stock_value = pd.read_pickle("stocks_values")
    stock_values = all_stock_value.sort_values(by = "HGDG_TARIH")
    stock_values = stock_values[stock_values["HGDG_KAPANIS"] != 0]
    stock_values = stock_values.reset_index()
    stock_values = stock_values[["HGDG_HS_KODU", "HGDG_TARIH", "HGDG_KAPANIS"]]
    stock_values = stock_values.drop_duplicates(subset=["HGDG_HS_KODU", 'HGDG_TARIH'], 
                                                keep="last")
    stock_values = stock_values.pivot(index="HGDG_TARIH",
                              columns = "HGDG_HS_KODU",
                              values = "HGDG_KAPANIS")
    return stock_values

"""
def returns(stock_name: str):
    ""
    Purpose is to calculate returns
    ""
    stock_values = clean_stock_raw_table(stock_name)
     
    returns = stock_values["HGDG_KAPANIS"].pct_change()
    dates = stock_values["HGDG_TARIH"]
    
    returns = pd.concat([dates, returns], axis = 1)

    return returns

"""



#############################################################################################################
############################################# BOOK VALUE ####################################################
#############################################################################################################

# This section to update for book values of stocks

def book_values(stock_name: str):
    """
    AMAÇ: Belirtilen hisse senedi için, her mali dönemin defter değerini (özkaynak) getirmek
    """
    bv = []
    for term in [3,6,9,12]:
        bv.append(get_financial_ratio([stock_name], term, "equity"))
    bv = pd.concat(bv)
    
    new = pd.DataFrame(bv.index.str.split('/',1).tolist(), columns = ['year','month'])
    bv = bv.reset_index(drop=True)
    bv = bv.join(new)
    bv['day'] = np.where(bv['month']=="3", 31, (np.where(bv['month']=="12", 31, 30)))
    
    bv["year"] = bv["year"].apply(int)
    bv["month"] = bv["month"].apply(int)
    df = pd.DataFrame(pd.to_datetime(pd.DataFrame({'year': bv["year"], 'month': bv["month"], 'day': bv["day"]})))
    bv = bv.join(df)
    
    bv["date"] = bv[0]
    bv = bv.drop(['year', 'month', "day", 0], axis=1)
    bv.index = bv["date"]
    bv["book_value"] = bv.iloc[:,0]
    bv = pd.DataFrame(bv.iloc[:,2])
    
    bv = bv.sort_index()
    bv["stock_name"] = stock_name
    bv = bv.reset_index()
    
    return bv


def day_table(frame_book_values):
    """
    Her mali dönemden bir sonraki mali döneme kadar kaç gün var.
    """
    fram = pd.DataFrame(frame_book_values["date"].diff())
    fram.columns = ["days"]
    fram = pd.DataFrame(fram["days"].shift(periods=-1))
    fram["date"] = frame_book_values["date"]
    fram.iloc[-1,0] = date.today() - pd.DataFrame(fram["date"]).iloc[-1,:][0].date()
    fram["days"] = pd.DataFrame(fram["days"].dt.days)
    
    return fram


def book_value_timeFrame(stock_name:str, frame_book_values, days):
    """
    AMAÇ: Belirtilen hisse senedinin defter değerini zaman serisi olarak oluşturmak.
    """
    frames = []
    for day, date, seq in zip(days["days"], days["date"], range(frame_book_values.shape[0])):
        ind = pd.date_range(date, periods = day, freq ='1d')
        df = pd.DataFrame(index = ind) 
        df["book_value"] = frame_book_values.iloc[seq,:][1]
        df["stock_name"] = frame_book_values.iloc[seq,:][2]
        frames.append(df)
    frames = pd.concat(frames)
    
    return frames


def book_valueFrame(stock_name:str, frame):
    
    stock_values = clean_stock_raw_table(stock_name)
    stock_values = stock_values[["HGDG_HS_KODU", "HGDG_TARIH", "PD"]]
    stock_values.index = stock_values.HGDG_TARIH
    stock_values.index.names = ['Date']
    del stock_values["HGDG_TARIH"]
    
    bookValues = frame.join(stock_values)
    bookValues = bookValues.dropna()
    
    bookValues = bookValues.rename(columns={"PD": "market_value"})
    bookValues["marketV_to_bookV"] = bookValues["market_value"] / bookValues["book_value"]
    
    del bookValues["HGDG_HS_KODU"]
    
    return bookValues


def update_market_value_frame():
    """
    Genel güncelleme için
    """
    frames = []
    stockNames = get_stock_names()
    for stock in stockNames:
        stock_name = stock
        try:
            frame_book_values = book_values(stock_name)
            days = day_table(frame_book_values)
            frame = book_value_timeFrame(stock_name, frame_book_values, days)
            final = book_valueFrame(stock_name, frame)
            frames.append(final)
        except:
            print(stock_name)
    frames = pd.concat(frames)
    
    return frames

# update_market_value_frame() yeterli -> kümüle güncelleme
# REFERENCE NOTEBOOK --> PD_DD.ipynb


def update_bookVal_Daily():
    from datetime import date
    marketValues = pd.read_pickle("marketValues")
    frames = []
    for stock in list(set(marketValues.stock_name)):
        frame = marketValues.loc[marketValues["stock_name"] == stock]
        diff = date.today() - frame.index[-1].date()
        diff = diff.days

        dates = []
        for i in range(diff):
            date = frame.index[-1].date() + datetime.timedelta(days=(i+1))
            dates.append(date)

        data = []
        for i in range(diff):
            data.append(frame.iloc[-1])
        data = pd.concat(data, axis=1)
        data = data.T

        ind = dates

        data["date"] = ind

        data = data.set_index('date')

        data.index.name = None
        data.index = pd.to_datetime(data.index, format = "%Y-%m-%d")

        frame_ = pd.concat([frame, data])
        frames.append(frame_)

    frames = pd.concat(frames)
    return frames

# This is for daily update


#############################################################################################################
#############################################################################################################
#############################################################################################################



def change_day_month(date_string):
    return date_string[3:5] + "-" + date_string[:2] + "-" + date_string[-4:]


def values_from_database():
    return pd.read_pickle("stocks_values_pivot")


def value_stock(stock_name, date_start, 
                end_date = datetime.datetime.today().strftime("%d-%m-%Y")):
    
    values = values_from_database()
    stock_values = pd.DataFrame(values[stock_name])
    stock_values.columns = ["HGDG_KAPANIS"]
    
    date_start = datetime.datetime.strptime(date_start, "%d-%m-%Y")
    
    end_date = change_day_month(end_date)

    values = stock_values.loc[(stock_values.index > date_start) &
                            (stock_values.index < end_date)]
    
    return values


def plot_value_stock(stock_name, date_start, 
                end_date = datetime.datetime.today().strftime("%d-%m-%Y")):
    
    values = value_stock(stock_name, date_start, end_date)
    
    return values["HGDG_KAPANIS"].plot(figsize=(20,5))


def value_drawdowns(stock_name: str, date_start, 
                end_date = datetime.datetime.today().strftime("%d-%m-%Y")):
    """
    Purpose is to create a dataframe showing drawdowns for values
    """
    
    values = value_stock(stock_name, date_start, end_date)
    values = values["HGDG_KAPANIS"]
    previous_peak = values.cummax()
    drawdowns = (values - previous_peak) / previous_peak
    
    frame = pd.DataFrame({
            "Wealth": values,
            "Peaks" : previous_peak, 
            "Drawdown": drawdowns    
            })

    return frame


def plot_value_drawdowns(stock_name: str, date_start: str,
                   end_date = datetime.datetime.today().strftime("%d-%m-%Y")):   
    """
    Purpose is to plot drawdowns for values
    """

    dd = value_drawdowns(stock_name, date_start, end_date)
    
    return dd[["Wealth", "Peaks"]].plot.line(figsize=(20,5)) 


def returns(stock_name: str):
    """
    Purpose is to calculate returns
    """
    values = values_from_database()
    
    stock_values = pd.DataFrame(values[stock_name])
    stock_values.columns = ["HGDG_KAPANIS"]
     
    returns = pd.DataFrame(stock_values["HGDG_KAPANIS"].pct_change())
    returns.reset_index(inplace = True)

    return returns



def returns_time_specified(stock_name: str, start_date: str, end_date: str):
    """
    Purpose is to calculat returns between specified dates
    """

    rets = returns(stock_name)
    
    date_start = datetime.datetime.strptime(start_date, "%d-%m-%Y")
    date_end = datetime.datetime.strptime(end_date, "%d-%m-%Y")
    
    returns_specified = rets.loc[(rets["HGDG_TARIH"] < date_end)
                            & (rets["HGDG_TARIH"] > date_start)]

    return returns_specified


def wealth_index(stock_name: str, date: str, 
                 end_date = datetime.datetime.today().strftime("%d-%m-%Y")):
    """
    Purpose is to calculate wealth index of specified stock as of stated datetime
    
    date is entered as string
    
    """    
    rets = returns(stock_name)
        # get all returns for specified stock with function returns
    
    date_start = datetime.datetime.strptime(date, "%d-%m-%Y")
        # convert "date" entered as string to datetime type
        
    end_date = datetime.datetime.strptime(end_date, "%d-%m-%Y")
        # convert "date" entered as string to datetime type
    
    rets = rets.loc[(rets["HGDG_TARIH"]> date_start) & (rets["HGDG_TARIH"]< end_date)]
    
    rets_columns = rets["HGDG_KAPANIS"]
    dates = rets["HGDG_TARIH"]
    
    wealth_index = 1 * (1 + (rets_columns)).cumprod()
    
    wealth_index = pd.concat([dates, wealth_index], axis = 1)
    
    wealth_index = pd.DataFrame({
            "Date": wealth_index["HGDG_TARIH"],
            "Wealth_Index": wealth_index["HGDG_KAPANIS"]  
            })

    return wealth_index


def plot_wealth_index(stock_name: str, date: str,
                      end_date = datetime.datetime.today().strftime("%d-%m-%Y")):
    """
    Purpose is to plot wealth index of specified stock as of stated datetime
    
    it depends on wealth_index function 
    """
    ret = wealth_index(stock_name, date, end_date)
    
    ret.index = ret["Date"]

    return ret["Wealth_Index"].plot(figsize=(20,5))


def compare_wealth_index(stock_1: str, stock_2: str, date: str,
                         end_date = datetime.datetime.today().strftime("%d-%m-%Y")):
    """
    Purpose is to bring a table to compare two specified stocks
    """
    s1 = wealth_index(stock_1, date, end_date)
    s2 = wealth_index(stock_2, date, end_date)
    
    comparison = s1.merge(s2, on = "Date", how = "left")
    
    frame = pd.DataFrame({
            "Date": comparison["Date"],
            str(stock_1): comparison["Wealth_Index_x"],
            str(stock_2): comparison["Wealth_Index_y"] 
            })
                
    return frame


def plot_compare_wealth_index(stock_1: str, stock_2: str, date: str,
                              end_date = datetime.datetime.today().strftime("%d-%m-%Y")):
    """
    Purpose is to plot comparison for wealth of two specified stocks
    """
    s1 = wealth_index(stock_1, date, end_date)
    s2 = wealth_index(stock_2, date, end_date)
    
    comparison = s1.merge(s2, on = "Date", how = "left")
    
    frame = pd.DataFrame({
            "Date": comparison["Date"],
            str(stock_1): comparison["Wealth_Index_x"],
            str(stock_2): comparison["Wealth_Index_y"] 
            })
                
    return frame[[str(stock_1), str(stock_2)]].plot.line(figsize=(20,5))


# example stocks = ["THYAO", "PGSUS", "TKFEN", "ASELS"]
def compare_wealths(stocks: list, date: str,
                    end_date = datetime.datetime.today().strftime("%d-%m-%Y")):
    """
    Purpose is to be able to compare specified stocks whose numbers are than 2
    """
    
    wealth_of_stocks = []
    for i in stocks:
        wealth_of_stocks.append(wealth_index(i, date, end_date))
        
    
    comparison = wealth_of_stocks[0].merge(wealth_of_stocks[1], 
                                 on = "Date", 
                                 how = "left")
    
    comparison = pd.DataFrame({
            "Date": comparison["Date"],
            str(stocks[0]): comparison["Wealth_Index_x"],
            str(stocks[1]): comparison["Wealth_Index_y"] 
            })
    
    for i in range(len(wealth_of_stocks)-2):
        comparison = comparison.merge(wealth_of_stocks[i+2], 
                                 on = "Date", 
                                 how = "left")
        
        columns1 = list(comparison)[:-1]
        columns2 = [stocks[i+2]]
        columns = columns1 + columns2
        comparison.columns = columns
        
    comparison.index = comparison["Date"]
        
    return comparison


def plot_compare_wealths(stocks: list, date: str,
                         end_date = datetime.datetime.today().strftime("%d-%m-%Y")):
    """
    Purpose is to be able to plot comparison of specifed stocks 
    whose numbers are than 2
    """
    
    plotting = compare_wealths(stocks, date, end_date)
    
    titles = []
    for i in range(len(list(plotting))-1):
        
        titles.append(list(plotting)[i+1])
    
    return plotting[titles].plot.line(figsize=(20,5)) 


def best_wealth_index(date: str,
                      end_date = datetime.datetime.today().strftime("%d-%m-%Y")):
    """
    purpose is to get best stocks as stated date in terms of wealth index
    """
    wealth_index_all_Stocks = []
    stock_names = []
    for i in get_stock_names():
        wealth_index_ = wealth_index(i, date, end_date)
        get_last_state_of_index = float(wealth_index_.iloc[-1,-1:])
        wealth_index_all_Stocks.append(get_last_state_of_index)
        stock_names.append(i)
        
    wealth_frame = pd.concat([pd.DataFrame(stock_names), pd.DataFrame(wealth_index_all_Stocks)], 
                              axis=1)
        
    columns = ["stock_name", "wealth"]
    wealth_frame.columns = columns
    wealth_frame = wealth_frame.sort_values(by = "wealth")    
    
    return wealth_frame


def drawdowns(stock_name: str, date: str):
    """
    Purpose is to create a dataframe showing drawdowns
    """
    
    wi = wealth_index(stock_name, date)
    date = wi["Date"]
    wi = wi["Wealth_Index"]
    previous_peak = wi.cummax()
    drawdowns = (wi - previous_peak) / previous_peak
    
    frame = pd.DataFrame({
            "date": date,
            "Wealth": wi,
            "Peaks" : previous_peak, 
            "Drawdown": drawdowns    
            })
                
    frame.index = frame["date"]
   
    return frame
    
    
def plot_drawdowns(stock_name: str, date: str,
                   end_date = datetime.datetime.today().strftime("%d-%m-%Y")):   
    """
    Purpose is to plot drawdowns
    """

    dd = drawdowns(stock_name, date)
    
    return dd[["Wealth", "Peaks"]].plot.line(figsize=(20,5)) 


def plot_drawdowns_details(stock_name: str, date: str):   
    """
    Purpose is to plot drawdowns
    """

    dd = drawdowns(stock_name, date)
    
    return dd[["Wealth", "Peaks", "Drawdown"]].plot.line(figsize=(20,5)) 


# bir önceki peak noktasının neresinde ve ne kadar uzağında hesaplat.
# finansallar ile anlamlandır, ve kısa ve orta vadeli en mantıklı hisseleri getir.

############################################################################################################
################################################# VOLUME ##################################################
############################################################################################################

def volumeTable():
    """
    Hacim tablosu oluşturmak için. UPDATE bölümü için.
    """
    all_stock_value = pd.read_pickle("stocks_values")
    all_stock_value = all_stock_value.sort_values(by=["HGDG_TARIH"])
    all_stock_value = all_stock_value.drop_duplicates(subset=["HGDG_HS_KODU", "HGDG_TARIH"], keep="last")
    all_stock_value = all_stock_value.reset_index(drop=True)
    all_stock_value = all_stock_value[["HGDG_TARIH", "HGDG_HS_KODU", "HGDG_HACIM"]]
    all_stock_value.index = all_stock_value.HGDG_TARIH
    all_stock_value = all_stock_value.drop(['HGDG_TARIH'], axis=1)
    
    return all_stock_value


def volume_table(stock_name, number_of_days):
    """
    hacim tablosu oluşturma
    """
    volume_frame = pd.read_pickle("volume_frame")
    volume_frame = volume_frame.loc[volume_frame["HGDG_HS_KODU"] == stock_name]
    
    SMAs = []
    for i in range(volume_frame.shape[0]):
        sma = volume_frame[["HGDG_HACIM"]][i:i+number_of_days].rolling(window=number_of_days).mean()
        sma = sma.iloc[-1,:]
        SMAs.append(sma)
    SMAs = pd.concat(SMAs, axis=1) 
    SMAs = SMAs.T
    SMAs = SMAs.dropna()

    SMAs = SMAs.rename(columns={"HGDG_HACIM": f"volume_ma_{number_of_days}"})
    
    volume_frame = volume_frame.join(SMAs)
    volume_frame = volume_frame.rename(columns={"HGDG_HACIM": "volume", "HGDG_HS_KODU": "stock_name"})
    
    return volume_frame

############################################################################################################
############################################### BULL & BEAR ################################################
############################################################################################################

def get_return(stock):
    stock_returns = returns(stock)
    stock_returns.index = stock_returns.HGDG_TARIH
    del stock_returns["HGDG_TARIH"]
    stock_returns = stock_returns.rename(columns = {'HGDG_KAPANIS':str(stock)})
    return stock_returns

def positive(value):
    return max(value, 0) # get positive values, otherwise zero

def negative(value):
    return min(value, 0) # get negative values, otherwise zero
    
def bear_bull_analysis():
    """
    Amaç her gün için artan hisselerin, düşen hisselere oranını çıkarmak. "market_positive" sütunu.
    UPDATE için
    """
    
    stockNames = get_stock_names()
    frame = get_return(stockNames[0])
    for stock in stockNames[1:]:
        stock_ret = get_return(stock)
        frame = frame.join(stock_ret)
             
    ratios = []
    for row in range(frame.shape[0]):
        observation = frame.iloc[row,:]
        observation = observation[~np.isnan(observation)]
        observation_pos = observation.map(positive)
        observation_neg = observation.map(negative)
        observation_pos = np.count_nonzero(observation_pos)
        observation_neg = np.count_nonzero(observation_neg)
        total = observation_pos + observation_neg
        if total == 0:
            positive_ratio = 0
        else:
            positive_ratio = observation_pos / total
        ratios.append(positive_ratio)
        
    frame["market_positive"] = ratios
    
    return frame


def positive_returns_ma(returnTable, number_of_days):
    """
    return table, positive ratio sütununa hareketli ortalama ekle.
    """
    SMAs = []
    for i in range(returnTable.shape[0]):
        sma = returnTable["market_positive"][i:i+number_of_days].rolling(window=number_of_days).mean()
        sma = sma.iloc[-1]
        SMAs.append(sma)

    reference_count = number_of_days-1
    SMAs = SMAs[:-reference_count]
    prepend = [0 for i in range(reference_count)]
    SMAs[:0] = prepend
    
    returnTable[f"market_positive_ma_{number_of_days}"] = SMAs
    
    return returnTable

############################################################################################################
############################################# MOVING AVERAGE ###############################################
############################################################################################################

# all_stock_value = pd.read_pickle("stocks_values_pivot")
def moving_average(all_stock_value, stock_name: str, number_of_days: int, start_date: str, end_date: str):
    """
    The function returns moving average for specified stock and specified number of days
    Args:
        - all_stock_value (frame) : This comes from pd.read_pickle("stocks_values_pivot")
        - stock_name (str)        : Stock name
        - number_of_days (int)    : Moving Average Day (e.g. 5, 20, 100, etc.)
        - start_date (str)        : Start Date
        - end_date (str)          : End Data
    Return:
        - frame indicating moving average results
    """
    
    date_start = datetime.datetime.strptime(start_date, "%d-%m-%Y") - datetime.timedelta(days=(number_of_days*2.2))
    end_date = datetime.datetime.strptime(end_date, "%d-%m-%Y")
    
    data = all_stock_value[[str(stock_name)]]
    
    data = data.loc[(data.index > date_start) & (data.index < end_date)]
    
    SMAs = []
    for i in range(data.shape[0]):
        sma = data[i:i+number_of_days].rolling(window=number_of_days).mean()
        sma = sma.iloc[-1,:]
        SMAs.append(sma)
    SMAs = pd.concat(SMAs, axis=1) 
    SMAs = SMAs.T
    SMAs = SMAs.dropna()
    
    return SMAs


def all_movingAverages(all_stock_value, stock_name: str, number_of_days: list, start_date: str, end_date: str):
    """
    The function returns moving average for specified stock and specified various days
    Args:
        - all_stock_value (frame) : This comes from pd.read_pickle("stocks_values_pivot")
        - stock_name (str)        : Stock name
        - number_of_days (list)   : Moving Average Day (e.g. [5], [20, 100], etc.)
        - start_date (str)        : Start Date
        - end_date (str)          : End Data
    Return:
        - frame indicating moving average results
    """
    MAs = [] 
    for days in number_of_days:
        MA = moving_average(all_stock_value, stock_name, days, start_date, end_date)
        MAs.append(MA)
    MAs = pd.concat(MAs, axis=1)
    
    titles = [("MA_" + str(i)) for i in number_of_days]
    MAs.columns = titles
    
    MAs = MAs.dropna()
    
    return MAs


def all_movingAverages_plot(all_stock_value, stock_name: str, number_of_days: list, start_date: str, end_date: str):
    """
    The function returns plotting of moving averages for specified stock and also specified various days
    Args:
        - all_stock_value (frame) : This comes from pd.read_pickle("stocks_values_pivot")
        - stock_name (str)        : Stock name
        - number_of_days (list)   : Moving Average Day (e.g. [5], [20, 100], etc.)
        - start_date (str)        : Start Date
        - end_date (str)          : End Data
    Return:
        - frame indicating moving average results
    """
    MAs = [] 
    for days in number_of_days:
        MA = moving_average(all_stock_value, stock_name, days, start_date, end_date)
        MAs.append(MA)
    MAs = pd.concat(MAs, axis=1)
    
    titles = [("MA_" + str(i)) for i in number_of_days]
    MAs.columns = titles
    
    titles = []
    for i in range(len(list(MAs))):
        titles.append(list(MAs)[i])
    
    return MAs[titles].plot.line(figsize=(30,7)) 


def moving_average_intersections(stock_name, start_date, end_date, moving_average_1, moving_average_2, another_ma):
    """
    The purpose is to get the points where moving average 1 intersect the second one below (buy),
        or above (sell)
    Args:
        stock_name (str)       : stock name (e.g. BIMAS, THYAO)
        start_date (str)       : start date (e.g. "11-01-2010")
        end_date (str)         : end date (e.g. "31-12-2019")
        moving_average_1 (int) : ma1 (e.g. 5, 10) it represents days
        moving_average_2 (int) : ma2 (e.g. 5, 10) it represents days
        
    """
    frame = all_movingAverages(values_from_database(), stock_name, [moving_average_1,
                                                                    moving_average_2,another_ma], start_date, end_date)
    frame["change"] = frame[f"MA_{moving_average_1}"] - frame[f"MA_{moving_average_2}"] 
    frame["new"] = frame["change"].shift(1)
    frame = frame.dropna()
    frame["test"] = frame["change"] * frame["new"]
    frame = frame.loc[frame["test"]<0]
    frame["status"] = frame["change"] * frame["test"]

    frame['suggestion'] = np.where(frame['status']<0, 'buy', 'sell')

    del frame["new"]
    del frame["test"]
    del frame["status"]
    del frame["change"]

    # frame["date"] = frame.index

    values = values_from_database()
    values = values[[str(stock_name)]]
    # values["date"] = values.index
    values = values.dropna()

    # frame = pd.merge(frame, values, on="date", how="left")
    frame = frame.join(values)
    
    return frame


############################################################################################################
################################################## RSI #####################################################
############################################################################################################


def gain_loss(stock_name, date_start, 
                end_date = datetime.datetime.today().strftime("%d-%m-%Y")):
    
    stock = value_stock(stock_name, date_start, end_date) # use this function to get values
    stock["Change"] = stock["HGDG_KAPANIS"].diff() # get difference on new column
    
    def positive(value):
        return max(value, 0) # get positive values, otherwise zero

    def negative(value):
        return min(value, 0) # get negative values, otherwise zero
    
    stock["Gain"] = stock["Change"].map(positive) # create a column for gains
    stock["Loss"] = stock["Change"].map(negative) # create a column for losses
    
    return stock


def RS(values, row, dayRSI):
    gainsAvg = values.iloc[row-dayRSI:row,:]["Gain"].sum() / dayRSI 
        # ilgili satırdaki değeri referans alarak, belirtilen gün kadar geriye giderek POZİTİF değerleri alıp ortalamasını alacak
    lossesAvg = abs(values.iloc[row-dayRSI:row,:]["Loss"].sum()) / dayRSI
        # ilgili satırdaki değeri referans alarak, belirtilen gün kadar geriye giderek NEGATİF değerleri alıp ortalamasını alacak
    
    try:
        RS = gainsAvg/lossesAvg
        # rs için pozitiflerin, negatife oranı.
    except ZeroDivisionError:
        RS = 0
   
    return RS  


def RSI(rs):
    return 100-(100/(1+rs))


def RS_series(values, dayRSI):
    series = []
    for row in range(values.shape[0]-dayRSI+1):
        reference_row = int(row + dayRSI)
        rs = RS(values, reference_row, dayRSI)
        series.append(rs)
        
    elements = [0] * (dayRSI-1)
    series = elements + series
    
    values["RS"] = series
    
    return values


def RSI_frame(values, dayRSI):
    values = RS_series(values, dayRSI)
    values["RSI"] = values["RS"].map(RSI)
    return values


def RSI_indicator(stock_name:str, dayRSI, date_start, end_date= datetime.datetime.today().strftime("%d-%m-%Y")):
    stock_values = gain_loss(stock_name, date_start, end_date)
    RSI = RSI_frame(stock_values, dayRSI)
    return RSI


def plot_RSI(stock_name:str, dayRSI, date_start, end_date= datetime.datetime.today().strftime("%d-%m-%Y")):
    RSI = RSI_indicator(stock_name, dayRSI, date_start, end_date)
    ax = RSI["RSI"].plot.line(figsize=(30,7))
    plt.axhline(30, color="gray")
    plt.axhline(70, color="gray")
    return ax


############################################################################################################
################################################ INDICATORS ################################################
############################################################################################################


def moving_average_trajectory(all_movingAverage, pct_change_day=5):  
    """
    Hesaplanan hareketli ortalama sütunları için, yönelim belirler.
    Her bir sütun için, ilgili satırdaki değeri belirtilen gün kadar önceki (varsayılan 5) değerle kıyaslar
    """
    multipliers = [i+1 for i in range(all_movingAverage.shape[1])]
    for mult, column in zip(multipliers, all_movingAverage.columns):
        all_movingAverage[f"{column}_CH"] = all_movingAverage[f"{column}"].pct_change(pct_change_day*mult)
        
    all_movingAverage = all_movingAverage.dropna()
        
    return all_movingAverage


def trajectory(frame, number_of_days):
    """
    moving_average_trajectory yerine BUNU KULLAN
    Hesaplanan hareketli ortalama sütunları için, yönelim belirler.
    Her bir sütun için, ilgili satırdaki değeri belirtilen gün kadar önceki (varsayılan 5) değerle kıyaslar
    """
    datas = []
    for column in list(frame):
        data = frame[[f"{column}"]]
        data[f"{column}_CH"] = data[f"{column}"].pct_change()
        data = data.dropna()

        SMAs = []
        for i in range(data.shape[0]):
            sma = data[i:i+number_of_days].rolling(window=number_of_days).mean()
            sma = sma.iloc[-1,:]
            SMAs.append(sma)
        SMAs = pd.concat(SMAs, axis=1) 
        SMAs = SMAs.T
        SMAs = SMAs.dropna()

        del SMAs[f"{column}"]
        del data[f"{column}_CH"]

        data = data.join(SMAs)
        data = data.dropna()

        datas.append(data)

    fram = datas[0]
    for count in range(len(list(datas))-1):
        fram = fram.join(datas[count+1])
        
    return fram


def momentum(frame, frame_column:str, momentum_day, mode="diff"):
    """
    Belirtilen frame ve belirtilen sütunu için, belirtilen gün kadar önceki değerleri ile kıyaslar
    """
    if mode == "diff":
        frame[f"{frame_column}_diff_{momentum_day}"] = frame[f"{frame_column}"].diff(momentum_day)
    elif mode == "pct_change":
        frame[f"{frame_column}_pct_change_{momentum_day}"] = frame[f"{frame_column}"].pct_change(momentum_day)
        
    frame = frame.dropna()
       
    return frame


def momentum_frame(frame, columns:list, momentum_day, mode="diff"):
    """
    Belirtilen frame ve belirtilen sütunları için, belirtilen gün kadar önceki değerleri ile kıyaslar
    momentum fonksiyonunu esas alarak çalışır
    """
    for frame_column in columns:
        frame = momentum(frame, frame_column, momentum_day, mode)
    frame = frame.dropna()
    return frame



def indicators(stock_name, MA_day1, MA_day2, MA_day3, start_date, end_date, RSI_day, trajectory_day):
    """
    Belirtilen hisse senedi için;
    - belirtilen günlerin hareketli ortalamalarını, 
    - hareketli ortamaların belirtilen trajectory değer kadar önceki günü esas alarak yönelimlerini,
    - RSI değerlerini (belirtilen RSI gün değeri esas alınarak)
    - Belirtilen tarihler esas alınarak Drawdown değerlerini
    """
    
    all_stock_value = values_from_database()
    
    # bring moving averages
    frame = all_movingAverages(all_stock_value, stock_name, [MA_day1, MA_day2, MA_day3], start_date, end_date)
    # calculate trajectories of moving average
    frame = moving_average_trajectory(frame, trajectory_day)
    
    # distance (%) between moving averages based on reference shortest period of days (e.g. 20, 50, 200 -> 20_200 and 20_50)
    frame[f"distance_{MA_day1}_{MA_day2}"] = (frame[f"MA_{MA_day1}"] - frame[f"MA_{MA_day2}"]) / frame[f"MA_{MA_day2}"]
    frame[f"distance_{MA_day1}_{MA_day3}"] = (frame[f"MA_{MA_day1}"] - frame[f"MA_{MA_day3}"]) / frame[f"MA_{MA_day3}"]
    
    # RSI
    RSI = RSI_indicator(stock_name, RSI_day, start_date, end_date)
    RSI = RSI[["RSI"]]
    frame = frame.join(RSI)
    
    # Drawdowns
    DD = drawdowns(stock_name, start_date)
    DD = DD[["Drawdown"]]
    frame = frame.join(DD)
    
    return frame


def indicators_with_buy_sell(stock_name, MA_day1, MA_day2, MA_day3, start_date, end_date, RSI_day, trajectory_day):
    """
    moving intersection ile indicator frame birleştirme
    """
    buy_sell = moving_average_intersections(stock_name, start_date, end_date,  MA_day1, MA_day2, MA_day3)
    frame = indicators(stock_name, MA_day1, MA_day2, MA_day3, start_date, end_date, RSI_day, trajectory_day)
    buy_sell.drop(buy_sell.columns[[0, 1, 2]], axis = 1, inplace = True)
    buy_sell = buy_sell.join(frame)
    return buy_sell


def simulation_only_buy_sell(frame):
    """
    buy_sell frame üzerinden (indicators_with_buy_sell), buy ve sell dikkate alınarak yapılabilecek kârı hesaplar.
    """
    frame = frame.iloc[:,:2]
    
    if frame.iloc[0,:][0] == "sell":
        frame = frame.iloc[1:,:]
    else:
        frame = frame

    if frame.iloc[-1,:][0] == "buy":
        frame = frame.iloc[:-1,:]
    else:
        frame = frame
    
    stock_name = str(list(frame)[1])
    m = 1
    for i in range(frame.shape[0]-2):
        m = m * (1+frame.iloc[i:i+2,:][stock_name].pct_change()[1])
        
    return m


def short_moving_average(frame, day):
    """
    Kısa hareketli ortalama hesaplamaları için.
    """
    SMAs = []
    for i in range(frame.shape[0]):
        sma = frame[i:i+day].rolling(window=day).mean()
        sma = sma.iloc[-1,:]
        SMAs.append(sma)
    SMAs = pd.concat(SMAs, axis=1) 
    SMAs = SMAs.T
    SMAs = SMAs.dropna()
    
    SMAs = SMAs.rename(columns={"RSI": f"RSI_{day}"})
    
    return SMAs


def whole_frame(stock_name:str, MA_days:list, start_date:str, end_date:str, RSI_day:int, trajectory_day:int):
    """
    THIS IS FINAL FRAME FOR INDICATOR
    trajectory için ve RSI için tarihleri (start_Date ve end_Date) RSI day ve trajectory day kadar gerie
    """
    all_stock_value = values_from_database()
    frame = all_movingAverages(all_stock_value, stock_name, MA_days, start_date, end_date)
    
    # frame = trajectory(frame, trajectory_day)
    
    ## kaldırmak için bundan sonraki 7 satırı kaldırabilirsin.
    # columns = [list(frame)[i] for i in range(frame.shape[1]) if i%2 != 0] # SADECE CH OLANLARI ALMAK İÇİN
    # new_frame = frame[columns]
    # new_frame = trajectory(new_frame, 7)  # son 7 gün MA_CH_CH değeri
    
    # columns = [list(frame)[i] for i in range(frame.shape[1]) if i%2 == 0] # SADECE CH OLANLARI ALMAK İÇİN
    # frame = frame[columns]
    # frame = frame.join(new_frame)
    # frame = frame.dropna()
    
    # RSI = RSI_indicator(stock_name, RSI_day, start_date, end_date)
    # RSI = RSI[["RSI"]]
    ## RSI'ın hareketli ortalamasını kaldırmak için devam eden 3 satırı kaldırmak yeterli olacaktır.
    # RSI_ma = short_moving_average(RSI, 5) # son 5 gün esas alınıyor.
    # RSI = RSI.join(RSI_ma)
    # RSI = RSI.dropna()
    ## trajectory. kaldırmak için bir sonraki satırın kaldırılması yeterli
    # RSI = trajectory(RSI, 7) # son 7 gün esas alınıyor.
    
    DD = drawdowns(stock_name, start_date)
    DD = DD[["Drawdown"]]
    
    # MV = get_market_values(stock_name, start_date)[["marketV_to_bookV"]]
    
    stock = value_stock(stock_name, start_date)
    stock["StockValue_momentum"] = ((stock["HGDG_KAPANIS"].pct_change(14))+1)*100 #-> momentum 14 alındı.
    
    # returnTable = pd.read_pickle("returnTable")
    # returnTable = positive_returns_ma(returnTable, 10) # son 10 gün positive artış oranlarının ortalaması
    # returnTable = returnTable.iloc[:,-2:]
    
    # volume_frame = volume_table(stock_name, 14) # son 14 gün positive artış oranlarının ortalaması
    
    # frame = frame.join(RSI)
    frame = frame.join(DD)
    # frame = frame.join(MV)
    frame = frame.join(stock)
    # frame = frame.join(returnTable)
    # frame = frame.join(volume_frame)
    frame = frame.rename(columns={"HGDG_KAPANIS": "StockValue"})

    
    return frame

############################################################################################################
####################################### FINANCIAL PERFORMANCE THRESHOLDS ###################################
############################################################################################################

def positive(value):
    return max(value, 0) # get positive values, otherwise zero


def negative(value):
    return min(value, 0) # get negative values, otherwise zero


def get_stock_ongoing_performance(ratio:str, term:int, num_last_year:int, how_many_years_before:int, mode=True):
    """
    Purpose is to find stocks showing desired performance for recent specified terms
    
    Args:
        ratio (str)           -> reference ratio or account (e.g. ebitda)
        term (int)            -> 3,6,9,12 (quarters or year ends)
        num_last_year (int)   -> how many recent terms to be considered
        mode (bool)           -> If TRUE, it brings all stocks; if FALSE, it brings only compatible ones
        how_many_years_before -> Kaç yıl öncesinden itibaren geriye bakmak istiyorsan (0 yazarsan 2019/12 dahil geriye gider, 1 yazarsan 2018/12, vs.)
    """
    stock_names = list(pd.read_pickle("financial_ratios_Summary_Table"))
    main_fs_frame = get_financial_ratio(stock_names, term, ratio)
    
    if how_many_years_before == 0:
        main_fs_frame = main_fs_frame
    else:
        main_fs_frame = main_fs_frame.iloc[:-how_many_years_before,:]
    
    print(f"Reference year to move back: {main_fs_frame.tail(1).index[0]}")
    
    stocks = []
    scores = []
    for stock in stock_names[:-3]: # son üç başlık hisse senedi ismi değil
        frame = pd.DataFrame(main_fs_frame[stock].pct_change())
        frame = frame.iloc[-num_last_year:,:]
        frame["positive"] = frame[stock].map(positive)
        frame = frame[["positive"]]
        frame = frame[(frame.T != 0).any()]
        score = frame.shape[0]
        scores.append(score)
        stocks.append(stock)
        
    final_frame = pd.DataFrame(list(zip(stocks, scores)), 
               columns =['stocks', 'scores'])
    final_frame = final_frame.sort_values(by=["scores"])
    
    if mode:
        final_frame = final_frame
    else:
        final_frame = final_frame.loc[final_frame["scores"] == num_last_year]
        
    final_frame = final_frame.reset_index(drop=True)

    return final_frame


def filter_financials(essential_ratios:list, term:int, num_last_year:int, how_many_years_before:int):
    """
    Multiple version of get_stock_ongoing_performance. You can use muliple ratio/account to filter.
    """
    frames = []
    for ratio in essential_ratios:
        frame = get_stock_ongoing_performance(ratio, term, num_last_year, how_many_years_before, mode=False)
        frame = set(frame["stocks"])
        frames.append(frame)
        
    finalStocks = set.intersection(*frames) # get intersection of all
    finalStocks = list(finalStocks)
    
    return finalStocks



############################################################################################################
####################################### ???????????????????????????????? ###################################
############################################################################################################

def get_market_values(stock_name: str, date_start: str, date_end=datetime.datetime.today().strftime("%d-%m-%Y")):
    """
    The purpose is return market value frame for specified stock and also for specified dates
    """
    
    marketValues = pd.read_pickle("marketValues")
    
    marketValues = marketValues.loc[marketValues["stock_name"] == stock_name]
    
    date_start = datetime.datetime.strptime(date_start, "%d-%m-%Y")
    date_end = datetime.datetime.strptime(date_end, "%d-%m-%Y")
    
    marketValues = marketValues.loc[(marketValues.index < date_end)
                            & (marketValues.index > date_start)]
    
    return marketValues


def market_value_specified_date(stock_name: str, date: str):
    """
    Belirtilen tarihteki piyasa değerini getirir.
    """
    market_value = get_market_values(stock_name, date)["market_value"][0]
    return market_value


def plot_market_values(stock_name: str, date_start: str, date_end=datetime.datetime.today().strftime("%d-%m-%Y")):
    """
    Plotting version of get_market_values
    """
    
    market_values = get_market_values(stock_name, date_start, date_end)
    
    return market_values["marketV_to_bookV"].plot(figsize=(30,7))


"""
VOLATILITY

BUNDAN SONRASI İÇİN TUTORIAL EKSİK
"""


def volatility(stock_name: str, start_date: str, end_date: str):
    """
    To calculate volatility based on daily returns
    """
    rets = returns_time_specified(stock_name, start_date, end_date)    
    volatility_ = rets.std()
    return volatility_[0]


def annualize_volatilityD(stock_name: str, start_date: str, end_date: str):
    """
    To annualize volatility based on daily returns
    """
    vol = volatility(stock_name, start_date, end_date)   
    annualized_volatility = vol * np.sqrt(252)    
    return annualized_volatility
    
    
def annualize_volatilityM(stock_name: str, start_date: str, end_date: str):
    """
    To annualize volatility based on monthly returns
    """
    vol = volatility(stock_name, start_date, end_date)    
    annualized_volatility = vol * np.sqrt(12)    
    return annualized_volatility
    
 
def annualize_volatilityW(stock_name: str, start_date: str, end_date: str):
    """
    To annualize volatility based on weekly returns
    """
    vol = volatility(stock_name, start_date, end_date)    
    annualized_volatility = vol * np.sqrt(52) 
    return annualized_volatility



def Annualized_volatility_stocks(start_date: str, end_date: str):
    """
    To calculate annualized volatility for all stocks
    """   
    volatilities = []
    stocks = []
    stock_names = get_stock_names()
    for i in stock_names:
        volatilities.append(annualize_volatilityD(i, start_date, end_date))
        stocks.append(i)
        
    volatility_table = pd.concat([pd.DataFrame(stocks), 
                                  pd.DataFrame(volatilities)], 
                    axis=1)
    
    volatility_table.columns = ["Stock_Name", "Annualized_Volatility"]
        
    return volatility_table
    
    
# stocks = ["THYAO", "PGSUS", "TKFEN"] 
def Annualized_volatility_stocks_specified(stocks: list, start_date: str, end_date: str):
    """
    To calculate annualized volatility for "specified" stocks
    """   
    volatilities = []
    stocks_ = []
    stock_names = stocks
    for i in stock_names:
        volatilities.append(annualize_volatilityD(i, start_date, end_date))
        stocks_.append(i)
        
    volatility_table = pd.concat([pd.DataFrame(stocks), 
                                  pd.DataFrame(volatilities)], 
                    axis=1)
        
    return volatility_table

  
############################################################################################################
############################################### ALTMAN SCORE ###############################################
############################################################################################################
    
def term_func(term:str):
    return f"{term}/12"


def term_date(term:str):
    return f"31-12-{term}"


def convert_Frame(serie):
    return pd.DataFrame(serie) 


def altman(stock_name, term="2019"):
    """
    Altman score hesaplamak için
    """
    term_ = term_func(term)
    termDate = term_date(term)
    
    A = ratio_calculation(stock_name, "WA_to_TotalAssets", "12")
    A = convert_Frame(A)
    A = A.loc[A.index == term_].iloc[0,0]
    
    B = ratio_calculation(stock_name, "RetainedEarnings_to_TotalAssets", "12")
    B = convert_Frame(B)
    B = B.loc[B.index == term_].iloc[0,0]
    
    C = ratio_calculation(stock_name, "ebit_TotalAssets", "12")
    C = convert_Frame(C)
    C = C.loc[C.index == term_].iloc[0,0]
    
    D_1 = market_value_specified_date(stock_name, termDate)
    D_2 = ratio_calculation(stock_name, "total_liabilities", "12")
    D_2 = convert_Frame(D_2)
    D_2 = D_2.loc[D_2.index == term_].iloc[0,0]
    D = D_1 / D_2
    
    E = ratio_calculation(stock_name, "sales_to_totalAssets", "12")
    E = convert_Frame(E)
    E = E.loc[E.index == term_].iloc[0,0]
    
    Altman_Z_Score = (1.2 * A) + (1.4 * B) + (3.3 * C) + (0.6 * D) + (1.0 * E)
    
    scores = {
        "WA_to_TotalAssets"              : A,
        "RetainedEarnings_to_TotalAssets": B, 
        "ebit_TotalAssets"               : C,
        "total_liabilities"              : D,
        "sales_to_totalAssets"           : E,
        "AltmanScore"                    : Altman_Z_Score
    }
    
    return scores



def altman_timeSeries(stock_name: str, start_year: int, end_year: int):
    """
    The function returns altman scores for specified stock between stattted start and end years.
    """
    terms = [year for year in range(start_year,end_year+1,1)]
    
    altmanScores = []
    for year in terms:
        altmanScores.append(altman(stock_name, term=str(year))["AltmanScore"])
        
    altmanScores = pd.DataFrame(list(zip(terms, altmanScores)), 
               columns =['Terms', 'AltmanScores'])
    
    altmanScores.index = altmanScores.Terms
    
    altmanScores = altmanScores.drop(['Terms'], axis=1)
    
    return altmanScores



def altman_Table(stockNames, start_year, end_year):
    """
    The funtion returns altman score table including the stocks stated for the specified start and end years.
    """
    series = []
    for stock_name in stockNames:
        serie = altman_timeSeries(stock_name, start_year, end_year)
        serie = serie.rename(columns = {"AltmanScores": stock_name})
        series.append(serie)
        
    series = pd.concat(series, axis=1)
    return series      

############################################################################################################
############################################### FINANCIALS #################################################
############################################################################################################

def financials_stock(stock_name: str, term = "all"):
    """
    The purpose is to bring financials of the stock specified
    if term = all, brings all financials
       term = 12, brings year end financials
       term = 9, brings q3 financials
       term = 6, brings q2 end financials
       term = 3, brings q1 end financials
    """    
    fin = pd.read_pickle("all_financials")   
    fin = fin.loc[fin["stock_name"] == stock_name]
    acc_tr = fin["account"]
    acc_en = fin["account_eng"]
    name = fin["stock_name"]
    
    if term == "all":
        fin = fin
    else:
        columns = [col for col in fin if col.endswith(term)]
        fin = fin[columns]
        fin.insert(loc=0, column='stock_name', value=name)
        fin.insert(loc=1, column='account', value=acc_tr)
        fin.insert(loc=2, column='account_eng', value=acc_en)
          
    fin.reset_index(inplace = True)
    del fin["index"]
        
    return fin


def plot_account_fs(stock_name: str, account_name: str, term = "all"):
    """
    Purpose is to plot specific account
    don't need to use! use plot ratios.
    """
    
    financials = financials_stock(stock_name, term)
    
    account = financials.loc[financials["account_eng"] == account_name]
    account = account.T
    account = account.iloc[3:,:]
    account.columns = [stock_name]
    
    return account.plot.bar(title = "Trend of " + str(account_name), figsize=(20,5))
     

def before_ratio_calculation(stock_name: str, term = "all"):
    """
    Purpose is to make frame ready for further calculations
    IMPORTANT NOTE: It only gets regular companies, not banks and the other FIs
    """
    fin = pd.read_pickle("all_financials")       
    fin = fin.loc[fin["stock_name"] == stock_name]
    acc_tr = fin["account"]
    acc_en = fin["account_eng"]
    name = fin["stock_name"]
    
    columns = [col for col in fin if col.endswith(term)]
    fin = fin[columns]
    fin.insert(loc=0, column='stock_name', value=name)
    fin.insert(loc=1, column='account', value=acc_tr)
    fin.insert(loc=2, column='account_eng', value=acc_en)
      
    fin.reset_index(inplace = True)
    del fin["index"]
    
    fin = fin.T
    fin = fin.iloc[2:,:]
    
    new_header = fin.iloc[0]
    fin = fin[1:]
    fin.columns = new_header
    
    return fin


ratio_list = ["turnover", 
              "total_assets", 
              "equity", 
              "gross_profit",
              "gross_profit_margin",
              "networth_base",
              "net_profit_margin",
              "net_profit",
              "ebitda",
              "ebitda_margin",
              "ebit",
              "ebit_margin",
              "net_debt",
              "netDebt_ebitda",
              "roe",
              "roa",
              "acid_test",
              "cash_ratio",
              "current_ratio",
              "asset_turnover",
              "debt_equity",
              "marketing_selling_general_to_gross",
              "working_capital",
              "WA_to_TotalAssets",
              "RetainedEarnings_to_TotalAssets",
              "ebit_TotalAssets",
              "sales_to_totalAssets",
              "total_liabilities"
             ] 
                # update it!

terms = [3,6,9,12]
    
def ratio_calculation(stock_name: str, ratio: str, term = "12"):
    """
    Purpose is to calculate ratios specified for specfied stocks in YEAR ENDS
        - turnover
        - total_assets
        - equity
        - gross_profit
        - gross_profit_margin
        - networth_base
        - net_profit_margin
        - net_profit
        - ebitda
        - ebitda_margin
        - ebit
        - ebit_margin
        - net_debt
        - netDebt_ebitda
        - roe
        - roa
        - acid_test
        - cash_ratio
        - current_ratio
        - asset_turnover
        - debt_equity
        - marketing_selling_general_to_gross
        - working_capital
        - WA_to_TotalAssets
        - RetainedEarnings_to_TotalAssets
        - ebit_TotalAssets
        - sales_to_totalAssets
        - total_liabilities

        
        HENÜZ İŞLENMEYENLER
        - fixed_asset_turnover
        - solvency_ratio
        - compound_annual_growth
        - free_cash
        - capex
        - dscr
        - interest_coverage
        - cash_cycle_conversion
        - dio
        - dso
        - dpo
    """
    fin = before_ratio_calculation(stock_name, term)
    fin = fin.fillna(0) # fill na with zero
    fin = fin[(fin.T != 0).any()] # remove zero rows (the years having no financials)

    
    if ratio == "turnover":
        fin["turnover"] = fin["Net Sales"]
    
    elif ratio == "marketing_selling_general_to_gross":
        fin["marketing_selling_general_to_gross"] = (-1*(fin["Marketing Selling & Distrib. Expenses (-)"] + fin["General Administrative Expenses (-)"])) / fin["GROSS PROFIT (LOSS)"]
    
    elif ratio == "total_assets":
        fin["total_assets"] = fin["TOTAL ASSETS"]
        
    elif ratio == "equity":
        fin["equity"] = fin["SHAREHOLDERS EQUITY"]

    elif ratio == "gross_profit":
        fin["gross_profit"] = fin["GROSS PROFIT (LOSS)"]

    elif ratio == "gross_profit_margin":
        fin["gross_profit_margin"] = fin["GROSS PROFIT (LOSS)"]  / fin["Net Sales"]
   
    elif ratio == "networth_base":
        fin["networth_base"] = fin["SHAREHOLDERS EQUITY"]  / fin["TOTAL ASSETS"]
        
    elif ratio == "net_profit_margin":
        fin["net_profit_margin"] = fin["NET PROFIT AFTER TAXES"]  / fin["Net Sales"]

    elif ratio == "net_profit":
        fin["net_profit"] = fin["NET PROFIT AFTER TAXES"]
        
    elif ratio == "ebitda":
        fin["ebitda"] = fin["Net Operating Profits"] + fin["Depreciation & Amortization"]
    
    elif ratio == "ebitda_margin":
        fin["ebitda"] = fin["Net Operating Profits"] + fin["Depreciation & Amortization"]
        fin["turnover"] = fin["Net Sales"]
        fin["ebitda_margin"] =  fin["ebitda"] / fin["Net Sales"]
    
    elif ratio == "ebit":
        fin["ebit"] = fin["Net Operating Profits"]
    
    elif ratio == "ebit_margin":
        fin["ebit_ratio"] = fin["Net Operating Profits"] / fin["Net Sales"]
    
    elif ratio == "net_debt":
        fin["net_debt"] = fin["Short-Term Financial Loans"] + fin["Other Short-Term Liabilities"] + fin["Long-Term Financial Loans"] + fin["Long-Term Loans from Financial Operations"] - fin["Cash\xa0and\xa0Cash\xa0Equivalents"]
        
    elif ratio == "netDebt_ebitda":
        fin["net_debt"] = fin["Short-Term Financial Loans"] + fin["Other Short-Term Liabilities"] + fin["Long-Term Financial Loans"] + fin["Long-Term Loans from Financial Operations"] - fin["Cash\xa0and\xa0Cash\xa0Equivalents"]
        fin["ebitda"] = fin["Net Operating Profits"] + fin["Depreciation & Amortization"]
        fin["netDebt_ebitda"] = fin["net_debt"] / fin["ebitda"]
    
    elif ratio == "roe":
        fin["roe"] = fin["NET PROFIT AFTER TAXES"] / fin["SHAREHOLDERS EQUITY"]
        
    elif ratio == "roa":
        fin["roa"] = fin["NET PROFIT AFTER TAXES"] / fin["TOTAL ASSETS"]

    elif ratio == "acid_test":
        fin["acid_test"] = (fin["Cash\xa0and\xa0Cash\xa0Equivalents"] + fin["Trade Receivables"] ) / fin["SHORT TERM LIABILITIES"]

    elif ratio == "cash_ratio":
        fin["cash_ratio"] = fin["Cash\xa0and\xa0Cash\xa0Equivalents"] / fin["SHORT TERM LIABILITIES"]

    elif ratio == "current_ratio":
        fin["current_ratio"] = fin["CURRENT ASSETS"] / fin["SHORT TERM LIABILITIES"]
        
    elif ratio == "asset_turnover":
        previous_asset_1 = fin['TOTAL ASSETS']
        
        t1 = previous_asset_1[1:]
        t1 = pd.DataFrame(t1)
        t1.reset_index(inplace=True)
        ind = t1["index"]
        t1 = t1["TOTAL ASSETS"]
        
        t2 = previous_asset_1[:-1]
        t2 = pd.DataFrame(t2)
        t2.reset_index(inplace=True)
        t2 = t2["TOTAL ASSETS"]
        
        average_asset = (t1 + t2) / 2
        average_asset = pd.concat([ind, average_asset], axis=1)
        average_asset = average_asset.set_index("index")
        
        total_sales = fin["Net Sales"][1:]
        
        asset_turnover = total_sales / average_asset["TOTAL ASSETS"]
        
        fin = pd.concat([fin, asset_turnover], axis=1)

        fin.rename(columns={ fin.columns[-1]: "asset_turnover" }, inplace = True)

    elif ratio == "debt_equity":
        fin["debt_equity"] = (fin['SHORT TERM LIABILITIES'] + fin["LONG TERM LIABILITIES"]) / fin["SHAREHOLDERS EQUITY"]
        
    elif ratio == "working_capital":
        fin["working_capital"] = fin["CURRENT ASSETS"] - fin["SHORT TERM LIABILITIES"]
        
    elif ratio == "WA_to_TotalAssets":
        fin["working_capital"] = fin["CURRENT ASSETS"] - fin["SHORT TERM LIABILITIES"]
        fin["WA_to_TotalAssets"] = fin["working_capital"] / fin["TOTAL ASSETS"]

    elif ratio == "RetainedEarnings_to_TotalAssets":
        fin["Retained_Earnings"] = fin["NET PROFIT AFTER TAXES"] - fin["Distrubition of Profit (Loss)"]
        fin["RetainedEarnings_to_TotalAssets"] = fin["Retained_Earnings"] / fin["TOTAL ASSETS"]
        
    elif ratio == "ebit_TotalAssets":
        fin["ebit_TotalAssets"] = fin["Net Operating Profits"] / fin["TOTAL ASSETS"]
 
    elif ratio == "sales_to_totalAssets":
        fin["sales_to_totalAssets"] = fin["Net Sales"] / fin["TOTAL ASSETS"]
    
    elif ratio == "total_liabilities":
        fin["total_liabilities"] = fin["SHORT TERM LIABILITIES"] + fin["LONG TERM LIABILITIES"]
        
    ratio = fin.iloc[:,-1]
    
    return ratio


def ratio_for_all_stocks(ratio: str, term = "12"):
    """
    The purpose is to get specified ratio for all stocks and for all specified terms
    """
     
    # get regular companies
    fin = pd.read_pickle("all_financials") 
    stock_types = pd.DataFrame(fin.stock_name.value_counts())
    stock_types["stock_names"] = stock_types.index
    stocks = list(stock_types.loc[stock_types["stock_name"] == 118]["stock_names"])
        # 118 will be changed in the future
    fin = fin[fin['stock_name'].isin(stocks)]
    stock_names = list(fin["stock_name"].unique())
    
    all_values = [] 
    
    for name in stock_names:
        all_values.append(ratio_calculation(name, ratio, term))
        
    all_stocks = pd.concat(all_values, axis = 1)
    all_stocks.columns = stock_names
    
    all_stocks = all_stocks.sort_index()
    
    return all_stocks
  
    
def create_finRatio_Table():
    """
    Purpose is to create summary financial ratio table
    """
    frames = []
    for ratio in ratio_list:
        for term in terms:
            frame = ratio_for_all_stocks(str(ratio), str(term))
            frame["ratio"] = ratio
            frame["term"] = term
            frame["year"] = frame.index.str[:4]
            frames.append(frame) 
    frames_final = pd.concat(frames)
    
    return frames_final


def plot_ratios(stock_name: str, ratio: str, term = "12"):
    """
    Purpose is to plot ratio for specified stock -> Instead use the function of "get_financial_ratio"
    """
    plotting = ratio_calculation(stock_name, ratio, term)
    plotting = pd.DataFrame(plotting)
    
    
    return plotting[ratio].plot.bar(title = stock_name, figsize=(20,5))


def plot_ratios_double(stock_name: str, ratio_1: str, ratio_2: str, term = "12"):
    """
    Purpose is to make comparison between ratios for specified stocks
    """
    plotting_1 = ratio_calculation(stock_name, ratio_1, term)
    plotting_1 = pd.DataFrame(plotting_1)
    
    plotting_2 = ratio_calculation(stock_name, ratio_2, term)
    plotting_2 = pd.DataFrame(plotting_2)

    plotting = pd.concat([plotting_1, plotting_2], axis = 1)
                     
    return plotting.plot.bar(title = stock_name, figsize=(20,5))


def get_financial_ratio(stock_names:list, term_type:int, ratio: str):
    """
    The purpose is to get ratio trend from the database for specified stock
    """
    fin_ratio_tables = pd.read_pickle("financial_ratios_Summary_Table")
    return fin_ratio_tables.loc[(fin_ratio_tables["ratio"]==str(ratio)) & (fin_ratio_tables["term"]==term_type)][stock_names]


def plot_financial_ratio(stock_names:list, term_type:int, ratio: str):
    """
    The purpose is to plot stated ratio trend from the database for specified stock
    """
    fin_ratio_tables = pd.read_pickle("financial_ratios_Summary_Table")
    result = fin_ratio_tables.loc[(fin_ratio_tables["ratio"]==str(ratio)) & (fin_ratio_tables["term"]==term_type)][stock_names]
    return result.plot.bar(figsize=(20,5))


['CURRENT ASSETS',
 'Cash\xa0and\xa0Cash\xa0Equivalents',
 'Short-Term Financial Investments',
 'Short-Term Trade Receivables',
 'Short-Term Receivables from Financial Operations',
 'Short-Term Other Receivables',
 0,
 'Inventories',
 'Short-Term Live Assets',
 'Other Current Assets',
 '  (Subtotal)',
 'Assets to be Sold',
 'LONG TERM ASSETS',
 'Trade Receivables',
 'Long-Term Receivables from Financial Operations',
 'Other Receivables',
 'Financial Investments',
 'Investments with Equity Method',
 'Long-Term Live Assets',
 'Real Estate Investments',
 'Stoklar',
 0,
 'Tangible Fixed Assets',
 'Goodwill',
 'Intangible Fixed Assets',
 'Long Term Deffered Tax Assets',
 'Other Long-Term Assets',
 'TOTAL ASSETS',
 'LIABILITIES',
 'SHORT TERM LIABILITIES',
 'Short-Term Financial Loans',
 'Other Short-Term Financial Liabilities',
 'Short-Term Trade Payables',
 'Other Short-Term Loans',
 0,
 'Short-Term Loans from Financial Operations',
 'Short-Term Government Promotions and Aids',
 0,
 'Taxation Liabilities on Income (-)',
 'Short-Term Provisions',
 'Other Short-Term Liabilities',
 'Liabilities on Assets to be Sold',
 'LONG TERM LIABILITIES',
 'Long-Term Financial Loans',
 'Long-Term Trade Payables',
 'Other Long-Term Loans',
 0,
 'Long-Term Loans from Financial Operations',
 'Long-Term Government Promotions and Aids',
 0,
 'Long-Term Provisions',
 'Provisions for Retirment Pay',
 'Deferred Tax Liabilities',
 'Other Long-Term Liabilities',
 'SHAREHOLDERS EQUITY',
 'Parent Shareholders Capital',
 'Share Capital',
 'Adjustments to Share Capital',
 'Premium\xa0in\xa0Excess\xa0of\xa0Par',
 'Market Value Surpluses',
 'FX Translation Differences ',
 'Income Reserves',
 'Retained Earnings /(Acc. Losses)',
 'Current Year Income /(Losses)',
 'Other Sholders Equity Items',
 'Minority Interests',
 'TOTAL LIABILITIES AND S.HOLDERS EQUITY',
 'Continuing Operations',
 'Net Sales',
 'Cost Of Sales',
 'Other Profit (Loss) from Trade Operations',
 'Gross Profit (Loss) from Trade Operations',
 'Proceeds from Interest, Fee, Premium, Commission and Other',
 'Expenses from Interest, Fee, Premium, Commission and Other',
 'Other Profit (Loss) from Financial Operations',
 'Gross Profit (Loss) from Financial Operations',
 'Other Income (Expenses)',
 'GROSS PROFIT (LOSS)',
 'Marketing Selling & Distrib. Expenses (-)',
 'General Administrative Expenses (-)',
 'Research & Development Expenses (-)',
 'Income from Other Operations',
 'Expenses from Other Operations (-)',
 'Other Income (Expenses) Before Operating Profits',
 'OPERATING PROFITS',
 'Net Operating Profits',
 0,
 0,
 0,
 'Profit (Loss) from Subsidiaries',
 0,
 'Financial Income (from Other Operations)',
 'Financial Expenses (from Other Operations) (-)',
 'Other Income (Expenses) Before Tax',
 'PROFIT BEFORE TAX FROM CONTINUING OPERATIONS ',
 'Taxation on Continuing Operations',
 '  Taxation on Income (Expenses)',
 '  Income (Expenses) of Deferred Tax',
 '  Other Taxation Income (Expenses)',
 'PROFIT FROM CONTINUING OPERATIONS ',
 'DISCONTINUED OPERATIONS ',
 'Profit After Taxes from Discontinued Operations',
 'NET PROFIT AFTER TAXES',
 'Distrubition of Profit (Loss)',
 'Minority Interests',
 'Parent Shares',
 'Earnings per Share',
 'Diluted Earnings per Share',
 'Earnings per Share from Continuing Operations ',
 'Earnings per Share from Discontinued Operations ',
 'Depreciation & Amortization',
 'Severance Payments',
 'Financial Expenses',
 'Domestic Sales',
 'Export Sales',
 'Net Fx Position',
 'Parasal net yabancı para varlık/(yükümlülük) pozisyonu',
 'Net YPP (Hedge Dahil)',
 'gross_profit_ratio']



"""
1- teknik analiz şekillerini yakalayan algoritma
2- portolio management
3- stratejilere uyarlanma
4- kısa vade ve uzun vade stratejileri

"""









