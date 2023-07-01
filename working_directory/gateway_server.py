import hashlib
import socket
import time
import mysql.connector
import random
from datetime import date
from datetime import datetime
import pandas as pd
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Marlinspike.42*",
)

cursor = db.cursor()
cursor.execute("USE gateway")

# This is the gateway class
class GatewayServer:
    # These are the attributes used in the program, most of them are breaking apart the message
    def __init__(self, details) -> None:
        self.message_type = details[0] #
        self.raw_data = details[1:61] #
        self.hashed_data = details[61:93] # 
        self.issuing_bank = details[2:7] #
        self.card_no = details[1:17]#
        self.cvv = details[17:20]#
        self.expiry = details[20:24]#
        self.date = details[24:30]#
        self.time = details[30:36]#
        self.card_order_no = details[36:42]#
        self.funds = details[42:46]#
        self.merchant_bank = details[46:51]#
        self.merchantID = details[51:61]#
    
    # The following get the type of message recieved and the IDs of the client and merchant banks along with the details to be checked, the hash and the card no
    def getMessageType(self):
        return self.message_type
    
    # This method returns the ID of the issuing bank
    def getIssuingBank(self):
        return self.issuing_bank
    
    # This method returns the card number
    def getCardNo(self):
        return self.card_no
    
    # This method returns the ID of the merchant bank
    def getMerchantBank(self):
        return self.merchant_bank
    
    # This method returns the raw details of the message
    def getRawDetails(self):
        return self.raw_data
    
    # This method returns the hashed details of the message
    def getHashedDetails(self):
        return self.hashed_data

    # This checks whether the card number is a valid one
    def checkCard(self):
        # Convert the card number to a string and get the last digit (the checksum)
        card = str(self.card_no)
        checksum = int(card[-1])
        # Extract the payload (the first 15 digits) and initialize a sum variable
        payload = card[0:15]
        sum = 0

        # Iterate over the payload digits, starting from the second-to-last and going backwards in steps of 2
        for i in range(len(payload) - 1, 0, -2):
            doubled = int(payload[i]) * 2 # Double the current digit
            if len(str(doubled)) == 2: # If the doubled result is 2 digits long
                doubled_sum = int(str(doubled)[0]) + int(str(doubled)[1]) # Add the individual digits together
                sum = sum + doubled_sum # Add the result to the running sum
            else:
                sum = sum + doubled # Otherwise, just add the doubled result to the sum

        # Double the first digit in the payload
        doubled = int(payload[0]) * 2
        if len(str(doubled)) == 2: # If the result is 2 digits long
            doubled_sum = int(str(doubled)[0]) + int(str(doubled)[1]) # Add the individual digits together
            sum = sum + doubled_sum # Add the result to the running sum
        else:
            sum = sum + doubled # Otherwise, just add the doubled result to the sum
        
        # Iterate over the payload digits, starting from the third-to-last and going backwards in steps of 2
        for i in range(len(payload) - 2, 0, -2):
            sum = sum + int(payload[i]) # Add each digit to the running sum

         # Calculate the received checksum based on the sum
        if sum % 10 == 0:
            recieved_check = 0
        else:
            recieved_check = 10 - (sum % 10)

        # Check if the received checksum matches the expected checksum
        if recieved_check == checksum:
            return True
        else:
            return False

    # This checkes whether the details recieved match the hash
    def checkHash(self):
        raw_data = self.getRawDetails()
        hashed_data = self.getHashedDetails()
        # check the limit for the part of data we'll use
        check_hash = hashlib.md5(raw_data.encode()).hexdigest()
        if check_hash == hashed_data:
            return True
        else:
            return False

    # This function adds the details of payment to the transaction ledger
    def addEntry(self):
        cust_id = self.getCardNo()
        acq_id = self.merchantID
        cust_bank = self.getIssuingBank()
        acq_bank =self.getMerchantBank()
        funds = self.funds
        date = self.date
        time = self.time
        message = self.getRawDetails()
        hash = self.getHashedDetails()

        cursor.execute("USE gateway")
        message_type = self.getMessageType()
        # Find the type of message which is to be inserted into the transaction ledger
        if int(message_type) == 9:
            message_type = "authorisation"
        elif int(message_type) == 8:
            message_type = "settlement"
        elif int(message_type) == 7:
            message_type = "hold"
        elif int(message_type) == 1:
            message_type = "Approval"
        elif int(message_type) == 0:
            message_type = "Disapproval"
        else:
            return False

        # Select the previous hash and insert the details into the transaction ledger
        cursor.execute("SELECT Hash FROM TransactionLedger ORDER BY TransactionNo DESC LIMIT 1")
        prev_hash = "".join(cursor.fetchone())
        values = (cust_id, acq_id, cust_bank, acq_bank, date, time, funds, message, hash, prev_hash, message_type)
        try:
            cursor.execute("INSERT INTO TransactionLedger (CustID, AcqID, CustBank, AcqBank, Date, Time, Funds, Message, Hash, PrevHash, MessageType) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", values)
            db.commit()
        except Exception as e:
            print(e)
        return True

    # This functionchecks whether the banks mentioned in the message exist
    def checkBanks(self):
        # Fetch both issuing banks and merchant banks 
        issuing_bank = self.getIssuingBank()
        merchant_bank = self.merchant_bank

        # Queries the table to check if the issuing  bank is present
        query = f"SELECT BankID FROM BankCodes WHERE BankID = {issuing_bank}"
        cursor.execute(query)
        check_issuing_bank = cursor.fetchone()

        # Queries the table to check if the merchant bank is present
        query = f"SELECT BankID FROM BankCodes WHERE BankID = {merchant_bank}"
        cursor.execute(query)
        check_merchant_bank = cursor.fetchone()
        
        # If both banks exist then true is returned, otherwise false is returned
        if (check_issuing_bank is not None) and (check_merchant_bank is not None):
            return True
        else:
            return False

    # This function executes the checkCard(), addEntry(), checkHash() and checkBanks() subroutine and returns true only if all of them are true
    def validMessage(self):
        return (self.checkCard() and self.addEntry() and self.checkHash() and self.checkBanks())


    
