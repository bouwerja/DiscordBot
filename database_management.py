import mysql.connector
import settings as s
import datetime
import calendar

connection = mysql.connector.connect(
        host = s.DATABASE_HOSTNAME, 
        user = s.ACTIVE_USERNAME,
        password = s.ACTIVE_USER_PWD,
        database = s.ACTIVE_DATABASE
        )
def dm_ConnectionStatus():
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