import mysql.connector
import random
from datetime import date
from datetime import datetime
import time
import hashlib
import pandas as pd

# establish database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Marlinspike.42*",
)

cursor = db.cursor()
cursor.execute("USE gateway")


cursor.execute("CREATE DATABASE gateway")
print("created database")

# switch to the bank1 database
cursor.execute("USE gateway")

cursor.execute("CREATE TABLE TransactionLedger (\
                TransactionNo INT(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,\
                CustID BIGINT(16) NOT NULL,\
                AcqID BIGINT(10) NOT NULL,\
                CustBank INT(5) NOT NULL,\
                AcqBank INT(5) NOT NULL,\
                Date DATE NOT NULL,\
                Time TIME NOT NULL,\
                Funds FLOAT NOT NULL,\
                Message VARCHAR(60) NOT NULL,\
                Hash VARCHAR(255) NOT NULL,\
                PrevHash VARCHAR(255) NOT NULL,\
                Settled ENUM('YES', 'NO') NOT NULL DEFAULT 'NO')")
print("created database")


# THIS IS TO CREATE THE GENESIS BLOCK FOR THE TRANSACRTION LEDGER
cust_id = 1000001011011010
acq_id = 1100101011
cust_bank = 10010
acq_bank = 10011
funds = 1101
date = datetime(2023, 3, 21)
time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
message = str(cust_id) + str(acq_id) + str(cust_bank) + str(acq_bank) + str(funds) + str(date) + str(time) 
hash = str(hashlib.md5(message.encode()).hexdigest())
values = (cust_id, acq_id, cust_bank, acq_bank, date, time, funds, message, hash, hash, "NO")


alter_query = "ALTER TABLE TransactionLedger MODIFY COLUMN Message VARCHAR(255)"
cursor.execute(alter_query)
cursor.execute("INSERT INTO TransactionLedger (CustID, AcqID, CustBank, AcqBank, Date, Time, Funds, Message, Hash, PrevHash, Settled) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", values)
db.commit()

print("values altered")

cursor.execute("SELECT * FROM TransactionLedger")
result = cursor.fetchall()
df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
print(df)

card_no = 4554402769419581

cust_id = card_no
acq_id = 7525812137
cust_bank = 55440
acq_bank = 53981
date = datetime(2023, 3, 21)
time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
funds = 56

# This is to add an entry to the table
message = str(cust_id) + str(acq_id) + str(cust_bank) + str(acq_bank) + str(funds) + str(date) + str(time) 
hash = str(hashlib.md5(message.encode()).hexdigest())
cursor.execute("SELECT Hash FROM TransactionLedger ORDER BY TransactionNo DESC LIMIT 1")
prev_hash = "".join(cursor.fetchone())
print(prev_hash)
print(type(prev_hash))
values = (cust_id, acq_id, cust_bank, acq_bank, date, time, funds, message, hash, prev_hash, "NO")

print("entry added")

#execute SQL query
cursor.execute("INSERT INTO TransactionLedger (CustID, AcqID, CustBank, AcqBank, Date, Time, Funds, Message, Hash, PrevHash, Settled) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", values)
db.commit()

print("ANOTHER ENTRY ADDED")




#cursor.execute("SELECT * FROM TransactionLedger")
#result = cursor.fetchall()
#pd.set_option('display.max_columns', None)
#pd.set_option('display.max_rows', None)
#df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
#print(df)

create_table_query = "CREATE TABLE BankCodes (BankID INT(5) NOT NULL, BankName VARCHAR(255) NOT NULL, PRIMARY KEY (BankID))"

# Execute the CREATE TABLE query
cursor.execute(create_table_query)

# Commit the changes to the database
db.commit()


query1 = "INSERT INTO BankCodes (BankID, BankName) VALUES (59381, 'bank1')"
cursor.execute(query1)

# Query 2: Inserting 55440 as bankcode and "bank2" as the name of the bank
query2 = "INSERT INTO BankCodes (BankID, BankName) VALUES (55440, 'bank2')"
cursor.execute(query2)


query = "ALTER TABLE Transactionledger DROP COLUMN Settled, ADD COLUMN MessageType ENUM('authorisation', 'settlement', 'hold') NOT NULL"
cursor.execute(query)

# Commit the changes to the database
db.commit()

print("Done")
cursor.execute("SELECT * FROM TransactionLedger")
result = cursor.fetchall()
df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
print(df)


# Commit the changes to the database
db.commit()

