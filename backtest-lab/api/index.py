# index.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
# from larry_williams_day_api import calculate_breakout_price, backtest_breakout_daily, calculate_today_breakout_price, Config
# from larry_williams_day_fine_api import backtest_with_stop_take, Config
from larry_connors_api import connors_api

app = FastAPI(title="Backtest-Labs")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/larry_connors_rsi4")
def larry_connors_rsi4(
    ticker: str = Query("QQQ", description="종목 티커"),
    start: str = Query("2020-08-01", description="시작 날짜 YYYY-MM-DD"),
    end: str = Query("2025-10-01", description="종료 날짜 YYYY-MM-DD"),
    first_rsi4: float = Query(30, description="첫 매수 기준 rsi4 수치"),
    second_rsi4: float = Query(25, description="두번쨰 매수 기준 rsi4 수치"),
    sell_rsi4: float = Query(80, description="매도 기준 rsi4 수치"),
):
    result = connors_api(
        ticker=ticker, 
        start=start, 
        end=end, 
        first_rsi4=first_rsi4, 
        second_rsi4=second_rsi4, 
        sell_rsi4=sell_rsi4
    )
    return {
        "ticker": ticker,
        "test_period": start + ' - ' + end,
        "seed_money": 100000,
        "result_money": result
    }

