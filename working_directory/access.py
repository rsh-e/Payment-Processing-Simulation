import mysql.connector
import pandas as pd
from datetime import date
from datetime import datetime
import hashlib

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Marlinspike.42*",
)

cursor = db.cursor()
## DUE TO POOR NAMING SKILLS BANK1 HAS THE DATA OF BANK2 AND BANK1 HAS THE DATA OF BANK2. THE ORGINAL USE prompts indicate the database being used while the DATABASE prompts tell us which database it actually symbolises.

# This sets the funds to a defualt value
#cursor.execute("UPDATE BankDetails SET Funds=10000 WHERE BankAccNo=1382907774")
#db.commit()

cursor.execute("USE bank1")
cursor.execute("UPDATE `CardDetails` SET FundsHeld = 0 WHERE CardNo = '4539816573456341'")
db.commit()

cursor.execute("USE bank2")

print()
print('-' * 208)
print()
print("DATABASE: BANK1")
print()

print("TABLE: BANK DETAILS")

cursor.execute("SELECT * FROM BankDetails")
result = cursor.fetchall()
df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
print(df)
print()

print("TABLE: CARD DETAILS")
cursor.execute("SELECT * FROM CardDetails")
result = cursor.fetchall()
df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
print(df)
print()

print("TABLE: TRANSACTION LEDGER")
cursor.execute("SELECT * FROM TransactionLedger")
result = cursor.fetchall()
df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
print(df)
print()
print('-' * 208)
print()

# The following blocks resets everything to default values
#cursor.execute("UPDATE BankDetails SET Funds=100000 WHERE BankAccNo=1")
#db.commit()


cursor.execute("USE bank1")
print("DATABASE: BANK2")
print()

print("TABLE: BANK DETAILS")
cursor.execute("SELECT * FROM BankDetails")
result = cursor.fetchall()
df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
print(df)
print()

print("TABLE: CARD DETAILS")
cursor.execute("SELECT * FROM CardDetails")
result = cursor.fetchall()
df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
print(df)
print()

print("TABLE: TRANSACTION LEDGER")
cursor.execute("SELECT * FROM TransactionLedger")
result = cursor.fetchall()
df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
print(df)
print()
print('-' * 208)
print()

cursor.execute("USE gateway")

print("DATABASE: GATEWAY")
print()
print("TABLE: TRANSACATION LEDGER")
cursor.execute("SELECT * FROM TransactionLedger")
result = cursor.fetchall()
df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
print(df)


print("TABLE: BANKCODES")
cursor.execute("SELECT * FROM BankCodes")
result = cursor.fetchall()
df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
print(df)

print()
print('-' * 208)
print()

print("DATABASE: MERCHANT")



cursor.execute("USE merchant")
cursor.execute("")

#cursor.execute("DELETE FROM Batch WHERE Settled='NO'")
#db.commit()

card_no = "4554402769419581" 
cust_bank = card_no[1:6]
cvv = "434" 
expiry = "1223" 
date = (datetime.today()).strftime("%d%m%y")
save_date = date
time = (datetime.now()).strftime("%H%M%S")
save_time = time
order_no = "000001" 
funds = "0070" 
merchant_bank = "53981"
merchant_id = "1382907774"
raw_message = (card_no + cvv + expiry + date + time + order_no + funds + merchant_bank + merchant_id)
hashed_message = hashlib.md5(raw_message.encode()).hexdigest()
'''
# The previous hash is selected
cursor.execute("SELECT Hash FROM Batch ORDER BY TransactionNo DESC LIMIT 1")
prev_hash = "".join(cursor.fetchone())
values = (card_no, merchant_id, cust_bank, merchant_bank, save_date, save_time, funds, raw_message, hashed_message, prev_hash, "NO")

# The details or the payment are inserted into the batch file and are committed.
cursor.execute("INSERT INTO Batch (CustID, AcqID, CustBank, AcqBank, Date, Time, Funds, Message, Hash, PrevHash, Settled) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", values)
db.commit()
'''
cursor.execute("USE merchant")

 #The following resets it all the default values
#cursor.execute("DELETE FROM Batch WHERE Settled='NO'")
#cursor.execute("DELETE FROM Batch WHERE TransactionNo=66")
#db.commit()

print()
print("TABLE: BATCH")
cursor.execute("SELECT * FROM Batch")
result = cursor.fetchall()
df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
print(df)
