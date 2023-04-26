from loguru import logger

#
# from PyStockBook.stock import Stock
from PyStockBook.book import Book


def run():
    v = Book()
    v.update_stock_close_price()


def main():
    run()
