import sys
from loguru import logger
from PyStockBook.book import Book


def run():
    v = Book()
    v.update_stock_close_price()
    input("按任意鍵離開....")


def main():
    sys.exit(run())
