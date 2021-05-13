import pyupbit
import time
import datetime

access = "4GCpUIApjDWr0MycA7dTUUJXGvoAYOt3zThd2LRB"
secret = "JRea20zazMQggEGVfpy4JUgOILTi4Kx7rps6ndhD"

def cal_target(ticker):   
    df = pyupbit.get_ohlcv(ticker, "day")
    yesterday = df.iloc[-2]
    today = df.iloc[-1]
    yesterday_range = yesterday['high']-yesterday['low']
    target = today['open'] + yesterday_range * 0.3
    return target

# 업비트 로그인
upbit = pyupbit.Upbit(access, secret)

# 변수 설정
target = cal_target("KRW-DOGE")
op_mode = False
hold = False

while True:
    now = datetime.datetime.now()

# 거래 시작

    # 전량 매도 시도
    if now.hour == 8 and now.minute == 59 and 50 <= now.second <=59:
        if op_mode is True and hold is True:
            doge_balance = upbit.get_balance("KRW-DOGE")
            upbit.sell_market_order("KRW-DOGE". doge_balance)
            hold = False

        op_mode = False
        time.sleep(10)

    #  09:00:00 목표가 갱신
    if now.hour == 9 and now.minute == 0 and 20 <= now.second <=30:
        target =cal_target("KRW-DOGE")
        op_mode = True

    price = pyupbit.get_current_price("KRW-DOGE")

    # 매초마다 조건 확인 후 매수 시도
    if op_mode is True and hold is False and price >= target:
        
        # 전량 매수 시도
        if op_mode is True and price is not None and price >= target and hold is False:
            krw_balance = upbit.get_balance("KRW")
            upbit.buy_market_order("KRW-DOGE", krw_balance)
            hold = True

    # 상태 출력
    print(f"현재시간: {now} 목표가: {target} 현재가: {price} 보유상태: {hold} 동작상태: {op_mode}")
    
    time.sleep(1)

