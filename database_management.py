import mysql.connector
import settings as s
import datetime
from datetime import timedelta
import calendar
import yfinance as yf

connection = mysql.connector.connect(
        host = s.DATABASE_HOSTNAME, 
        user = s.ACTIVE_USERNAME,
        password = s.ACTIVE_USER_PWD,
        database = s.ACTIVE_DATABASE
        )
def dm_ConnectionStatus(close=False):
    if connection.is_connected():
        mysql_cursor = connection.cursor()
        return mysql_cursor, False
    else:
        return None, True

def ReacurringUpdates():
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    last_day = calendar.monthrange(year, month)[1]
    date = datetime.date(year, month, last_day)
    while date.weekday() > 4:
        date -= datetime.timedelta(days=1)

    if date.day == datetime.datetime.now(): # Pay day
        cursor, err = dm_ConnectionStatus()
        if err:
            print("Failed to connect to database from DM")
            return
        
        income_query = """
            SELECT SUM(CurrentMonthInstalment) FROM ForFun.TransactionSource ts 
            WHERE TransactionNature = 'Income'
        """
        balance_query = """
            SELECT SUM(Balance) FROM ForFun.FinanceDetail fd
        """
        cursor.execute(income_query)
        income_fetch = cursor.fetchall()
        income_result = income_fetch[0][0]
        cursor.execute(balance_query)
        balance_fetch = cursor.fetchall()
        balance_result = balance_fetch[0][0]
        balance = float(income_result) + float(balance_result)

        insert_query = """
            INSERT INTO ForFun.FinanceDetail (TransactionSourceID , TransactionReason, Balance, CreditorAmount, IsNecessity, PaidToName)
            VALUES(9, 'Monthly Income', %s, %s, 1, %s);
        """
        cursor.execute(insert_query, (balance, income_result, 'Capitec Amount'))
        cursor._connection.commit()
        cursor.close()
        connection.close()
        

def GoldPriceTracking():
    data = yf.Ticker("GLD.JO")
    twoYearPrice = data.history(interval='1d', period='2Y')
    price_dict = {}
    
    for row in range(len(twoYearPrice)):
        date = twoYearPrice.index[row]
        price_dict[f'{date.date()}'] = {
            'ClosePrice': int(twoYearPrice['Close'][row]) / 100,
            'Volume': int(twoYearPrice['Volume'][row])
        }

    select_query = """
    
    """

    insert_query = """
        INSERT INTO ForFun.GoldPrice (Date, ClosePrice, Volume, PriceChange, TwelveMonthMovingAverage, CMA, SeasonalWeighting , LinearRegression, PointForecast, Error)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    return price_dict

def StatusInsert(online_status = 'ONLINE'):
    cursor, err = dm_ConnectionStatus()
    if err:
        print("failed to connect to DataBase")
        return
    
    insert_query = """
        INSERT INTO ForFun.AppStatusLog (LogStatus, AppName)
        VALUES (%s, %s);
    """
    cursor.execute(insert_query, (online_status, 'DISCORD'))
    cursor._connection.commit()
    cursor.close()
    connection.close()

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
    cursor.execute(select_query)
    raw_result = cursor.fetchall()
    latest_status_time = raw_result[0][0]
    prev_status_time = raw_result[1][0]
    restart_timeDelta = latest_status_time - prev_status_time
    restart_timeDelta_float = float(restart_timeDelta.total_seconds())

    hasError = False    # Variable to indicate error
    if restart_timeDelta_float > 3600:
        hasError = True
        StatusInsert('MISSED RESTART')
    
    cursor.close()
    connection.close()
    return latest_status_time, hasError