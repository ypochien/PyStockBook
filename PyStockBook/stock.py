from loguru import logger
from strenum import StrEnum
import requests
import pandas as pd


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

        self.twse: pd.DataFrame = pd.DataFrame()
        self.tpex: pd.DataFrame = pd.DataFrame()

    def get_twse_closing_price(self):
        logger.info("開始下載 TWSE...")
        res = requests.get(url=URL.TWSE_CLOSING_PRICE)
        if res.status_code != requests.codes.ok:
            logger.error(f"Request failed: {res.status_code}")
            return
        df = pd.DataFrame(res.json())
        self.twse = df[["Code", "Name", "ClosingPrice"]]
        self.twse.columns = ["code", "name", "close"]

    def get_tpex_closing_price(self):
        logger.info("開始下載 TPEX...")
        res = requests.get(url=URL.TPEX_CLOSEING_PRICE)
        if res.status_code != requests.codes.ok:
            logger.error(f"Request failed: {res.status_code}")
            return
        df = pd.DataFrame(res.json())
        self.date = df["Date"].iloc[0]
        self.tpex = df[["SecuritiesCompanyCode", "CompanyName", "Close"]]
        self.tpex.columns = ["code", "name", "close"]
