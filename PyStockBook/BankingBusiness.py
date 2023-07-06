import typing
from loguru import logger
import datetime
import polars as pl


def list_pad_dates(cursor, start_date):
    end_date = datetime.date.today()
    cursor.execute(
        f"SELECT Day FROM Schedule WHERE day>'{start_date}' AND day<='{end_date}' AND IsClosed=0 ORDER BY Day"
    )
    return [i._getValue(0).date() for i in cursor.fetchall()]


def latest_loan_data(cursor):
    sql = """SELECT * FROM LoanBalance"""
    cursor.execute(sql)
    sql_data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    # print(columns)
    df = pl.DataFrame(data=list(sql_data.ado_results), schema=columns)
    df = df.sort(["AccountNo", "AccountDay"])
    return df.groupby("AccountNo").agg(
        pl.col("AccountDay").last(),
        pl.col("Loan").last(),
        pl.col("InterestDate").last(),
        pl.col("InterestDays").last(),
        pl.col("LoanInterest").last(),
    )


def latest_account(cursor):
    sql = """SELECT AccountNo,LoanRate FROM Account WHERE MarginType=2 AND IsDeleted=0 GROUP BY Account.AccountNo, Account.LoanRate"""
    cursor.execute(sql)
    sql_data = cursor.fetchall()
    list_of_dicts = [
        dict(zip([column[0] for column in cursor.description], row)) for row in sql_data
    ]
    return pl.DataFrame(data=list_of_dicts)


def current_account_loan(cursor):
    df = latest_account(cursor)
    df = df.join(latest_loan_data(cursor), on="AccountNo", how="left")
    return df


def get_interest_date_and_days(all_open_date, open_date=datetime.date.today()):
    interest_date = [day for day in all_open_date if day >= open_date][2]
    next_open_date = [day for day in all_open_date if day >= open_date][3]
    return open_date, interest_date, (next_open_date - interest_date).days


def get_pading_loan_data(cursor):
    cursor.execute(
        f"SELECT Day FROM Schedule WHERE IsClosed=0 and day<='{str(datetime.date.today()+datetime.timedelta(days=30))}' ORDER BY Day"
    )
    all_open_date = [i._getValue(0).date() for i in cursor.fetchall()]
    df = current_account_loan(cursor)

    pad_data = []
    for one_df in df.to_dicts():
        if one_df["AccountDay"]:
            relevant_days = [
                day
                for day in list_pad_dates(cursor, one_df["AccountDay"])
                if day > one_df["AccountDay"].date()
            ]
            for date in relevant_days:
                loan_rate = one_df["LoanRate"]
                loan = int(one_df["Loan"])
                open_date, interest_date, interest_days = get_interest_date_and_days(
                    all_open_date, date
                )
                load_interest = (
                    0 if loan <= 0 else round(loan * loan_rate * interest_days)
                )
                new_record = (
                    one_df["AccountNo"],
                    open_date,
                    loan,
                    interest_date,
                    interest_days,
                    load_interest,
                )
                pad_data.append(new_record)
    return pad_data


def account_stock(df) -> pl.DataFrame:
    return (
        df.fill_null(0)
        .with_columns(
            [
                (pl.col("Quantity") * pl.col("UnitPrice")).alias("CostValue"),
                (pl.col("Quantity") * pl.col("ClosingPrice")).alias("MarketValue"),
                pl.col("ClosingPrice").alias("MarketPrice"),
            ]
        )
        .with_columns(
            [
                pl.when(pl.col("HoldingType") == 1)
                .then((pl.col("CostValue") * 1.001425).floor().round(0))
                .when(pl.col("HoldingType") == 2)
                .then(
                    (
                        (pl.col("CostValue") * 1.001425).floor()
                        - pl.col("Margin")
                        + pl.col("Collateral")
                    ).round(0)
                )
                .when(pl.col("HoldingType") == 3)
                .then((pl.col("Margin")))
                .otherwise(0)
                .alias("Cost"),
                pl.when(pl.col("HoldingType") == 1)
                .then(
                    (
                        pl.col("MarketValue")
                        - (pl.col("MarketValue") * 0.001425).floor()
                        - pl.col("MarketValue") * 0.003
                    ).round(0)
                )
                .when(pl.col("HoldingType") == 2)
                .then(
                    (
                        pl.col("MarketValue")
                        - (pl.col("MarketValue") * 0.001425).floor()
                        - pl.col("MarketValue") * 0.003
                        - pl.col("Margin")
                        + pl.col("Collateral")
                    ).round(0)
                )
                .when(pl.col("HoldingType") == 3)
                .then(
                    (
                        pl.col("Collateral")
                        + pl.col("Margin")
                        - pl.col("MarketValue")
                        - (pl.col("MarketValue") * 0.001425).floor()
                    )
                )
                .otherwise(0)
                .alias("RealizedValue"),
                pl.when(pl.col("HoldingType") == 1)
                .then(0)
                .when(pl.col("HoldingType") == 2)
                .then(
                    (
                        pl.col("Collateral")
                        + pl.col("MarketValue")
                        - (pl.col("MarketValue") * 0.001425).floor()
                        - pl.col("MarketValue") * 0.003
                    ).round(0)
                )
                .when(pl.col("HoldingType") == 3)
                .then(pl.col("Collateral") + pl.col("Margin"))
                .otherwise(0)
                .alias("d"),
                pl.when(pl.col("HoldingType") == 1)
                .then(0)
                .when(pl.col("HoldingType") == 2)
                .then(pl.col("Margin"))
                .when(pl.col("HoldingType") == 3)
                .then(pl.col("MarketValue") - (pl.col("CostValue") * 1.001425).floor())
                .otherwise(0)
                .alias("num"),
            ]
        )
        .with_columns(
            [
                (pl.col("RealizedValue") - pl.col("Cost")).round(0).alias("GainLoss"),
                pl.when(pl.col("Cost") == 0)
                .then(0)
                .otherwise((pl.col("RealizedValue") - pl.col("Cost")) / pl.col("Cost"))
                .round(4)
                .fill_null(0)
                .alias("GainLossPercent"),
                pl.when(pl.col("HoldingType") == 1)
                .then(0)
                .when(pl.col("HoldingType") == 2)
                .then(
                    pl.col("Collateral")
                    + pl.col("MarketValue")
                    - (pl.col("MarketValue") * 0.001425).floor()
                    - pl.col("MarketValue") * 0.003
                )
                .when(pl.col("HoldingType") == 3)
                .then(
                    (pl.col("Collateral") + pl.col("Margin"))
                    / (
                        pl.col("MarketValue")
                        - (pl.col("MarketValue") * 0.001425).floor()
                    )
                )
                .otherwise(0)
                .round(4)
                .alias("MaintenanceRatio"),
            ]
        )
    )


