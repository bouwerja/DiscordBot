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
    source_dict = {}
    for i in range(0, len(trans_sources), 1):
        if trans_sources[i][3] == "Discord":
            source_dict[f'{trans_sources[i][0]}'] = trans_sources[i][2]
        else:
            continue

    return source_dict

def cal_Balance(amount):
    cursor, err = connection_status()
    if err:
        print("Failed to connect to database from DM")
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

def save_TransactionData(transSource, transReason, Necessity, PaidToName, amount):
    cursor, err = connection_status()
    if err:
        print("Failed to connect to database.")
        return

    query = """
        INSERT INTO ForFun.FinanceDetail (TransactionSourceID, TransactionReason, IsNecessity, PaidToName, DebitorAmount, Balance)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    balance = cal_Balance(amount)
    if balance is None:
        print("Balance calc error")
    cursor.execute(query, (transSource, transReason, Necessity, PaidToName, amount, balance))
    cursor._connection.commit()

def save_SavingsData(savingscredited, Necessity, amount):
    cursor, err = connection_status()
    if err:
        print("Failed to connect to database.")
        return

    query = """
        INSERT INTO ForFun.FinanceDetail (SavingsCredited, IsNecessity, CreditorAmount, Balance)
        VALUES (%s, %s, %s, %s)
    """
    balance = cal_Balance(amount)
    if balance is None:
        print("Balance calc error")
    cursor.execute(query, (savingscredited, Necessity, amount, balance))
    cursor._connection.commit()

def update_TransactionSource(
        	TransactionName,
        	InfoSource,
        	TransactionNature,
        	IsCreditor ,
        	CompanyName,
        	InterestRate,
        	DateInterestRateUpdated ,
        	ActualContractBalance,
        	CurrentMonthInstalment,
        	ExpectedNextPayment,
        	InterestAmount,
        	DateAmountUpdated,
        	RemainingInstalments,
        	IsCurrentlyPaying,
        	DatePaymentsEnd
        ):
    cursor, err = connection_status()
    if err:
        print("Failed to connect to database.")
        return

    query = """
        INSERT INTO ForFun.TransactionSource (
        	TransactionName,
        	InfoSource,
        	TransactionNature,
        	IsCreditor ,
        	CompanyName,
        	InterestRate,
        	DateInterestRateUpdated ,
        	ActualContractBalance,
        	CurrentMonthInstalment,
        	ExpectedNextPayment,
        	InterestAmount,
        	DateAmountUpdated,
        	RemainingInstalments,
        	IsCurrentlyPaying,
        	DatePaymentsEnd
        )
        VALUES(
        	%s,
        	%s,
        	%s,
        	%s,
        	%s,
        	%s,
        	%s,
        	%s,
        	%s,
        	%s,
        	%s,
        	%s,
        	%s,
        	%s,
        	%s
        );
    """
    cursor.execute(query, (
        	TransactionName,
        	InfoSource,
        	TransactionNature,
        	IsCreditor ,
        	CompanyName,
        	InterestRate,
        	DateInterestRateUpdated ,
        	ActualContractBalance,
        	CurrentMonthInstalment,
        	ExpectedNextPayment,
        	InterestAmount,
        	DateAmountUpdated,
        	RemainingInstalments,
        	IsCurrentlyPaying,
        	DatePaymentsEnd
        ))
    cursor._connection.commit()
