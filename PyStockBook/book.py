from loguru import logger
from PyStockBook.sdf import open_sdf
import typing
import adodbapi
from .stock import Stock
import datetime


class Book:
    def __init__(self) -> None:
        print("Start StockBook...")
        self.stock = Stock()

    def update_stock_close_price(self, sdf_path: typing.Optional[str] = None):
        def update_stock_price(stock_data):
            logger.info(f"更新上市、上櫃、興櫃資料... :  {len(stock_data)}")
            new_item = []
            for code, row in stock_data.items():
                if code in ("2330", "2646", "8299"):
                    logger.info(f"{code}:{row}")

                if code not in exist_code:
                    item = {
                        "stockno": code,
                        "market": row["market"],
                        "stockname": row["name"],
                        "unitshares": 1000,
                        "closingprice": float(row["close"]),
                        "xr": "",
                        "xrday": "",
                        "xd": "",
                        "xdday": "",
                    }
                    try:
                        new_item.append(f"{code} {row['name']}")
                        insert_sql = """INSERT INTO stock (stockno, market, stockname, unitshares, closingprice)
                                        VALUES ('%s', %s, '%s', %s, %s)""" % (
                            item["stockno"],
                            item["market"],
                            item["stockname"],
                            1000,
                            item["closingprice"],
                        )
                        cursor.execute(insert_sql)

                    except Exception as e:
                        logger.warning(f"TSE除權息更新失敗 {item} {code}:{row} [{e}]")
                        break
                else:
                    name = row["name"]
                    price = (
                        0.0
                        if row["close"].replace("-", "").strip() == ""
                        else float(row["close"])
                    )
                    try:
                        update_sql = f"UPDATE stock SET ClosingPrice = {price} , StockName ='{name}' WHERE StockNo = '{code}';"
                        cursor.execute(update_sql)
                    except Exception as e:
                        logger.warning(f"更新失敗 {code}:{row} {e}")
            logger.info(f"新增 {len(new_item)} 筆 股票 \n {new_item}")

        def update_stock_xdxr(stock_data):
            logger.info(f"更新上市除權息資料... :  {len(stock_data)}")
            # new_item = 0
            for code, row in stock_data.items():
                if code not in exist_code:
                    if row["xr"] == 0 and row["xd"] == 0:
                        continue
                    item = {
                        "stockno": code,
                        "xr": row["xr"],
                        "xrday": row["date"],
                        "xd": row["xd"],
                        "xdday": row["date"],
                    }
                    try:
                        # new_item += 1
                        insert_sql = """INSERT INTO stock (stockno, xr, xrday, xd, xdday)
                                        VALUES ('%s', '%s', '%s', '%s', '%s')""" % (
                            item["stockno"],
                            item["xr"],
                            item["xrday"],
                            item["xd"],
                            item["xdday"],
                        )
                        cursor.execute(insert_sql)

                    except Exception as e:
                        logger.warning(f"{item}")
                        logger.warning(f"新增失敗 {code}:{row} {e}")
                        break
                else:
                    try:
                        update_sql = f"UPDATE stock SET xr = '{row['xr']}', xrday = '{row['date']}', xd = '{row['xd']}', xdday = '{row['date']}' WHERE StockNo = '{code}';"
                        cursor.execute(update_sql)
                    except Exception as e:
                        logger.warning(f"更新失敗 {code}:{row} {e}")
            # logger.info(f"新增 {new_item} 筆商品 ")

        self.stock.get_twse_closing_price()
        self.stock.get_tpex_closing_price()
        self.stock.get_esb_tpex_closing_price()
        self.stock.get_twse_xdxr()
        logger.info(f"資料日期 {self.stock.date}")
        try:
            connection: adodbapi.Connection = open_sdf(sdf_path)
        except Exception as e:
            logger.warning(f"無法開啟資料庫 {e}")
            return
        cursor: adodbapi.Cursor = connection.cursor()
        cursor.execute("SELECT * FROM Stock")
        sdf = cursor.fetchall()
        exist_code = sdf.ado_results[0]

        update_stock_price({**self.stock.twse, **self.stock.tpex, **self.stock.esb})
        try:
            connection.commit()
        except Exception as e:
            logger.warning(f"基本股價 回寫失敗 {e}")

        update_stock_xdxr({**self.stock.twse_xdxr})
        try:
            connection.commit()
        except Exception as e:
            logger.warning(f"除權息 回寫失敗 {e}")

        cursor.close()
        connection.close()
        logger.info(f"更新完畢...")
