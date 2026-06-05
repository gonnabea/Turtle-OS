
#!pip install mplfinance

import yfinance as yf
import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime

start_date = '2026-04-01'
end_date = '2026-05-17'  # 원하는 마지막 날짜에 +1 더해줘야 한다.

# ticker = ['069500.KS']  # KODEX 200 ETF
# ticker = ['SPY']  # S&P500 ETF
ticker = 'TQQQ'  # 티커는 야후파이낸스를 따릅니다.

# 데이터 불러오기
stock_data = yf.download(ticker, start=start_date, end=end_date)

#data = stock_data[['Open','High','Low','Adj Close']]  # 종가는 수정종가를 사용한다
data = stock_data[['Open','High','Low','Close']]
data.columns = ['Open','High','Low','Close']

# 지수화된 주가 계산
data = data / data.iloc[0] * 100

# 이격도 계산 함수 정의
def calculate_disparity(data, ticker, moving_average_period):
    moving_average = data.rolling(window=moving_average_period).mean()
    disparity = (data / moving_average) * 100
    return disparity

def calculate_volatility(data, ticker, period=20, annual_factor=252):
#def calculate_volatility(data, ticker, period=20, annual_factor=120):

    # 로그 수익률 계산
    log_returns = np.log(data / data.shift(1))

    # 변동성 계산
    volatility = log_returns.rolling(window=period).std() * np.sqrt(annual_factor) * 100

    return volatility

# 각 티커에 대한 이격도 계산 및 그래프 그리기
plt.figure(figsize=(14, 10))

# x축 범위 설정을 위한 시작 및 종료 날짜
x_start_date = data.index.min()
x_end_date = data.index.max()

# 1달 단위 날짜 추출
monthly_dates = pd.date_range(start=start_date, end=end_date, freq='MS')

# 20일 및 60일 이격도 계산
disparity_5d = calculate_disparity(data['Close'], ticker, 5)
disparity_20d = calculate_disparity(data['Close'], ticker, 20)

# 변동성 계산
volatility = calculate_volatility(data['Close'], ticker)

#fig
fig, axes = plt.subplots(
    3,
    1,
    figsize=(14, 10),
    sharex=True,
    gridspec_kw={'height_ratios': [2, 1, 1]}
)

# 캔들차트를 위한 스타일 설정
mc = mpf.make_marketcolors(
    up='red',
    down='blue',
    edge='black',
    wick='black',
    inherit=True
)

s = mpf.make_mpf_style(marketcolors=mc)

# 2일의 여백
margin = datetime.timedelta(days=2)

# 캔들차트 그리기
mpf.plot(
    data,
    ax=axes[0],
    type='candle',
    style=s,
    ylabel='Price',
    mav=(5, 20),  # 5일과 20일 이동평균 추가
    mavcolors=['red', 'black'],  # 5일 이동평균은 빨간색, 20일 이동평균은 검은색
    show_nontrading=True,
    scale_width_adjustment=dict(candle=0.8, volume=0.8),
    xlim=(x_start_date - margin, x_end_date + margin)
)

# axes[0]에 제목 설정
axes[0].set_title("{} Candlestick Chart".format(ticker))

# 월단위 수직선 그리기
for date in monthly_dates:
    axes[0].axvline(
        x=date,
        color='gray',
        linestyle='--',
        alpha=0.5
    )

# 이격도 그래프
axes[1].bar(
    disparity_5d.index,
    disparity_5d - 100,
    color='red',
    label=f'{ticker} 5-Day Disparity',
    alpha=0.7
)

axes[1].plot(
    disparity_20d - 100,
    color='black',
    label=f'{ticker} 20-Day Disparity',
    alpha=0.7
)

axes[1].axhline(
    0,
    color='black',
    linestyle='--'
)

axes[1].set_title(
    f'{ticker} 5-Day and 20-Day Disparity'
)

axes[1].legend(loc='upper left')

plt.xlim(
    x_start_date - margin,
    x_end_date + margin
)

# 월단위 수직선 그리기
for date in monthly_dates:
    axes[1].axvline(
        x=date,
        color='gray',
        linestyle='--',
        alpha=0.5
    )

# 변동성 그래프
axes[2].plot(
    volatility,
    label=f'{ticker} Volatility',
    color='green'
)

axes[2].set_title(
    f'{ticker} Rolling 20-Day Annualized Volatility'
)

axes[2].legend(loc='upper left')

plt.xlim(
    x_start_date - margin,
    x_end_date + margin
)

# 월단위 수직선 그리기
for date in monthly_dates:
    axes[2].axvline(
        x=date,
        color='gray',
        linestyle='--',
        alpha=0.5
    )

plt.tight_layout()
plt.show()
