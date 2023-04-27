import adodbapi
import typing 

def open_sdf(sdf_path: typing.Optional[str] = None):
    if sdf_path is None:
        sdf_path = r"./DATA/StockBook.sdf"
    password = r"St0ck%%Book"
    cons_str = f"Provider=Microsoft.SQLSERVER.CE.OLEDB.3.5;Data Source={sdf_path};SSCE:Database Password={password};Mode=ReadWrite|Share Deny None;"
    return adodbapi.connect(
        cons_str,
    )
