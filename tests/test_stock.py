import os
from pathlib import Path
import ujson as json
from pytest_mock import MockFixture
import requests_mock
import datetime
from PyStockBook.stock import Stock, URL


def test_twse_date():
    sut = Stock()
    sut.get_twse_closing_price()
    assert (
        sut.datetime.date() + datetime.timedelta(days=1)
        == datetime.datetime.now().date()
    )
    assert sut.twse.shape == (18607, 4)


def test_mock_twse_data():
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    jsonfile = script_dir / "data" / "STOCK_DAY_AVG_ALL.json"

    with open(jsonfile, "rb") as json_file:
        json_obj = json.load(json_file)

    json_text = json.dumps(json_obj)
    sut = Stock()
    with requests_mock.Mocker() as mock:
        mock.get(
            URL.TWSE_CLOSING_PRICE,
            text=json_text,
            headers={"Last-Modified": "Wed, 19 Apr 2023 21:00:46 GMT"},
        )
        sut.get_twse_closing_price()

    assert (
        sut.datetime.date() + datetime.timedelta(days=1)
        == datetime.datetime.now().date()
    )
    assert sut.twse.shape == (18607, 4)
