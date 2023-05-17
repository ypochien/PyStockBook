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

        def update_stock_xr():
            stock_data = self.stock.xr
            logger.info(f"更新上市櫃除權資料... :  {len(stock_data)} 筆 ")
            # {'Code': '9105', 'Name': '泰金寶-DR', 'ExRightsDate': '2023-03-17 00:00:00', 'StockAmount': 0.0833333}
            for stock in stock_data:
                if stock.get("Code", "") not in exist_code:
                    logger.warning(f"無基本資料 {stock}")
                    # try:
                    #     insert_sql = """INSERT INTO stock (stockno,market,stockname,unitshares,closingprice, xr, xrday)
                    #                 VALUES ('%s','1', '%s','1000','0', '%s', '%s')""" % (
                    #         stock["Code"],
                    #         stock["Name"],
                    #         stock["StockAmount"],
                    #         stock["ExRightsDate"],
                    #     )
                    #     cursor.execute(insert_sql)
                    # except Exception as e:
                    #     logger.warning(f"新增失敗 {stock} {e}")
                    #     break
                else:
                    try:
                        update_sql = f"UPDATE stock SET xr = '{stock.get('StockAmount',0)}', xrday = '{stock['ExRightsDate']}' WHERE StockNo = '{stock['Code']}';"
                        cursor.execute(update_sql)
                    except Exception as e:
                        logger.warning(f"更新失敗 {stock} {e}")
                        break

        def update_stock_xd():
            stock_data = self.stock.xd
            logger.info(f"更新上市櫃除息資料... :  {len(stock_data)} 筆")
            # {'Code': '2636', 'Name': '台驊投控', 'ExDividendDate': '2023-01-04 00:00:00', 'CashAmount': 5.17793356}
            for stock in stock_data:
                if stock.get("Code", "") not in exist_code:
                    logger.warning(f"無基本資料 {stock}")
                    # try:
                    #     insert_sql = """INSERT INTO stock (stockno,market,stockname,unitshares,closingprice, xd, xdday)
                    #                     VALUES ('%s','1', '%s','1000','0', '%s', '%s')""" % (
                    #         stock["Code"],
                    #         stock["Name"],
                    #         stock["CashAmount"],
                    #         stock["ExDividendDate"],
                    #     )
                    #     cursor.execute(insert_sql)
                    # except Exception as e:
                    #     logger.warning(f"新增失敗 {stock} {e}\n{insert_sql}")
                    #     break
                else:
                    try:
                        update_sql = f"UPDATE stock SET xd = '{stock.get('CashAmount',0)}', xdday = '{stock['ExDividendDate']}' WHERE StockNo = '{stock['Code']}';"
                        cursor.execute(update_sql)
                    except Exception as e:
                        logger.warning(f"更新失敗 {stock} {e}")
                        break

        def get_data_from_github():
            import requests

            # GitHub API endpoint for your repository
            repo_url = "https://api.github.com/repos/ypochien/sb_xdxr/contents"

            response = requests.get(repo_url)

            if response.status_code == 200:
                files = response.json()
                for file in files:
                    if file["name"].endswith(".json"):
                        json_url = file["download_url"]
                        json_response = requests.get(json_url)
                        if json_response.status_code == 200:
                            logger.info(f'Retrieve {file["name"]}')
                            data = json_response.json()
                            zipped = list(zip(*data.values()))
                            if "ExDividendDate" in data.keys():
                                self.stock.xd = [
                                    dict(zip(data.keys(), values)) for values in zipped
                                ]
                                update_stock_xd()
                                try:
                                    connection.commit()
                                except Exception as e:
                                    logger.warning(f"現金除息 回寫失敗 {e}")

                            elif "ExRightsDate" in data.keys():
                                self.stock.xr = [
                                    dict(zip(data.keys(), values)) for values in zipped
                                ]
                                update_stock_xr()
                                try:
                                    connection.commit()
                                except Exception as e:
                                    logger.warning(f"股票除權 回寫失敗 {e}")

                        else:
                            print(
                                f'Failed to retrieve {file["name"]} from GitHub. Status code: {json_response.status_code}'
                            )
            else:
                print(
                    f"Failed to retrieve file list from GitHub. Status code: {response.status_code}"
                )

        self.stock.get_twse_closing_price()
        self.stock.get_tpex_closing_price()
        self.stock.get_esb_tpex_closing_price()
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

        cursor.execute("SELECT * FROM Stock")
        sdf = cursor.fetchall()
        exist_code = sdf.ado_results[0]

        get_data_from_github()
        cursor.close()
        connection.close()
        logger.info(f"更新完畢...")
