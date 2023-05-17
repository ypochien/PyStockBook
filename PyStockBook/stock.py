from loguru import logger
from strenum import StrEnum
import requests
import typing
import datetime
import ujson as json


class URL(StrEnum):
    TWSE_CLOSING_PRICE = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
    TPEX_CLOSEING_PRICE = "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes"
    ESB_TPEX_CLOSEING_PRICE = (
        "https://www.tpex.org.tw/openapi/v1/tpex_esb_latest_statistics"
    )
    TWSE_XDXR = "https://openapi.twse.com.tw/v1/exchangeReport/TWT48U_ALL"


class Stock:
    def __init__(self):
        self.date: str = ""

        self.twse: typing.Dict = dict()
        self.tpex: typing.Dict = dict()
        self.esb: typing.Dict = dict()
        self.twse_xdxr: typing.Dict = dict()
        self.xd: typing.List[typing.Dict[str, typing.Any]] = list()
        self.xr: typing.List[typing.Dict[str, typing.Any]] = list()

    def load_xdxr(self, json_file):
        with open(json_file, "rb") as json_file:
            data = json.load(json_file)
            zipped = list(zip(*data.values()))
            if "ExDividendDate" in data.keys():
                self.xd = [dict(zip(data.keys(), values)) for values in zipped]
            elif "ExRightsDate" in data.keys():
                self.xr = [dict(zip(data.keys(), values)) for values in zipped]

    def get_twse_closing_price(self):
        logger.info("開始下載 TWSE(上市)...")
        res = requests.get(url=URL.TWSE_CLOSING_PRICE)
        if res.status_code != requests.codes.ok:
            logger.error(f"TWSE Request failed: {res.status_code}")
            return
        self.twse = {
            item["Code"]: {
                "name": item["Name"],
                "close": item["ClosingPrice"]
                if item["ClosingPrice"].replace("-", "").strip() != ""
                else "0.0",
                "market": 1,
            }
            for item in res.json()
        }
        logger.info(f"筆數: {len(self.twse)} 筆 ")

    def get_esb_tpex_closing_price(self):
        logger.info("開始下載 ESB-TPEX(興櫃)...")
        res = requests.get(url=URL.ESB_TPEX_CLOSEING_PRICE)
        if res.status_code != requests.codes.ok:
            logger.error(f"ESB-TPEX Request failed: {res.status_code}")
            return

        self.esb = {
            item["SecuritiesCompanyCode"]: {
                "name": item["CompanyName"],
                "close": item["Average"]
                if item["Average"].replace("-", "").strip() != ""
                else "0.0",
                "market": 3,
            }
            for item in res.json()
        }
        logger.info(f"筆數: {len(self.esb)} 筆 ")

    def get_tpex_closing_price(self):
        logger.info("開始下載 TPEX(上櫃)...")
        res = requests.get(url=URL.TPEX_CLOSEING_PRICE)
        if res.status_code != requests.codes.ok:
            logger.error(f"TPEX Request failed: {res.status_code}")
            return
        self.tpex = {
            item["SecuritiesCompanyCode"]: {
                "name": item["CompanyName"],
                "close": item["Close"]
                if item["Close"].replace("-", "").strip() != ""
                else "0.0",
                "market": 2,
            }
            for item in res.json()
        }
        self.date = res.json()[0]["Date"]
        logger.info(f"筆數: {len(self.tpex)} 筆 ")
