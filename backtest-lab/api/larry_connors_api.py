import backtrader as bt
import yfinance as yf
import pandas as pd


def connors_api(ticker, start, end, first_rsi4, second_rsi4, sell_rsi4):
    # ✅ 데이터 다운로드
    # df = yf.download("SPY", start="2015-01-01", end="2025-01-01", progress=False) # 1배
    # df = yf.download("SSO", start="2022-01-01", end="2025-01-01", progress=False) # 2배
    # df = yf.download("UPRO", start="2020-01-01", end="2025-04-01", progress=False) # 3배
    # df = yf.download("SH", start="2020-01-01", end="2025-01-01", progress=False) # 인버스
    # df = yf.download("GLD", start="2015-01-01", end="2025-01-01", progress=False) # 금 1배
    # df = yf.download("UGL", start="2020-01-01", end="2025-04-01", progress=False) # 금 2배
    # df = yf.download("SHNY", start="2023-08-01", end="2023-09-30", progress=False) # 금 3배
    # df = yf.download("GDXU", start="2022-08-30", end="2022-09-30", progress=False) # 금광 3배

    # df = yf.download("KO", start="2022-08-01", end="2022-09-30", progress=False) # 금광 3배

    df = yf.download(ticker, start=start, end=end, progress=False) # QQQ 3배
    # df = yf.download("BITX", start="2024-08-01", end="2024-09-30", progress=False) # 비트코인 2배
    # df = yf.download("BRK-A", start="2022-08-01", end="2022-09-30", progress=False) # MSCI
    # df = yf.download("SCHD", start="2001-01-01", end="2025-04-01", progress=False) # SCHD
    # df = yf.download("KORU", start="2011-01-01", end="2025-04-01", progress=False) # MSCI
    # df = yf.download("SOXL", start="2024-08-01", end="2024-09-30", progress=False) # SOXL




    # df = yf.download("ETHU", start="2023-01-01", end="2025-04-01", progress=False) # 이더리움
    # df = yf.download("DFEN", start="2019-08-01", end="2019-09-30", progress=False) # 항공우주 3배
    # df = yf.download("HERO", start="2015-01-01", end="2025-04-01", progress=False) # 비디오게임
    # df = yf.download("ITA", start="2020-01-01", end="2025-04-01", progress=False) # 미국 항공, 방위






    # ✅ MultiIndex → 단일 컬럼으로 변환
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    # ✅ 전략 정의
    class Rsi4SplitStrategy(bt.Strategy):
        params = dict(rsi_period=4, rsi_buy1=first_rsi4, rsi_buy2=second_rsi4, rsi_sell=sell_rsi4)

        def __init__(self):
            self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)
            self.order = None
            self.buy1 = False
            self.buy2 = False

        def notify_order(self, order):
            if order.status in [order.Submitted, order.Accepted]:
                return  # 체결 전 단계는 무시

            if order.status in [order.Completed]:
                action = 'BUY' if order.isbuy() else 'SELL'
                print(f"[{self.datas[0].datetime.date(0)}] ORDER {action} EXECUTED: "
                    f"Price: {order.executed.price:.2f}, Size: {order.executed.size:.2f}, "
                    f"Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}")

            elif order.status in [order.Canceled, order.Margin, order.Rejected]:
                print(f"[{self.datas[0].datetime.date(0)}] ORDER {order.Status[order.status]}")

            self.order = None

        def notify_trade(self, trade):
            if trade.isclosed:
                print(f"[{self.datas[0].datetime.date(0)}] TRADE PROFIT: "
                    f"Gross: {trade.pnl:.2f}, Net: {trade.pnlcomm:.2f}")

        def next(self):
            # print(f"{self.datas[0].datetime.date(0)} RSI: {self.rsi[0]:.2f} | Position: {self.getposition().size:.2f} | Cash: {self.broker.get_cash():.2f}")

            if self.order:
                return  # 주문이 처리 중이면 아무 것도 하지 않음

            cash = self.broker.get_cash()
            pos = self.getposition().size

            # ✅ 첫 번째 매수 조건 (예수금의 절반)
            if self.rsi[0] < self.p.rsi_buy1 and not self.buy1:
                size = (cash * 0.5) / self.data.close[0]
                self.order = self.buy(size=size)
                self.buy1 = True

            # ✅ 두 번째 매수 조건 (남은 예수금 전부)
            if self.rsi[0] < self.p.rsi_buy2 and self.buy1 and not self.buy2:
                size = self.broker.get_cash() / self.data.close[0]
                self.order = self.buy(size=size)
                self.buy2 = True
                return

            # ✅ 전량 매도 조건
            if self.rsi[0] > self.p.rsi_sell and pos > 0:
                self.order = self.sell(size=pos)
                self.buy1 = False
                self.buy2 = False

    # ✅ 백트레이더 실행
    data = bt.feeds.PandasData(dataname=df)

    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(Rsi4SplitStrategy)
    cerebro.broker.set_cash(100000)
    cerebro.broker.setcommission(commission=0.001)

    print("🔁 백테스트 시작...")
    cerebro.run()
    print(f"✅ 최종 자산 가치: ${cerebro.broker.getvalue():,.2f}")
    result = cerebro.broker.getvalue()
    return result
