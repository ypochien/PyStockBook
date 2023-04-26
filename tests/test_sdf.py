import os
from pathlib import Path
import adodbapi as dbapi


def test_sdf():
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    dbpath = script_dir / "data" / "StockBook.sdf"
    password = r"St0ck%%Book"
    cons_str = f"Provider=Microsoft.SQLSERVER.CE.OLEDB.3.5;Data Source={dbpath};SSCE:Database Password={password};Mode=ReadWrite|Share Deny None;"
    conn = dbapi.connect(cons_str)
    cursor = conn.cursor()
    cursor.execute("select Stockname,ClosingPrice from stock where StockNo='2330';")
    result: dbapi.apibase.SQLrows = cursor.fetchall()  # type: ignore
    assert result.ado_results == (("台積電",), (498.0,))
