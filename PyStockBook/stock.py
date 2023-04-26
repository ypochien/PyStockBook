from loguru import logger
from strenum import StrEnum
import requests
import typing

# import pandas as pd


class URL(StrEnum):
    TWSE_CLOSING_PRICE = (
        "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_AVG_ALL"
    )
    TPEX_CLOSEING_PRICE = (
        "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_daily_close_quotes"
    )


class Stock:
    def __init__(self):
        self.date: str = ""

        self.twse: typing.Dict = dict()
        self.tpex: typing.Dict = dict()

    def get_twse_closing_price(self):
        logger.info("開始下載 TWSE...")
        res = requests.get(url=URL.TWSE_CLOSING_PRICE)
        if res.status_code != requests.codes.ok:
            logger.error(f"Request failed: {res.status_code}")
            return
        self.twse = {
            item["Code"]: {"name": item["Name"], "close": item["ClosingPrice"]}
            for item in res.json()
        }

    def get_tpex_closing_price(self):
        logger.info("開始下載 TPEX...")
        res = requests.get(url=URL.TPEX_CLOSEING_PRICE)
        if res.status_code != requests.codes.ok:
            logger.error(f"Request failed: {res.status_code}")
            return
        self.tpex = {
            item["SecuritiesCompanyCode"]: {
                "name": item["CompanyName"],
                "close": item["Close"],
            }
            for item in res.json()
        }
        self.date = res.json()[0]["Date"]
