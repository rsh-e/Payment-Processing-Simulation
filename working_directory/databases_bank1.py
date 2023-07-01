# prompts to create tables
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

# create the bank1 database
#cursor.execute("CREATE DATABASE bank1")

# switch to the bank1 database
cursor.execute("USE bank1")

# THE FOLLOWING CODE CREATES ALL THE NECCESSARY TABLES

#create BankDetails table
cursor.execute("CREATE TABLE BankDetails (\
                  BankAccNo BIGINT(10) NOT NULL PRIMARY KEY,\
                  AccType ENUM('business', 'savings', 'personal') NOT NULL,\
                  Name VARCHAR(100) NOT NULL,\
                  DOB DATE NOT NULL,\
                  Funds DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (Funds <= 500000),\
                  AccCreated DATE NOT NULL,\
                  Blacklisted BOOLEAN NOT NULL DEFAULT FALSE\
                  )")

#create the CardDetails table
cursor.execute("CREATE TABLE CardDetails (\
                CardNo BIGINT(16) NOT NULL PRIMARY KEY,\
                BankAccNo BIGINT(10) NOT NULL,\
                CardType ENUM('debit', 'credit') NOT NULL,\
                CVV INT(3) NOT NULL,\
                Expiry DATE NOT NULL,\
                Funds DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (Funds <= 5000),\
                FundsHeld FLOAT,\
                FOREIGN KEY (BankAccNo) REFERENCES BankDetails(BankAccNo))")

#create the TransactionLedger table
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

### THE FOLLOWING CODE ALLOWS YOU TO SEE WHAT SORT OF TABLES AND THEIR SCHEMA ARE IN THE DATABASE
# VIEWING ALL THE DATABASES AND COLOUMS CREATED
cursor.execute("SELECT table_name, column_name, data_type, character_maximum_length, is_nullable \
                FROM information_schema.columns \
                WHERE table_schema = 'bank1' \
                ORDER BY table_name, ordinal_position")

result = cursor.fetchall()
for i in result:
    print(i)

'''

card_no = "4554402769419581" 
cvv = "434" 
expiry = "1201" 


## THE FOLLOWING CODE IS USED TO INSERT VALUES INTO THE DATABASE
'''
card_no = "4554402769419581" 
cvv = "434" 
expiry = "1223" 
date = "130722" 
time = "202314" 
order_no = "000001" 
funds = "200" 
merchant_bank = "53981" # TOGGLE ME
merchant_id = "1234567890"

#acc_number = random.randint(1000000000, 9999999999)
acc_number = "5124911889"
card_type = "debit"
acc_type =  "personal"
expiry = datetime.datetime(1, 12, 2023) # This is not the original value, you have to change it
name =  "Rick Sanchez"
DOB = datetime.datetime(3, 7, 1958)
bank_funds = "1000"
acc_created = datetime.datetime(4, 6, 1990)
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

print("bank details")
cursor.execute("SELECT * FROM BankDetails")
result = cursor.fetchall()
for i in result:
    print(i)

print()
print("card details")
cursor.execue("SELECT * FROM CardDetails")
result = cursor.fetchall()
for i in result:
    print(i)
'''

# THIS CAN BE USED FOR THE HOLD FUNCTIONALITY
'''
cursor.execute("UPDATE CardDetails SET Funds=Funds-10 WHERE CardNo = 4554402769419581")
db.commit()
cursor.execute("SELECT * FROM CardDetails")
result = cursor.fetchall()
for i in result:
    print(i)
'''

'''
## This is for checkDetails in bank_server
sql = "SELECT CardNo, CVV, DATE_FORMAT(Expiry, '%m%y') FROM CardDetails WHERE CardNo = %s"
val = (card_no,)
# Execute the query
cursor.execute(sql, val)
result = cursor.fetchone()
if result:
    if str(result[1]) == str(cvv) and str(result[2]) == str(expiry):
        print("Match found")
    else:
        print("No match found")
else:
    print("Card does not exist")
'''

'''
## THIS IS FOR checkBlacklist  in bank_server
query = "SELECT BankDetails.Blacklisted FROM BankDetails INNER JOIN CardDetails ON BankDetails.BankAccNo = CardDetails.BankAccNo WHERE CardDetails.CardNo = %s"
cursor.execute(query, (card_no,))
result = cursor.fetchone()

if result:
    if result[0]:
        print("The account is blacklisted.")
    else:
        print("The account is not blacklisted.")
else:
    print("The provided card number does not exist in the database.")
'''

'''
## THIS IS TO FOR checkValidity in bank_server
query = "SELECT Expiry FROM CardDetails WHERE CardNo = %s"
cursor.execute(query, (card_no,))

