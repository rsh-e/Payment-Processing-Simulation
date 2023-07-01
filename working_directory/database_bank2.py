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

# create the bank2 database
#cursor.execute("CREATE DATABASE bank2")

# switch to the bank2 database
cursor.execute("USE bank2")
'''
# create BankDetails table
cursor.execute("CREATE TABLE BankDetails (\
                  BankAccNo BIGINT(10) NOT NULL PRIMARY KEY,\
                  AccType ENUM('business', 'savings', 'personal') NOT NULL,\
                  Name VARCHAR(100) NOT NULL,\
                  DOB DATE NOT NULL,\
                  Funds DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (Funds <= 500000),\
                  AccCreated DATE NOT NULL,\
                  Blacklisted BOOLEAN NOT NULL DEFAULT FALSE\
                  )")

# create the CardDetails table
cursor.execute("CREATE TABLE CardDetails (\
                CardNo BIGINT(16) NOT NULL PRIMARY KEY,\
                BankAccNo BIGINT(10) NOT NULL,\
                CardType ENUM('debit', 'credit') NOT NULL,\
                CVV INT(3) NOT NULL,\
                Expiry DATE NOT NULL,\
                Funds DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (Funds <= 5000),\
                FundsHeld FLOAT,\
                FOREIGN KEY (BankAccNo) REFERENCES BankDetails(BankAccNo))")

# create the TransactionLedger table
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
'''

#acc_number = random.randint(1000000000, 9999999999)
#print(acc_number)
#4538100000000000
1382907774


card_no = "4538100000000000" 
cvv = "561" 
expiry = "1224" 
date = "130723" 
time = "202314" 
order_no = "000001" 
funds = "300" 
merchant_bank = "53981" # TOGGLE ME
merchant_id = "1234567890"

#acc_number = random.randint(1000000000, 9999999999)
acc_number = "1382907774"
card_type = "debit"
acc_type =  "personal"
expiry = datetime(2024, 12, 1) 
name =  "Morty Smith"
DOB = datetime(3, 7, 1)
bank_funds = "1650"
acc_created = datetime(1990, 9, 19)
blacklisted = False
print("made it to here")

cursor.execute("INSERT INTO BankDetails (BankAccNo, AccType, Name, DOB, Funds, AccCreated, Blacklisted)  VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    acc_number, acc_type, name, DOB, bank_funds, acc_created, blacklisted
                ))

db.commit()
print("made it to here first insertion done")

cursor.execute("INSERT INTO CardDetails (CardNo, BankAccNo, CardType, CVV, Expiry, Funds) VALUES (%s, %s, %s, %s, %s, %s)",
                (
                    card_no, acc_number, card_type, cvv, expiry, funds
                ))
db.commit()
'''
'''
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

alter_query = "ALTER TABLE TransactionLedger MODIFY COLUMN Message VARCHAR(255)"
cursor.execute(alter_query)
db.commit()

values = (cust_id, acq_id, cust_bank, acq_bank, date, time, funds, message, hash, hash, "NO")

#execute SQL query
cursor.execute("INSERT INTO TransactionLedger (CustID, AcqID, CustBank, AcqBank, Date, Time, Funds, Message, Hash, PrevHash, Settled) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", values)
db.commit()

#delete_query = "DELETE FROM TransactionLedger WHERE CustID = %s"
#cursor.execute(delete_query, (card_no,))
#db.commit()

print("Genesis block added")

# THIS IS TO ADD AN ENTRY INTO THE TRANSACTION LEDGER
cust_id = 4538100000000000
acq_id = 1382907774
cust_bank = 53981
acq_bank = 55440
date = datetime(2023, 3, 21)
time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
funds = 56

message = str(cust_id) + str(acq_id) + str(cust_bank) + str(acq_bank) + str(funds) + str(date) + str(time) 
hash = str(hashlib.md5(message.encode()).hexdigest())
cursor.execute("SELECT Hash FROM TransactionLedger ORDER BY TransactionNo DESC LIMIT 1")
prev_hash = "".join(cursor.fetchone())
print(prev_hash)
print(type(prev_hash))
values = (cust_id, acq_id, cust_bank, acq_bank, date, time, funds, message, hash, prev_hash, "NO")

#execute SQL query
cursor.execute("INSERT INTO TransactionLedger (CustID, AcqID, CustBank, AcqBank, Date, Time, Funds, Message, Hash, PrevHash, Settled) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", values)
db.commit()

# close the database connection

print("process end.")


delete_query = "DELETE FROM TransactionLedger WHERE PrevHash = 'c35a9c2f19e1ea0ef9b34d2468a24971'"

# execute the delete query
cursor.execute(delete_query)

cursor.execute("SELECT * FROM BankDetails")
result = cursor.fetchall()
df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
print(df)
print()

cursor.execute("SELECT * FROM CardDetails")
result = cursor.fetchall()
df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
print(df)
print()

cursor.execute("SELECT * FROM TransactionLedger")
result = cursor.fetchall()
df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
print(df)
print()
