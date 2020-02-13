from datetime import datetime
import lxml
from lxml import html
import requests
import numpy as np
import pandas as pd
from selenium import webdriver
import time


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
        annual_balance['Symbol'] = symbol
        print(symbol + ": annual balance sheet")
    except:
        print(symbol +": Could not scrape annual balance sheet")

    #Navigate/scrape Income Statement
    driver.find_element_by_xpath("//span[text()='Income Statement']").click()
    time.sleep(3)
    try:
        annual_income = get_data(driver)
        annual_income['Symbol'] = symbol
        print(symbol + ": annual income statement")
    except:
        print(symbol + ": Could not scrape annual income statment")

    #Navigate/scrape Cash Flow
    driver.find_element_by_xpath("//span[text()='Cash Flow']").click()
    time.sleep(3)
    try:
        annual_cash = get_data(driver)
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
tickers = ['INTL', 'AMD', 'AAPL', 'MSFT']


#create empty dataframes to store results
balance_an = pd.DataFrame()
income_an = pd.DataFrame()
cash_an = pd.DataFrame()
balance_qu = pd.DataFrame()
income_qu = pd.DataFrame()
cash_qu = pd.DataFrame()
summary_qu = pd.DataFrame()

#Cycle through tickers collecting financials
for i in range(1,  4):
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