class GatewayEncryption:
    # Initialises the keys
    def __init__(self):
        self.bank1_keys = [604710583306877, 403246574997455042743991405701]
        self.bank2_keys = [751530808771457, 799152948108675269481101450069]
        self.gateway_keys = [420963772587006044991205558799, 747992601946009934875593562007]

        self.bank1_e = self.bank1_keys[0]
        self.bank1_N = self.bank1_keys[1]
        self.bank2_e = self.bank2_keys[0]
        self.bank2_N = self.bank2_keys[1]
        self.gateway_d = self.gateway_keys[0]
        self.gateway_N = self.gateway_keys[1]

    # Encrypts the messages to be sent to bank 1
    def encryptBank1(self, msg):
        cipher = ""
        #e = 604710583306877
        #N = 403246574997455042743991405701

        for c in msg:
            m = ord(c)
            cipher += str(pow(m, self.bank1_e, self.bank1_N)) + " "

        return cipher

    # Encrypts the messages to be sent to bank 2
    def encryptBank2(self, msg):
        cipher = ""
        #e = 751530808771457
        #N = 799152948108675269481101450069

        for c in msg:
            m = ord(c)
            cipher += str(pow(m, self.bank2_e, self.bank2_N)) + " "

        return cipher
    
    '''
    def decryptMessage(self, cipher):
        msg = ""
        gateway_d = 420963772587006044991205558799
        gateway_N = 747992601946009934875593562007
        cipher = str(cipher)
        parts = cipher.split()
        for part in parts:
            if part:
                c = int(part)
                #msg += chr(pow(c, self.gateway_d, self.gateway_N))
                msg += chr(pow(c, gateway_d, gateway_N))
        return msg
    '''

    # Decrypts the messages recieved
    def decryptMessage(self, cipher):
        msg = ""
        #d = 420963772587006044991205558799
        #N = 747992601946009934875593562007
        cipher = str(cipher)
        parts = cipher.split()
        for part in parts:
            if part:
                c = int(part)
                msg += chr(pow(c, 420963772587006044991205558799, 747992601946009934875593562007))

        return msg
