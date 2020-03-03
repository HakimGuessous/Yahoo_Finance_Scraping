from datetime import datetime
import lxml
from lxml import html
import requests
import numpy as np
import pandas as pd
from selenium import webdriver
import time

russell = pd.read_csv('russell1000.csv')

def get_data(webpage):
    dfs_annual = html.fromstring(webpage.page_source)
    table_rows = dfs_annual.xpath("//div[contains(@class, 'D(tbr)')]")

    # Check some table rows are found
    assert len(table_rows) > 0

    parsed_rows = []

    for table_row in table_rows:
        parsed_row = []
        el = table_row.xpath("./div")

        none_count = 0

        for rs in el:
            try:
                (text,) = rs.xpath('.//span/text()[1]')
                parsed_row.append(text)
            except ValueError:
                parsed_row.append(np.NaN)
                none_count += 1

        if (none_count < 4):
            parsed_rows.append(parsed_row)

    df = pd.DataFrame(parsed_rows)

    return df


def scrape_symbol(symbol):
    # select chrome driver
    driver = webdriver.Chrome('C:/Users/HGuessous/Downloads/chromedriver_win32/chromedriver.exe')

    #URL to Yahoo Finance Financial - Balance Sheet
    url = 'https://finance.yahoo.com/quote/' + symbol + '/balance-sheet?p=' + symbol
    driver.get(url)

    #Wait one second and then click past user agreement
    time.sleep(3)
    try:
        driver.find_element_by_xpath("//button[text()='I agree']").click()
    except:
        try:
            driver.find_element_by_xpath("/html/body/div/div/div/form/div/button[2]").click()
        except:
            print("fail")

    #Scrape Balance Sheet
    time.sleep(3)
    try:
        annual_balance = get_data(driver)
        annual_balance.columns = annual_balance.iloc[0]
        annual_balance = annual_balance[1:]
        annual_balance = pd.melt(annual_balance, id_vars='Breakdown', var_name='Date')
        annual_balance['Symbol'] = symbol
        print(symbol + ": annual balance sheet")
    except:
        print(symbol +": Could not scrape annual balance sheet")



    #Navigate/scrape Income Statement
    driver.find_element_by_xpath("//span[text()='Income Statement']").click()
    time.sleep(3)
    try:
        annual_income = get_data(driver)
        annual_income.columns = annual_income.iloc[0]
        annual_income = annual_income[1:]
        annual_income = pd.melt(annual_income, id_vars='Breakdown', var_name='Date')
        annual_income['Symbol'] = symbol
        print(symbol + ": annual income statement")
    except:
        print(symbol + ": Could not scrape annual income statment")

    #Navigate/scrape Cash Flow
    driver.find_element_by_xpath("//span[text()='Cash Flow']").click()
    time.sleep(3)
    try:
        annual_cash = get_data(driver)
        annual_cash.columns = annual_cash.iloc[0]
        annual_cash = annual_cash[1:]
        annual_cash = pd.melt(annual_cash, id_vars='Breakdown', var_name='Date')
        annual_cash['Symbol'] = symbol
        print(symbol + ": annual cash flow")
    except:
        print(symbol + ": Could not scrape annual cash flow")



    #Navigate/scrape quarterly Income Statement
    driver.find_element_by_xpath("//span[text()='Income Statement']").click()
    time.sleep(3)
    driver.find_element_by_xpath("//span[text()='Quarterly']").click()
    time.sleep(3)
    try:
        quarterly_income = get_data(driver)
        quarterly_income.columns = quarterly_income.iloc[0]
        quarterly_income = quarterly_income[1:]
        quarterly_income = pd.melt(quarterly_income, id_vars='Breakdown', var_name='Date')
        quarterly_income['Symbol'] = symbol
        print(symbol + ": quarterly income statement")
    except:
        print(symbol + ": Could not scrape quarterly income statement")


    #Navigate/scrape quarterly Balance Sheet
    driver.find_element_by_xpath("//span[text()='Balance Sheet']").click()
    time.sleep(3)
    driver.find_element_by_xpath("//span[text()='Quarterly']").click()
    time.sleep(3)
    try:
        quarterly_balance = get_data(driver)
        quarterly_balance.columns = quarterly_balance.iloc[0]
        quarterly_balance = quarterly_balance[1:]
        quarterly_balance = pd.melt(quarterly_balance, id_vars='Breakdown', var_name='Date')
        quarterly_balance['Symbol'] = symbol
        print(symbol + ": quarterly balance sheet")
    except:
        print(symbol + ": Could not scrape quarterly balance sheet")


    #Navigate/scrape quarterly Cash Flow
    driver.find_element_by_xpath("//span[text()='Cash Flow']").click()
    time.sleep(3)
    driver.find_element_by_xpath("//span[text()='Quarterly']").click()
    time.sleep(3)
    try:
        quarterly_cash = get_data(driver)
        quarterly_cash.columns = quarterly_cash.iloc[0]
        quarterly_cash = quarterly_cash[1:]
        quarterly_cash = pd.melt(quarterly_cash, id_vars='Breakdown', var_name='Date')
        quarterly_cash['Symbol'] = symbol
        print(symbol + ": quarterly cash flow")
    except:
        print(symbol + ": Could not scrape quarterly cash flow")



    #Navigate/scrape Summary Page
    driver.find_element_by_xpath("//span[text()='Summary']").click()
    time.sleep(3)
    dfs_annual = html.fromstring(driver.page_source)

    summary = pd.DataFrame(columns=['Attribute', 'Value'])
    for j in range(1,3):
        for i in range(1,9):
            try: (Attribute,) = dfs_annual.xpath("//*[@id='quote-summary']/div[{}]/table/tbody/tr[{}]/td[1]/span[1]/text()".format(j,i))
            except:
                try: (Attribute,) = dfs_annual.xpath("//*[@id='quote-summary']/div[{}]/table/tbody/tr[{}]/td[1]/text()".format(j, i))
                except: "Fail 1"
            try: (Value,) = dfs_annual.xpath("//*[@id='quote-summary']/div[{}]/table/tbody/tr[{}]/td[2]/span[1]/text()".format(j,i))
            except:
                try: (Value,) = dfs_annual.xpath("//*[@id='quote-summary']/div[{}]/table/tbody/tr[{}]/td[2]/text()".format(j,i))
                except: "Fail 2"

            summary = summary.append({'Attribute': Attribute, 'Value':Value}, ignore_index=True)
    print(symbol + ": summary page")
    summary['Symbol'] = symbol

    driver.close()
    return annual_balance, annual_income, annual_cash, quarterly_balance, quarterly_income, quarterly_cash, summary

#list of tickers to pull financial data
tickers = russell.loc[0:50,'Symbol']


#create empty dataframes to store results
balance_an = pd.DataFrame()
income_an = pd.DataFrame()
cash_an = pd.DataFrame()
balance_qu = pd.DataFrame()
income_qu = pd.DataFrame()
cash_qu = pd.DataFrame()
summary_qu = pd.DataFrame()


#Cycle through tickers collecting financials
for i in range(0,  len(tickers)):
    #pull data and store in temporary containers
    balance_an_temp, income_an_temp, cash_an_temp, balance_qu_temp, income_qu_temp, cash_qu_temp, summary_qu_temp = scrape_symbol(tickers[i])

    #append results
    balance_an = balance_an.append(balance_an_temp)
    income_an = income_an.append(income_an_temp)
    cash_an = cash_an.append(cash_an_temp)
    balance_qu = balance_qu.append(balance_qu_temp)
    income_qu = income_qu.append(income_qu_temp)
    cash_qu = cash_qu.append(cash_qu_temp)
    summary_qu = summary_qu.append(summary_qu_temp)


















