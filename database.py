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
    try:
        cursor.execute("SELECT * FROM ForFun.Budgeting")
        result = cursor.fetchall()
        return result
    finally:
        cursor.close()

def get_FinanceDetail():
    cursor, err = connection_status()
    if err:
        print("Failed to connect to database.")
        return

    try:
        cursor.execute("SELECT * FROM ForFun.FinanceDetail ORDER BY DateRecordCreated DESC LIMIT 10")
        result = cursor.fetchall()
        return result
    finally:
        cursor.close()

def get_DiscordSources():
    trans_sources = get_TransactionSource()
    source_dict = {}
    for i in range(0, len(trans_sources), 1):
        source_dict[f'{trans_sources[i][0]}'] = trans_sources[i][2]
        
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
    try:
        cursor.execute(select_query)
        current_balance = cursor.fetchall()
        
        current_balance = float(current_balance[0][0])
        new_balance = current_balance - amount

        return new_balance
    finally:
        cursor.close()

def save_TransactionData(transSource, transReason, Necessity, PaidToName, amount):
    cursor, err = connection_status()
    if err:
        print("Failed to connect to database.")
        return

    query = """
        INSERT INTO ForFun.FinanceDetail (BudgetID, TransactionReason, IsNecessity, Notes, DebitorAmount, Balance)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    balance = cal_Balance(amount)
    if balance is None:
        print("Balance calc error")
    
    try:
        cursor.execute(query, (transSource, transReason, Necessity, PaidToName, amount, balance))
        cursor._connection.commit()
    finally:
        cursor.close()

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
    
    try:
        cursor.execute(query, (savingscredited, Necessity, amount, balance))
        cursor._connection.commit()
    finally:
        cursor.close()

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
    
    try:
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
    finally:
        cursor.close()

def get_FinancialStatus():
    cursor, err = connection_status()
    if err:
        print("Error connecting to the database")

    try:
        select_query = """
            SELECT 
                b.BudgetID, 
                b.Description, 
                b.Amount,
                IFNULL(f.AmountSpent, 0) AS AmountSpent,
                IFNULL(b.Amount - f.AmountSpent, b.Amount) AS AmountLeft
            FROM ForFun.Budgeting b
            LEFT JOIN (
                SELECT
                    fd.BudgetID,
                    SUM(CASE 
                        WHEN fd.BudgetID = 13 THEN fd.SavingsCreditAmount
                        WHEN fd.BudgetID = 9 THEN fd.CreditorAmount
                        ELSE fd.DebitorAmount
                    END) AS AmountSpent
                FROM ForFun.FinanceDetail fd 
                WHERE fd.DateRecordCreated >= (
                    SELECT MAX(DateRecordCreated)
                    FROM ForFun.FinanceDetail
                    WHERE BudgetID = 9
                )
                GROUP BY fd.BudgetID
            ) AS f ON f.BudgetID = b.BudgetID
            WHERE b.Active = 1
                AND b.BudgetID <> 9
            ORDER BY b.BudgetID ASC;
        """
        cursor.execute(select_query)
        raw_result = cursor.fetchall()
        result_dict = {}
        for i in range(0, len(raw_result) - 1, 1):
            result_dict[f"{raw_result[i][1]}"] = {
                'Budget' : float(raw_result[i][2]),
                'Spent' : float(raw_result[i][3]),
                'Remaining' : float(raw_result[i][4])
            }
        return result_dict
    finally:
        cursor.close()

def insert_quote(author, quote, datecreated):
    cursor, err = connection_status()
    if err:
        print("Error connecting to the database")

    try:
        insert_query = """
INSERT INTO ForFun.Quotes (Author, Quote, DateRecordCreated)
VALUES (%s, %s, %s)
"""
        
        cursor.execute(insert_query, (author, quote, datecreated))
        cursor._connection.commit()
    
    finally:
        cursor.close()