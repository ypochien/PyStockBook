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
    assert len(sut.twse) > 0


def test_tpex_date():
    sut = Stock()
    sut.get_tpex_closing_price()
    assert len(sut.tpex) > 0


def test_load_xdxr():
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    jsonfile = script_dir / "data" / "xd.json"
    sut = Stock()
    sut.load_xdxr(jsonfile)
    assert len(sut.xd) > 0
    assert len(sut.xr) == 0

    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    jsonfile = script_dir / "data" / "xr.json"
    sut.load_xdxr(jsonfile)
    assert len(sut.xr) > 0


def test_mock_twse_data():
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    jsonfile = script_dir / "data" / "STOCK_DAY_ALL.json"
    with open(jsonfile, "rb") as json_file:
        json_obj = json.load(json_file)
    json_text = json.dumps(json_obj)
    time_obj = datetime.datetime.now()
    time_str = time_obj.strftime("%a, %d %b %Y %H:%M:%S GMT")

    sut = Stock()
    with requests_mock.Mocker() as mock:
        mock.get(
            URL.TWSE_CLOSING_PRICE,
            text=json_text,
            headers={"Last-Modified": time_str},
        )
        sut.get_twse_closing_price()

    assert len(sut.twse) == 1191


def test_mock_tpex_data():
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    jsonfile = script_dir / "data" / "tpex_mainboard_quotes.json"
    with open(jsonfile, "rb") as json_file:
        json_obj = json.load(json_file)

    sut = Stock()
    json_text = json.dumps(json_obj)
    time_obj = datetime.datetime.now()
    time_str = time_obj.strftime("%a, %d %b %Y %H:%M:%S GMT")
    with requests_mock.Mocker() as mock:
        mock.get(
            URL.TPEX_CLOSEING_PRICE,
            text=json_text,
            headers={"Last-Modified": time_str},
        )
        sut.get_tpex_closing_price()

    assert len(sut.tpex) == 905
