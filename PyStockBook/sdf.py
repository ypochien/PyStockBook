import adodbapi


def open_sdf():
    password = r"St0ck%%Book"
    cons_str = f"Provider=Microsoft.SQLSERVER.CE.OLEDB.3.5;Data Source=./data/StockBook.sdf;SSCE:Database Password={password};Mode=ReadWrite|Share Deny None;"
    return adodbapi.connect(
        cons_str,
    )
