import threading
import queue
import time
import pyupbit
import datetime
from collections import deque

class Consumer(threading.Thread):
    def __init__(self, q):
        super().__init__()
        self.q = q
        self.ticker = "KRW-XRP"

        self.ma15 = deque(maxlen=15)
        self.ma50 = deque(maxlen=50)        
        self.ma120 = deque(maxlen=120)

        df = pyupbit.get_ohlcv(self.ticker, interval="minute1")
        self.ma15.extend(df['close'])
        self.ma50.extend(df['close'])
        self.ma120.extend(df['close'])

        print(len(self.ma15), len(self.ma50), len(self.ma120))


    def run(self):
        price_curr = None
        hold_flag = False
        wait_flag = False

        with open("upbit.txt", "r") as f:       # 업비트 로그인 (파일인덱스)
            key0 = f.readline().strip()         # 업비트 로그인 (1번째줄 키)
            key1 = f.readline().strip()         # 업비트 로그인 (2번째줄 키)

        upbit = pyupbit.Upbit(key0, key1)       # 업비트 로그인
        cash = upbit.get_balance()              # 업비트 캐쉬 조회
        print("보유현금", cash)

        i = 0
        
        while True:
            try:
                if not self.q.empty():
                    if price_curr != None:
                        self.ma15.append(price_curr)
                        self.ma50.append(price_curr)
                        self.ma120.append(price_curr)

                    curr_ma15 = sum(self.ma15) / len(self.ma15)
                    curr_ma50 = sum(self.ma50) / len(self.ma50)
                    curr_ma120 = sum(self.ma120) / len(self.ma120)

                    price_open = self.q.get()
                    if hold_flag == False:
                        price_buy  = int(price_open * 1.01)
                        price_sell = int(price_open * 1.025)
                    wait_flag  = False

                price_curr = pyupbit.get_current_price(self.ticker)
                
                if hold_flag == False and wait_flag == False and\
                    price_curr >= price_buy and curr_ma15 >= curr_ma50 and \
                    curr_ma15 <= curr_ma50 * 1.03 and curr_ma120 <= curr_ma50 :
                    # 0.05%수수료
                    ret = upbit.buy_market_order(self.ticker, cash * 0.9995)
                    print("매수주문", ret)
                    time.sleep(1)
                    volume = upbit.get_balance(self.ticker)
                    ret = upbit.sell_limit_order(self.ticker, price_sell, volume)
                    print("매도주문", ret)
                    hold_flag = True
                # print(price_curr, curr_ma15, curr_ma50, curr_ma120)

                if hold_flag == True:
                    uncomp = upbit.get_order(self.ticker)
                    if len(uncomp) == 0:
                        cash = upbit.get_balance()
                        print("매도완료", cash)
                        hold_flag = False
                        wait_flag = True
                        
                # 3 minutes
                if i == (5 * 60 * 3):
                    print(f"[{datetime.datetime.now()}] 현재가 {price_curr}, 목표가 {price_buy}, 판매가 {price_sell}, ma {curr_ma15:.2f}/{curr_ma50:.2f}/{curr_ma120:.2f}, hold_flag {hold_flag}, wait_flag {wait_flag}")
                    i = 0
                i += 1                
            except:
                print("error")

            time.sleep(0.2)

class Producer(threading.Thread):
    def __init__(self, q):
        super().__init__()
        self.q = q

    def run(self):
        while True:
            price = pyupbit.get_current_price("KRW-XRP")
            self.q.put(price)
            time.sleep(60)

q = queue.Queue()
Producer(q).start()
Consumer(q).start()