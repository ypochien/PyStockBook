from loguru import logger
from PyStockBook.sdf import open_sdf
import json
import typing
import adodbapi
from .stock import Stock
import requests
import datetime


class Book:
    def __init__(self) -> None:
        print("Start StockBook...")
        self.stock = Stock()
        self.json_data = []  # 新增的屬性

    def update_stock_close_price(self, sdf_path: typing.Optional[str] = None):
        def update_stock_basic():
            basic = self.stock.basic
            cursor.execute("SELECT * FROM Stock")
            sdf = cursor.fetchall()
            exist_code = sdf.ado_results[0]
            logger.info(f"更新上市、上櫃、興櫃基本資料... :  {len(basic)}")
            new_items = []
            for one in basic:
                if one["Code"] not in exist_code:
                    new_items.append(one)
                    insert_sql = """INSERT INTO stock (stockno, market, stockname, unitshares, closingprice)
                                    VALUES ('%s', %s, '%s', %s, %s)""" % (
                        one["Code"],
                        one["Exchange"],
                        one["Name"],
                        one["Lot"],
                        float(one["Close"]),
                    )
                    try:
                        cursor.execute(insert_sql)
                    except Exception as e:
                        logger.warning(f"基本資料新增失敗 {one} [{e}]")
                        break
                else:
                    update_sql = f"UPDATE stock SET ClosingPrice = {float(one['Close'])} , Market = {one['Exchange']} WHERE stockno = '{one['Code']}'"
                    try:
                        cursor.execute(update_sql)
                    except Exception as e:
                        logger.warning(f"基本資料更新失敗 {one} [{e}]")
                        break
            logger.info(f"新增 {len(new_items)} 筆 股票 \n ")

        def update_stock_xr():
            stock_data = self.stock.xr
            cursor.execute("SELECT * FROM Stock")
            sdf = cursor.fetchall()
            exist_code = sdf.ado_results[0]
            logger.info(f"更新上市櫃除權資料... :  {len(stock_data)} 筆 ")
            # {'Code': '9105', 'Name': '泰金寶-DR', 'ExRightsDate': '2023-03-17 00:00:00', 'StockAmount': 0.0833333}
            for stock in stock_data:
                if stock.get("Code", "") not in exist_code:
                    logger.warning(f"\t無基本資料 {stock}")
                else:
                    update_sql = f"UPDATE stock SET xr = '{stock.get('StockAmount',0)}', xrday = '{stock['ExRightsDate']}' WHERE StockNo = '{stock['Code']}';"
                    try:
                        cursor.execute(update_sql)
                    except Exception as e:
                        logger.warning(f"更新失敗 {stock} {e}")
                        break

        def update_stock_xd():
            stock_data = self.stock.xd
            cursor.execute("SELECT * FROM Stock")
            sdf = cursor.fetchall()
            exist_code = sdf.ado_results[0]
            logger.info(f"更新上市櫃除息資料... :  {len(stock_data)} 筆")
            # {'Code': '2636', 'Name': '台驊投控', 'ExDividendDate': '2023-01-04 00:00:00', 'CashAmount': 5.17793356}
            for stock in stock_data:
                if stock.get("Code", "") not in exist_code:
                    logger.warning(f"\t無基本資料 {stock}")
                else:
                    update_sql = f"UPDATE stock SET xd = '{stock.get('CashAmount',0)}', xdday = '{stock['ExDividendDate']}' WHERE StockNo = '{stock['Code']}';"
                    try:
                        cursor.execute(update_sql)
                    except Exception as e:
                        logger.warning(f"更新失敗 {stock} {e}")
                        break

        def get_data_from_github():
            # GitHub API endpoint for your repository
            repo_url = "https://api.github.com/repos/ypochien/sb_xdxr/contents"
            response = requests.get(repo_url)
            current_year = str(datetime.datetime.now().year)

            try:
                with open("downloaded_files.json", "r") as f:
                    downloaded_files = json.load(f)
            except FileNotFoundError:
                downloaded_files = []

            if response.status_code == 200:
                files = response.json()
                for file in files:
                    if file["name"].endswith(".json"):
                        if (
                            current_year in file["name"]
                            or file["name"] not in downloaded_files
                        ):
                            json_url = file["download_url"]
                            try:
                                json_response = requests.get(json_url, timeout=5)
                                if json_response.status_code == 200:
                                    logger.info(f'Retrieve {file["name"]}')
                                    if file[
                                        "name"
                                    ] not in downloaded_files and not file[
                                        "name"
                                    ].startswith(
                                        "stock"
                                    ):
                                        downloaded_files.append(file["name"])
                                    self.json_data.append(
                                        json_response.json()
                                    )  # 將 JSON 資料儲存到 self.json_data 中
                            except Exception as e:
                                logger.warning(f"抓取失敗 {e}")
                with open("downloaded_files.json", "w") as f:
                    json.dump(downloaded_files, f)

            else:
                logger.warning(
                    f"Failed to retrieve file list from GitHub. Status code: {response.status_code}"
                )

        try:
            connection: adodbapi.Connection = open_sdf(sdf_path)
        except Exception as e:
            logger.warning(f"無法開啟資料庫 {e}")
            return

        cursor: adodbapi.Cursor = connection.cursor()

        get_data_from_github()

        for data in self.json_data:  # 新增的迴圈，依序處理每一份 JSON 資料
            zipped = list(zip(*data.values()))
            if "Exchange" in data.keys():
                self.stock.basic = [dict(zip(data.keys(), values)) for values in zipped]
                update_stock_basic()
                try:
                    connection.commit()
                except Exception as e:
                    logger.warning(f"基本資料 回寫失敗 {e}")

            if "ExDividendDate" in data.keys():
                self.stock.xd = [dict(zip(data.keys(), values)) for values in zipped]
                update_stock_xd()
                try:
                    connection.commit()
                except Exception as e:
                    logger.warning(f"現金除息 回寫失敗 {e}")

            elif "ExRightsDate" in data.keys():
                self.stock.xr = [dict(zip(data.keys(), values)) for values in zipped]
                update_stock_xr()
                try:
                    connection.commit()
                except Exception as e:
                    logger.warning(f"股票除權 回寫失敗 {e}")

        cursor.close()
        connection.close()
        logger.info(f"更新完畢...")
