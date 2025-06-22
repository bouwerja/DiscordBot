import mysql.connector
import settings as s

connection = mysql.connector.connect(
        host = s.DATABASE_HOSTNAME, 
        user = s.ACTIVE_USERNAME,
        password = s.ACTIVE_USER_PWD,
        database = s.ACTIVE_DATABASE
        )
def connection_status():
    if connection.is_connected():
        mysql_cursor = connection.cursor()
        return mysql_cursor, False
    else:
        return None, True

def get_TransactionSource():
    cursor, err = connection_status()
    if err:
        print("Failed to connect to database.")
        return

    cursor.execute("SELECT * FROM ForFun.TransactionSource")
    result = cursor.fetchall()
    return result

def get_FinanceDetail():
    cursor, err = connection_status()
    if err:
        print("Failed to connect to database.")
        return

    cursor.execute("SELECT * FROM ForFun.FinanceDetail ORDER BY DateRecordCreated DESC LIMIT 10")
    result = cursor.fetchall()
    return result

def get_DiscordSources():
    trans_sources = get_TransactionSource()
    source_list = []
    for i in range(0, len(trans_sources), 1):
        if trans_sources[i][3] == "Discord":
            source_list.append(trans_sources[i][2])
        else:
            continue

    return source_list

def save_TransactionData(transReason, Necessity, PaidToName, amount):
    cursor, err = connection_status()
    if err:
        print("Failed to connect to database.")
        return

    query = """
        INSERT INTO ForFun.FinanceDetail (TransactionReason, IsNecessity, PaidToName, DebitorAmount)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (transReason, Necessity, PaidToName))
    cursor.connection.commit()