def get_account_stock_df(cursor) -> pl.DataFrame:
    sql = """
        SELECT AccountStocks.*, Stock.ClosingPrice FROM AccountStocks LEFT JOIN Stock ON AccountStocks.StockNo = Stock.StockNo ORDER BY AccountNo, TradingDay, TradingNo
    """
    cursor.execute(sql)
    sql_data = cursor.fetchall()
    list_of_dicts = [
        dict(zip([column[0] for column in cursor.description], row)) for row in sql_data
    ]
    df = pl.DataFrame(data=list_of_dicts, infer_schema_length=10000)
    return account_stock(df)


def get_account_margin(cursor):
    # sql="""UPDATE Account SET MarginAmount = NULL, MarginRemain = NULL, ShortAmount = NULL, ShortRemain = NULL, MaintenanceRatio = NULL, LoanAmount = NULL, LoanRatio = NULL, Amount = NULL, MarketValue = NULL"""
    # cursor.execute(sql)
    sql = """SELECT * FROM Account """
    cursor.execute(sql)
    sql_data = cursor.fetchall()
    list_of_dicts = [
        dict(zip([column[0] for column in cursor.description], row)) for row in sql_data
    ]
    Account = pl.DataFrame(data=list_of_dicts)

    sql = """SELECT Level,MarginLimit,ShortLimit FROM MarginLevel """
    cursor.execute(sql)
    sql_data = cursor.fetchall()
    list_of_dicts = [
        dict(zip([column[0] for column in cursor.description], row)) for row in sql_data
    ]
    Margin = pl.DataFrame(data=list_of_dicts)

    # 取得最近交易日
    cursor.execute(
        f"SELECT TOP (1) Day FROM Schedule WHERE IsClosed=0 and day<='{str(datetime.date.today())}' ORDER BY Day desc"
    )
    open_date = [i._getValue(0).date() for i in cursor.fetchall()][0]

    sql = f"""select * from LoanBalance where AccountDay='{open_date}'"""
    # logger.info(sql)
    cursor.execute(sql)
    sql_data = cursor.fetchall()
    list_of_dicts = [
        dict(zip([column[0] for column in cursor.description], row)) for row in sql_data
    ]

    LoadBalance = pl.DataFrame(data=list_of_dicts)
    m = Account.join(Margin, left_on="MarginLevel", right_on="Level", how="left")
    return m.join(LoadBalance, on="AccountNo", how="left")

    # return Account.join(Margin,left_on='MarginLevel',right_on='Level',how='left')


def summary_account_margin(cursor):
    trade_detail = get_account_stock_df(cursor)
    margin_level = get_account_margin(cursor)
    df_detail = trade_detail.join(margin_level, on="AccountNo", how="left").fill_null(0)
    _ = (
        df_detail.groupby("AccountNo")
        .agg(
            pl.col("Loan").first(),
            pl.col("RealizedValue").sum().alias("MarketValue"),
            pl.col("MarginType").first(),
            pl.col("MarginLimit").first(),
            pl.col("ShortLimit").first(),
            pl.col("MarginAmount").sum().alias("MarginAmount"),
            pl.col("ShortAmount").sum().alias("ShortAmount"),
            pl.when(pl.col("MarginType").first() == 1)
            .then(pl.col("MarginLimit").first() - pl.col("MarginAmount").sum())
            .otherwise(0)
            .alias("MarginRemain"),
            pl.when(pl.col("MarginType").first() == 1)
            .then(pl.col("ShortLimit").first() - pl.col("ShortAmount").sum())
            .otherwise(0)
            .alias("ShortRemain"),
            pl.when(pl.col("num").sum() > 0)
            .then((pl.col("d").sum() / pl.col("num").sum()).round(4))
            .otherwise(0)
            .alias("MaintenanceRatio"),
            pl.col("Cost").sum().alias("CostAmount"),
            # MaintenanceRatio;
        )
        .with_columns(
            [
                pl.when((pl.col("Loan") > 0) & (pl.col("MarketValue") > 0))
                .then((pl.col("MarketValue") - pl.col("Loan")) / pl.col("MarketValue"))
                .otherwise(0)
                .alias("LoanRatio")
            ]
        )
    )
    return _
