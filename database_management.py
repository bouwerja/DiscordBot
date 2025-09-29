import mysql.connector
import settings as s
import datetime
from datetime import timedelta
import calendar
import yfinance as yf
from dateutil.relativedelta import relativedelta

connection = mysql.connector.connect(
    host=s.DATABASE_HOSTNAME,
    user=s.ACTIVE_USERNAME,
    password=s.ACTIVE_USER_PWD,
    database=s.ACTIVE_DATABASE,
)


def dm_ConnectionStatus(close=False):
    if connection.is_connected():
        mysql_cursor = connection.cursor()
        return mysql_cursor, False
    else:
        return None, True


def ReacurringUpdates():
    cursor, err = dm_ConnectionStatus()
    if err:
        print("Failed to connect to database from DM")
        return

    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    last_day = calendar.monthrange(year, month)[1]
    date = datetime.date(year, month, last_day)
    while date.weekday() > 4:
        date -= datetime.timedelta(days=1)

    try:
        date = date.strftime("%Y-%m-%d")
        current_date = datetime.datetime.now()
        current_date = current_date.strftime("%Y-%m-%d")
        if date == current_date:  # Pay day
            income_query = """
                SELECT Amount FROM ForFun.Budgeting b
                WHERE Description = 'Income';
            """
            balance_query = """
                SELECT Balance FROM ForFun.FinanceDetail fd
                ORDER BY FinID DESC
                LIMIT 1;
            """
            cursor.execute(income_query)
            income_fetch = cursor.fetchall()
            cursor.execute(balance_query)
            balance_fetch = cursor.fetchall()

            income_result = income_fetch[0][0]
            balance_result = balance_fetch[0][0]
            balance = float(income_result) + float(balance_result)

            insert_query = """
                INSERT INTO ForFun.FinanceDetail (BudgetID , TransactionReason, Balance, CreditorAmount, IsNecessity, Notes)
                VALUES(9, 'Monthly Income', %s, %s, 1, 'Capital Legacy Solutions');
            """
            cursor.execute(insert_query, (balance, income_result))
            cursor._connection.commit()

        current_datetime = datetime.datetime.now()
        if current_datetime.day == 1:  # First of month Expenses and Savings Transfer
            expenses_query = """SELECT BudgetID, Description, Amount FROM ForFun.Budgeting WHERE IsMonthly = 1 AND Active = 1"""
            balance_query = """
                SELECT Balance FROM ForFun.FinanceDetail fd
                ORDER BY FinID DESC
                LIMIT 1;
            """
            cursor.execute(expenses_query)
            expenses = cursor.fetchall()
            cursor.execute(balance_query)
            balance = cursor.fetchall()
            val_balance = float(balance[0][0])

            insert_dict = {}
            for i in range(0, len(expenses), 1):
                amount = float(expenses[i][2])
                new_balance = val_balance - amount
                insert_dict[f"{expenses[i][0]}"] = {
                    "Description": expenses[i][1],
                    "Amount": amount,
                    "Balance": new_balance,
                }
                val_balance = new_balance

            insert_query = """
                INSERT INTO ForFun.FinanceDetail (BudgetID , TransactionReason, Balance, DebitorAmount, IsNecessity, Notes)
                VALUES(%s, %s, %s, %s, 1, 'Monthly Expenses');
            """
            for key, value in insert_dict.items():
                budgetID = key
                transReason = value["Description"]
                credAmount = value["Amount"]
                balance = value["Balance"]

                cursor.execute(
                    insert_query, (budgetID, transReason, balance, credAmount)
                )
                cursor._connection.commit()

    finally:
        cursor.close()


def GoldPriceTracking():
    data = yf.Ticker("GLD.JO")
    twoYearPrice = data.history(interval="1d", period="2Y")
    price_dict = {}

    for row in range(len(twoYearPrice)):
        date = twoYearPrice.index[row]
        price_dict[f"{date.date()}"] = {
            "ClosePrice": int(twoYearPrice["Close"][row]) / 100,
            "Volume": int(twoYearPrice["Volume"][row]),
        }

    select_query = """
    
    """

    insert_query = """
        INSERT INTO ForFun.GoldPrice (Date, ClosePrice, Volume, PriceChange, TwelveMonthMovingAverage, CMA, SeasonalWeighting , LinearRegression, PointForecast, Error)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    return price_dict


def StatusInsert(online_status="ONLINE"):
    cursor, err = dm_ConnectionStatus()
    if err:
        print("failed to connect to DataBase")
        return

    insert_query = """
        INSERT INTO ForFun.AppStatusLog (LogStatus, AppName)
        VALUES (%s, %s);
    """
    try:
        cursor.execute(insert_query, (online_status, "DISCORD"))
        cursor._connection.commit()
    finally:
        cursor.close()


def RestartErrorCheck():
    cursor, err = dm_ConnectionStatus()
    if err:
        print(f"Discrod Bot missed restart at {datetime.datetime.now()}")
        return

    select_query = """
        SELECT DateRecordCreated FROM ForFun.AppStatusLog
        WHERE AppName = 'DISCORD'
        ORDER BY LogID DESC
        LIMIT 2
    """
    try:
        cursor.execute(select_query)
        raw_result = cursor.fetchall()

        latest_status_time = raw_result[0][0]
        prev_status_time = raw_result[1][0]
        restart_timeDelta = latest_status_time - prev_status_time
        restart_timeDelta_float = float(restart_timeDelta.total_seconds())

        hasError = False  # Variable to indicate error
        if restart_timeDelta_float > 3600:
            hasError = True
            StatusInsert("MISSED RESTART")

        return hasError

    finally:
        cursor.close()


"""REACURING EVENTS MANAGEMENT"""


def mth_Income():
    return "Just something"

