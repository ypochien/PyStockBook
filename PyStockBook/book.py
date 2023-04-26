from loguru import logger
from PyStockBook.sdf import open_sdf
import adodbapi
from .stock import Stock


class Book:
    def __init__(self) -> None:
        print("Start StockBook...")
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
        logger.info(f"寫入資料中... TWSE:  {len(self.stock.twse)}")
        cnt_twse = 0
        cnt_tpex = 0
        for code, row in self.stock.twse.items():
            if code not in exist_code:
                continue
            cnt_twse += 1
            if code == "2330":
                logger.info(f"{code}:{row}")

            name = row["name"]
            price = (
                0.0
                if row["close"].strip() == "" or row["close"] == "--"
                else float(row["close"])
            )
            update_sql = f"UPDATE stock SET ClosingPrice = {price} , StockName ='{name}' WHERE StockNo = '{code}';"
            cursor.execute(update_sql)

        logger.info(f"寫入資料中... TPEX:  {len(self.stock.tpex)}")
        for code, row in self.stock.tpex.items():
            if code not in exist_code:
                continue
            cnt_tpex += 1
            if code == "8299":
                logger.info(f"{code}:{row}")
            name = row["name"]
            price = 0.0 if row["close"] or row["close"] == "--" else float(row["close"])
            update_sql = f"UPDATE stock SET ClosingPrice = {price} , StockName ='{name}' WHERE StockNo = '{code}';"
            cursor.execute(update_sql)
        connection.commit()
        cursor.close()
        connection.close()
        logger.info(f"更新完畢...TWSE:{cnt_twse} TPEX: {cnt_tpex}")
