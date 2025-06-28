import mysql.connector
import settings as s

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

def cal_Balance(amount):
    cursor, err = dm_ConnectionStatus()
    if err:
        print("Failed to connect to database")
        return
    
    select_query = """
        SELECT fd.Balance
        FROM ForFun.FinanceDetail fd
        ORDER BY FinID DESC
        LIMIT 1
    """
    cursor.execute(select_query)
    current_balance = cursor.fetchall()
    current_balance = float(current_balance[0][0])
    
    new_balance = current_balance - amount
    return new_balance