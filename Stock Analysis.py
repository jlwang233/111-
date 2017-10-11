import pandas as pd
import pandas_datareader.data as web
import datetime
from pandas_datareader._utils import RemoteDataError
from dateutil.relativedelta import relativedelta
# import matplotlib.pyplot as plt

# declare the indices we used for future analysis
index_list = ['^IXIC', '^NYA', '^DJI', '^GSPC', '000001.SS', '^STOXX50E']

# get today's date as end_date for analysis
end_date = datetime.datetime.today()
start_date = end_date - relativedelta(months=24)
print("Start date: {}\nEnd date: {}".format(start_date, end_date))


def download_index():
    # download the indices needed
    df_index = pd.DataFrame()
    i = 0
    while i < len(index_list):
        try:
            df_temp = web.DataReader(index_list[i], 'yahoo', start_date, end_date)
            df_index[index_list[i]] = df_temp['Adj Close']
            i += 1
        except RemoteDataError:
            print('RemoteDataError...Recatch...')
            continue
    return df_index


download_index()


def verify_tickers():
    # ask for stock tickers input from users and verify the accessibility in Yahoo
    df_ticker = pd.read_csv("Yahoo_Stocks&Indexes_092017.csv")
    tickers_input = input("Input tickers you want to analyze in capitalized comma separated format:")
    tickers = tickers_input.split(",")
    if not tickers:
        print("Input tickers empty!")
    else:
        ticker_list = [ticker for ticker in tickers if ticker in
                       df_ticker.Ticker.unique()]
        print(ticker_list, ": searchable in Yahoo Finance!")

        ticker_error = [ticker for ticker in tickers if ticker not in
                        df_ticker.Ticker.unique()]
        if ticker_error:
            print(ticker_error, ": unrecognized in Yahoo Finance!")

        return ticker_list


def data_loader():
    # catch data of selected stocks from yahoo Finance
    df_volume = pd.DataFrame()
    df_price = pd.DataFrame()
    df_merged = download_index()
    ticker_list = verify_tickers()
    i = 0
    while i < len(ticker_list):
        try:
            df = web.DataReader(ticker_list[i], 'yahoo',start_date, end_date)
            df_merged[ticker_list[i]] = df['Adj Close']
            df_price[ticker_list[i]] = df['Adj Close']
            df_volume[ticker_list[i]] = df['Volume']
            i += 1
        except RemoteDataError:
            print('RemoteDataError...Recatch...')
            continue

    print("history adjusted price of stocks selected:",'\n',df_price,'\n',"history volume of stocks selected:", '\n',
          df_volume)
    return df_merged


def corr_cal():
    # calculate the correlation between indices and selected stocks
    df_merged = data_loader()
    returns = df_merged.pct_change()
    corr = returns.corr().iloc[:6,6:]
    print(corr)
    return corr


def highest_stock_per_index():
    # get the stock with highest correlation per index
    corr = corr_cal()
    ticker_list = verify_tickers()
    corr1 = corr
    corr1['highest'] = corr1.max(axis=1)
    for ticker in ticker_list:
        for index in index_list:
            if corr1.loc[index][ticker] == corr1.loc[index]['highest']:
                print('stock with highest corr per index:', '\n', index, ":", corr1.loc[index]['highest'], ticker)


def highest_index_per_stock():
    # get the index with highest correlation per stock
    corr = corr_cal()
    ticker_list = verify_tickers()
    corr2 = corr.transpose()
    corr2['highest'] = corr2.max(axis=1)
    for ticker in ticker_list:
        for index in index_list:
            if corr2[index][ticker] == corr2['highest'][ticker]:
                print('index with highest corr per stock:', '\n', ticker, ":", corr2['highest'][ticker], index)

    return corr2


def higher_corr_with_shift():
    # get corr within +/-5 days shift that is higher than the corr get in former process
    df_merged = data_loader()
    returns = df_merged.pct_change()
    ticker_list = verify_tickers()
    corr2 = highest_index_per_stock()
    all_corr = {i:returns[6:].shift(i).corr().iloc[:6, 6:] for i in range(-5,6) if i != 0}
    for i in range(-5,6):
        if i != 0:
            for ticker in ticker_list:
                for index in index_list:
                    if all_corr[i].loc[index][ticker]> corr2['highest'][ticker]:
                        print(i, ticker,":",all_corr[i].loc[index][ticker], index)