result = cursor.fetchone()

if result:
    expiry_date = result[0]
    today = date.today()
    if today > expiry_date:
        print("The card has expired.")
    else:
        print("The card is valid.")
else:
    print("The provided card number does not exist in the database.")
'''

'''
## THIS IS FOR holdFunds in bank_server
update_query = "UPDATE CardDetails SET Funds = Funds - %s, FundsHeld = COALESCE(FundsHeld, 0.0) + %s WHERE CardNo = %s"
to_pay = float(1)
cursor.execute(update_query, (to_pay, to_pay, card_no))
db.commit()

cursor.execute("SELECT * FROM CardDetails")
result = cursor.fetchone()
print(result)
'''

'''
## THIS IS FOR checkFunds in bank_server
to_pay = 100
cursor.execute("SELECT CardNo, Funds FROM CardDetails WHERE CardNo = %s AND Funds < %s", (card_no, to_pay))
row = cursor.fetchone()

if row:
    print("Not enough funds.")
else:
    print("Sufficient funds")
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
'''
#alter_query = "ALTER TABLE TransactionLedger MODIFY COLUMN Message VARCHAR(255)"
#cursor.execute(alter_query)
#db.commit()

#delete_query = "DELETE FROM TransactionLedger WHERE CustID = %s"
#cursor.execute(delete_query, (card_no,))
#db.commit()

'''
# THIS IS TO ADD AN ENTRY INTO THE TRANSACTION LEDGER
cust_id = card_no
acq_id = 7525812137
cust_bank = 55440
acq_bank = 53981
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

cursor.execute("SELECT * FROM TransactionLedger")
row =  cursor.fetchall()
for i in row:
    print(i)
# close the database connection
db.close()
print("process end.")
'''

'''
## THIS IS TO CREATE AN ACCOUNT FOR THE VISA TRANSFER
acc_number = "0000000001"
acc_type =  "business"
name =  "GATEWAY ACCOUNT"
DOB = datetime(2023, 3, 1)
bank_funds = "100000"
acc_created = datetime(2023, 3, 21)
blacklisted = False
print("made it to here")

cursor.execute("INSERT INTO BankDetails (BankAccNo, AccType, Name, DOB, Funds, AccCreated, Blacklisted)  VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    acc_number, acc_type, name, DOB, bank_funds, acc_created, blacklisted
                ))

db.commit()

cursor.execute("SELECT * FROM BankDetails")
result = cursor.fetchall()
df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
print(df)
'''

'''
## THIS IS for checkAuthorisedPayments
hash = "9b5f167fb9d35faed0c7cbeec6b6360e"
query = "SELECT * FROM TransactionLedger WHERE Hash = %s"
cursor.execute(query, (hash,))

result = cursor.fetchone()
if result is not None:
    print("The transaction with hash value", hash, "has been authorized.")
else:
    print("The transaction with hash value", hash, "has not been authorized.")
'''

'''
## THIS IS FOR TransferHoldToVisa
to_pay = 4
cursor.execute("UPDATE CardDetails SET FundsHeld = FundsHeld - %s WHERE CardNo = %s", (to_pay, card_no))
db.commit()

# Add the same to_pay amount to the Funds column in the BankDetails table for the gateway account
cursor.execute("UPDATE BankDetails SET Funds = Funds + %s WHERE BankAccNo = 1", (to_pay,))
db.commit()

'''

'''
## THIS IF FOR transferVisaToMerchant
to_pay = 4
acc_no = "5124911889"
query = "UPDATE bankDetails SET Funds = Funds - %s WHERE BankAccNo = 1"
cursor.execute(query, (to_pay,))
db.commit()

query = "UPDATE bankDetails SET Funds = Funds + %s WHERE BankAccNo = %s"
cursor.execute(query, (to_pay, acc_no,))
db.commit()
'''

'''
## THIS IS FOR directFundTransfer
to_pay = 4

cursor.execute("UPDATE CardDetails SET FundsHeld = FundsHeld - %s WHERE CardNo = %s", (to_pay, card_no))
db.commit()

# Add the same to_pay amount to the Funds column in the BankDetails table for the gateway account
cursor.execute("UPDATE BankDetails SET Funds = Funds + %s WHERE BankAccNo = %s", (to_pay, acc_no))
db.commit()

mycursor.execute(query, values)
mydb.commit()


cursor.execute("SELECT * FROM CardDetails")
result = cursor.fetchall()
df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
print(df)
print()
print()

cursor.execute("SELECT * FROM BankDetails")
result = cursor.fetchall()
df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
print(df)




db.commit()


