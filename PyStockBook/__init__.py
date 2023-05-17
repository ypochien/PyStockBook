"""
Stock Book is a Python library for managing Stock
"""
import logging
from loguru import logger
import datetime

# from import StockBook

logfilename = f"StockBookPy_{str(datetime.datetime.now().date()).replace('-','')}.log"
logger.add(
    logfilename,
    retention="10 days",
    rotation="00:00",
    format="{time:YYYY-MM-DD :mm:ss} - {level} - {file} - {line} - {message}",
    level=logging.INFO,
)

__version__ = "0.0.1"
