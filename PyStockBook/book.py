from loguru import logger
import pandas as pd
from PyStockBook.sdf import open_sdf
import adodbapi
from .stock import Stock
from adodbapi.apibase import variantConversions


class Book:
    def __init__(self) -> None:
        self.stock = Stock()

    def update_stock_close_price(self):
        self.stock.get_twse_closing_price()
        self.stock.get_tpex_closing_price()
        logger.info(f"資料日期 {self.stock.date}")
        connection: adodbapi.Connection = open_sdf()
        cursor: adodbapi.Cursor = connection.cursor()
        cursor.execute("SELECT * FROM Stock")
        sdf = cursor.fetchall()
        exist_code = sdf.ado_results[0]
        logger.info(f"寫入資料中... TWSE:  {self.stock.twse.shape}")
        for _, row in self.stock.twse.iterrows():
            code = row["code"]
            if code not in exist_code:
                continue
            if code == "2330":
                logger.info(row.to_dict())
            name = row["name"]
            price = (
                0.0
                if row["close"].strip() == "" or row["close"] == "--"
                else float(row["close"])
            )
            update_sql = f"UPDATE stock SET ClosingPrice = {price} , StockName ='{name}' WHERE StockNo = '{code}';"
            cursor.execute(update_sql)

        logger.info(f"寫入資料中... TPEX:  {self.stock.tpex.shape}")
        for _, row in self.stock.tpex.iterrows():
            code = row["code"]
            if code not in exist_code:
                continue
            if code == "8299":
                logger.info(row.to_dict())
            name = row["name"]
            price = 0.0 if row["close"] or row["close"] == "--" else float(row["close"])
            update_sql = f"UPDATE stock SET ClosingPrice = {price} , StockName ='{name}' WHERE StockNo = '{code}';"
            cursor.execute(update_sql)
        connection.commit()
        cursor.close()
        connection.close()
        logger.info(
            f"更新完畢...TWSE: {self.stock.twse.shape}  TPEX: {self.stock.tpex.shape}"
        )
