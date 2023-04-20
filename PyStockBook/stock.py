import datetime
from enum import auto
from strenum import StrEnum
import requests
import pandas as pd

try:
    import ujson as json
except ImportError:
    import json


# 收盤價 https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_AVG_ALL
class URL(StrEnum):
    TWSE_CLOSING_PRICE = (
        "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_AVG_ALL"
    )


class Stock:
    def __init__(self):
        self.datetime: datetime.datetime = datetime.datetime.now() + datetime.timedelta(
            days=-1
        )
        self.twse: pd.DataFrame = pd.DataFrame()

    def get_twse_closing_price(self):
        params = {"accept": "application/json"}
        res = requests.get(url=URL.TWSE_CLOSING_PRICE, params=params)
        if res.status_code != requests.codes.ok:
            raise Exception(f"Request failed: {res.status_code}")
        datetime_format = "%a, %d %b %Y %H:%M:%S %Z"
        twse_datetime = datetime.datetime.strptime(
            res.headers.get("Last-Modified", ""), datetime_format
        )
        if twse_datetime > self.datetime:
            self.datetime = twse_datetime
            self.twse = pd.DataFrame(res.json())
        else:
            self.twse = pd.DataFrame()
