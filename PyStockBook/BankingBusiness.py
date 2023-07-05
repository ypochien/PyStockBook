import typing
from loguru import logger
import datetime
import polars as pl


def list_pad_dates(cursor,start_date):
    end_date = datetime.date.today()
    cursor.execute(f"SELECT Day FROM Schedule WHERE day>'{start_date}' AND day<='{end_date}' AND IsClosed=0 ORDER BY Day")
    return [i._getValue(0).date() for i in  cursor.fetchall()]


def latest_loan_data(cursor):
    sql = """SELECT * FROM LoanBalance"""
    cursor.execute(sql)
    sql_data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    # print(columns)
    df = pl.DataFrame(data=list(sql_data.ado_results), schema=columns)
    df = df.sort(["AccountNo","AccountDay"])
    return df.groupby("AccountNo").agg(pl.col("AccountDay").last()
                                ,pl.col("Loan").last()
                                ,pl.col("InterestDate").last()
                                ,pl.col("InterestDays").last()
                                ,pl.col("LoanInterest").last()
                                )


def latest_account(cursor):
    sql = """SELECT AccountNo,LoanRate FROM Account WHERE MarginType=2 AND IsDeleted=0 GROUP BY Account.AccountNo, Account.LoanRate"""
    cursor.execute(sql)
    sql_data = cursor.fetchall()
    list_of_dicts = [dict(zip([column[0] for column in cursor.description], row)) for row in sql_data]
    return pl.DataFrame(data=list_of_dicts)

def current_account_loan(cursor):
    df = latest_account(cursor)
    df = df.join(latest_loan_data(cursor),on="AccountNo",how="left")
    return df

def get_interest_date_and_days(all_open_date,open_date=datetime.date.today()):    
    interest_date = [day for day in all_open_date if day >= open_date][2]
    next_open_date = [day for day in all_open_date if day >= open_date][3]
    return open_date,interest_date, (next_open_date - interest_date).days

def get_pading_loan_data(cursor):
    cursor.execute(f"SELECT Day FROM Schedule WHERE IsClosed=0 and day<='{str(datetime.date.today()+datetime.timedelta(days=30))}' ORDER BY Day")
    all_open_date = [i._getValue(0).date() for i in cursor.fetchall()]
    df = current_account_loan(cursor)

    pad_data = []
    for one_df in df.to_dicts():
        if one_df['AccountDay']:
            relevant_days = [day for day in list_pad_dates(cursor,one_df['AccountDay']) if day > one_df['AccountDay'].date()]
            for date in relevant_days:
                loan_rate = one_df['LoanRate']
                loan = int(one_df['Loan'])
                open_date,interest_date,interest_days = get_interest_date_and_days(all_open_date,date)
                load_interest = 0 if loan <= 0 else round(loan * loan_rate * interest_days)
                new_record = (one_df['AccountNo'], open_date , loan, interest_date , interest_days, load_interest)
                pad_data.append(new_record)
    return pad_data


