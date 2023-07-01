import socket
import hashlib
import random
import time
import threading
import select
import logging
import pandas as pd
from datetime import date
from datetime import datetime
import time
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Marlinspike.42*",
)

cursor = db.cursor()

# This is the Bank class. All bank functions are here.
class BankServer:
    # These are the variables that are used. Most of them are just the parts of the message stripped.
    def __init__(self, details, host_bank) -> None:
        self.message_type = details[0] 
        self.raw_data = details[1:61] 
        self.hashed_data = details[61:93]  
        self.issuing_bank = details[2:7] 
        self.card_no = details[1:17] 
        self.cvv = details[17:20] 
        self.expiry = details[20:24] 
        self.date = details[24:30] 
        self.time = details[30:36] 
        self.card_order_no = details[36:42] 
        self.funds = details[42:46] 
        self.merchant_bank = details[46:51] 
        self.merchantID = details[51:61] 
        self.funds_held = False
        self.no_blacklist = False
        self.host_bank_code = host_bank
        if self.host_bank_code == "53981":
            self.host_bank_name = "bank2"
        elif self.host_bank_code == "55440":
            self.host_bank_name = "bank1"
        else:
            self.host_bank_name = None
        

    # This returns the type of message (1, 0, 9, 8, 7)
    def getMessageType(self):
        return self.message_type
    
    # This returns the id of the issuing bank
    def getIssuingBank(self):
        return self.issuing_bank

    # This returns the id of the merchant bank
    def getMerchantBank(self):
        return self.merchant_bank

    # This returns the details sent (unhashed)
    def getRawDetails(self):
        return self.raw_data
    
    # This returns the hash of the details that are sent
    def getHashedDetails(self):
        return self.hashed_data

    # This returns the card number
    def getCardNo(self):
        return self.card_no

    # This checks the whether the hashed details and details sent are the same
    def checkHash(self):
        # The hashed raw details are collected, hashed and then compared with the actual hashed data
        raw_data = self.getRawDetails()
        original_hash = self.getHashedDetails()
        new_hash = hashlib.md5(raw_data.encode()).hexdigest()
        if new_hash == original_hash:
            # If they're the same then the program returns true
            return True
        else:
            return False

    # This checks whether the card details are in the bank's database
    def checkDetails(self):
        card_no = self.card_no
        cvv = self.cvv
        expiry = self.expiry

        # The cursor makes use of the host bank specified by the program
        use_host_bank = "USE" + " " + self.host_bank_name
        cursor.execute(use_host_bank)
        
        sql = "SELECT CardNo, CVV, DATE_FORMAT(Expiry, '%m%y') FROM CardDetails WHERE CardNo = %s"
        val = (card_no,)
        # Execute the query
        cursor.execute(sql, val)
        result = cursor.fetchone()
        if result:
            # If the details are in the table, the function returns true, lse it returns false
            if str(result[1]) == str(cvv) and str(result[2]) == str(expiry):
                print("returning true")
                return True
            else:
                return False
        else:
            return False

    # This checks whether the details are blacklisted
    def checkBlacklist(self):
        use_host_bank = "USE" + " " + self.host_bank_name
        cursor.execute(use_host_bank)
        card_no = self.getCardNo()
        # An inner join is used to link both the tables to check if the account of the card holder is blacklisted
        query = "SELECT BankDetails.Blacklisted FROM BankDetails INNER JOIN CardDetails ON BankDetails.BankAccNo = CardDetails.BankAccNo WHERE CardDetails.CardNo = %s"
        cursor.execute(query, (card_no,))
        result = cursor.fetchone()

        # If it is, then false is returned. If the account isn't blacklisted, true is returned.
        if result:
            if result[0]:
                return False
            else:
                return True
        else:
            return False

    # This checks whether the card is valid or not
    def checkValidity(self):
        use_host_bank = "USE" + " " + self.host_bank_name
        cursor.execute(use_host_bank)
        card_no = self.getCardNo()
        # The expiry date of the card is selected
        query = "SELECT Expiry FROM CardDetails WHERE CardNo = %s"
        cursor.execute(query, (card_no,))

        result = cursor.fetchone()

        # It is then compared with todays date to see if the card is expired or not
        if result:
            expiry_date = result[0]
            today = date.today()
            if today > expiry_date:
                print("The card has expired.")
                return False
            else:
                print("Card is not expired")
                return True
        else:
            print("The provided card number does not exist in the database.")
            return False
    
    # This function checks whether or not there are sufficient funds in the account
    def checkFunds(self):
        use_host_bank = "USE" + " " + self.host_bank_name
        cursor.execute(use_host_bank)
        card_no = self.getCardNo()
        to_pay = self.funds
        # The query checks if there exists an entry where the funds in a card holder are more than the funds to be payed
        cursor.execute("SELECT CardNo, Funds FROM CardDetails WHERE CardNo = %s AND Funds > %s", (card_no, to_pay))
        # If such an entry does exist (there are sufficient funds in the account) then True is returned, otherwise, false is returned
        row = cursor.fetchall()
        if row:
            return True
        else:
            return False

    # This functions checks if a message is valid and can be authorised
    def validMessage(self):
        # This function executes the functions checkDetails(), checkBlacklist(), checkValidity() and checkFunds()
        # If all the functions return true, then true is returned
        return (self.checkDetails() and
            self.checkBlacklist() and self.checkValidity() and self.checkFunds())
        

class Authorisation(BankServer):
    # The attributes are initialised and the super() method is used to get the attributes of the BankServer class
    def __init__(self, details, host_bank):
        super().__init__(details, host_bank)
        self.true_OTP = False
        self.decrypted_data = details

    # This function generates and sends an OTP to the client
    def sendOTP(self):
        print("generating an OTP....")
        # A socket is created and connected to the client
        ip = socket.gethostbyname(socket.gethostname())
        otp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        otp_socket.connect((ip, 8084))
        # A 6 digit OTP is randomly generated and sent to the client
        sent_OTP = str(random.randint(100000, 999999))
        data = sent_OTP.encode()
        otp_socket.send(data)
        print("OTP sent")
        # An OTP is then recieved and both the OTP that was sent and recieved is returned
        recieved_OTP = otp_socket.recv(10)
        print("OTP recieved")
        return sent_OTP, recieved_OTP
    
    # This verifies whether the OTP provided by the client is valid
    def verifyOTP(self, OTPSent, OTPRecieved):
        try:
            print(OTPSent, type(OTPSent))
            print(OTPRecieved, type(OTPRecieved))
            if int(OTPSent) == int(OTPRecieved):
                return True
            else:
                return False
        except:
            return False

    # This is an SQL query which holds funds in the card details database
    def holdFunds(self):
        use_host_bank = "USE" + " " + self.host_bank_name
        cursor.execute(use_host_bank)
        to_pay = float(self.funds)
        card_no = self.getCardNo()
        # The query updates the coloumns funds and fundsHeld
        update_query = "UPDATE CardDetails SET Funds = Funds - %s, FundsHeld = COALESCE(FundsHeld, 0.0) + %s WHERE CardNo = %s"
        cursor.execute(update_query, (to_pay, to_pay, card_no))
        db.commit()
        return True
    
    # This function adds the details into the trasaction ledger
    def addEntry(self):
        use_host_bank = "USE" + " " + self.host_bank_name
        cursor.execute(use_host_bank)
        cust_id = self.getCardNo()
        acq_id = self.merchantID
        cust_bank = self.getIssuingBank()
        acq_bank =self.getMerchantBank()
        funds = self.funds
        date = self.date
        time = self.time
        message = self.getRawDetails()
        hash = self.getHashedDetails()

        # The previous hash is selected and then added into the trasaction ledger along with the other values
        cursor.execute("SELECT Hash FROM TransactionLedger ORDER BY TransactionNo DESC LIMIT 1")
        prev_hash = "".join(cursor.fetchone())
        values = (cust_id, acq_id, cust_bank, acq_bank, date, time, funds, message, hash, prev_hash, "NO")
        cursor.execute("INSERT INTO TransactionLedger (CustID, AcqID, CustBank, AcqBank, Date, Time, Funds, Message, Hash, PrevHash, Settled) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", values)
        db.commit()

        return True
    
    # This functions handles all the authorisation messages
    def handleAuthorisation(self, host_bank):
        # The issuing bank, merchant bank and decrypted data are all fetched
        issuing_bank = self.getIssuingBank()
        merchant_bank = self.getMerchantBank()
        decrypted_data = self.decrypted_data

        # issuing bank isn't the host bank
        if issuing_bank != host_bank: 
            return "sendToGateway"
        elif issuing_bank == merchant_bank or issuing_bank == host_bank:
            if self.validMessage():
                sent_OTP, recieved_OTP = self.sendOTP()
                print("Checking OTP...")
                valid_otp = self.verifyOTP(sent_OTP, recieved_OTP)
                print(valid_otp)
                if valid_otp == True:
                    # If the OTP is valid then the funds are held and approval is sent.
                    print("OTP is true")
                    funds_held = self.holdFunds()
                    if funds_held == True:
                        new_entry = self.addEntry()
                        print("Entry added. Approval being sent.")
                        return "authorisedPayment"
                    else:
                        return "unauthorisedPayment"
                else:
                    print("Not valid")
                    return "unauthorisedPayment"
            else:
                print("Not valid")
                return "unauthorisedPayment"
        else:
            print("Not valid")   
            return "unauthorisedPayment" 
    
class Settlement(BankServer):
    # The attributes are initialised and the super() method is used to get the attributes of the BankServer class
    def __init__(self, details, host_bank):
        super().__init__(details, host_bank)
        issuing_bank = self.getIssuingBank()
        merchant_bank = self.getMerchantBank()
    
    # This function checks if a payment is authorised or not
    def checkAuthorisedPayments(self):
        use_host_bank = "USE" + " " + self.host_bank_name
        cursor.execute(use_host_bank)
        hash = self.getHashedDetails()
        # It selects the the payment in the transaction ledger that has the hash of the payment to be settled
        query = "SELECT * FROM TransactionLedger WHERE Hash = %s"
        cursor.execute(query, (hash,))

        result = cursor.fetchone()
        if result is not None:
            return True
        else:
            return False

    # This function transfers the funds from the held funds column of the customer to the reserve
    def transferHoldToVisa(self):
        use_host_bank = "USE" + " " + self.host_bank_name
        cursor.execute(use_host_bank)
        to_pay = self.funds
        card_no = self.getCardNo()

        cursor.execute("UPDATE CardDetails SET FundsHeld = FundsHeld - %s WHERE CardNo = %s", (to_pay, card_no))
        db.commit()

        # Add the same to_pay amount to the Funds column in the BankDetails table for the gateway account
        cursor.execute("UPDATE BankDetails SET Funds = Funds + %s WHERE BankAccNo = 1", (to_pay,))
        db.commit()

        return True

    # This function transafers the funds from reserve to the funds in the merchant's bank account
    def transferVisaToMerchant(self):
        use_host_bank = "USE" + " " + self.host_bank_name
        cursor.execute(use_host_bank)
        to_pay = self.funds
        acc_no = self.merchantID
        query = "UPDATE BankDetails SET Funds = Funds - %s WHERE BankAccNo = 1"
        cursor.execute(query, (to_pay,))
        db.commit()

        query = "UPDATE BankDetails SET Funds = Funds + %s WHERE BankAccNo = %s"
        cursor.execute(query, (to_pay, acc_no,))
        db.commit()
        return True

    # This function changes the status of the register in the transaction ledger
    def updateStatus(self):
        use_host_bank = "USE" + " " + self.host_bank_name
        cursor.execute(use_host_bank)
        hash = self.hashed_data
        # It uses the hash of the message to find the entry and change the settled status to 'YES'
        query = "UPDATE `TransactionLedger` SET Settled = 'YES' WHERE Hash = %s"
        values = (hash,)
        print(hash)
        cursor.execute(query, values)
        return True
    
    # This function transfers funds directly from customer to merchant account if they're in the same bank
    def directFundTransfer(self):
        use_host_bank = "USE" + " " + self.host_bank_name
        cursor.execute(use_host_bank)
        to_pay = self.funds
        acc_no = self.merchantID
        card_no = self.getCardNo()
        print(to_pay)
        print(acc_no)
        print(card_no)

        query = "UPDATE CardDetails SET FundsHeld = FundsHeld - %s WHERE CardNo = %s"
        cursor.execute(query, (to_pay, card_no))
        db.commit()

        query = "UPDATE BankDetails SET Funds = Funds + %s WHERE BankAccNo = %s"
        cursor.execute(query, (to_pay, acc_no,))
        db.commit()

        return True
    
    # This function handles the settlement requests recieved
    def handleSettlement(self, host_bank):
        # The issuing bank and merchant bank are fetched
        issuing_bank = self.getIssuingBank()
        merchant_bank = self.getMerchantBank()
        print(host_bank)
        print(issuing_bank)
        print(merchant_bank)
        print(issuing_bank != host_bank)
        # Issuing bank isn't the host bank
        if issuing_bank != host_bank:
            print("reached here")
            return "sendToGateway"
        # Host bank is the merchant bank and the issuing bank
        elif issuing_bank == merchant_bank and issuing_bank == host_bank:
            print("Both customer and merchant are in this bank.\n Direct transfer will take place")
            # The program checks if the payment has been authorised
            valid_payment = self.checkAuthorisedPayments()
            if valid_payment is True:
                #print("I am here")
                # Then it directly transfers the funds
                direct_payment = self.directFundTransfer()
                if direct_payment is True:
                    # Then it updates the status
                    status_updated = self.updateStatus()
                    if status_updated:
                        # If everything returns true, then the direct payment is made
                        return "directPaymentMade"
                    else:
                        # Otherwise failed is returned
                        return "Failed"
                else:
                    print("direct payment didn't happen")
                    return "Failed"
            else:
                print("payment isn't valid")
                return "Failed"
        # Host bank is the issuing back       
        elif issuing_bank == host_bank:
            print("inside here")
            # The program chekcs if the payment has been authorised
            valid_payment = self.checkAuthorisedPayments()
            if valid_payment is True:
                # Then it transfers the funds to the reserve account
                funds_transfered = self.transferHoldToVisa()
                if funds_transfered is True:
                    # Then it updates the status of the payment
                    status_updated = self.updateStatus()
                    if status_updated:
                        # If all processes are successful, then the "heldFundsTransferred" is returned
                        return "heldFundsTransfered"
                    else:
                        # Otherwise, "Failed" is returned
                        return "Failed"
                else:
                    return "Failed"
            else:
                return "Failed"
    
    # This function handles hold requests
    def handleHold(self, host_bank):
        # The issuing bank and the merchant bank are fetched
        issuing_bank = self.getIssuingBank()
        merchant_bank = self.getMerchantBank()
        # The funds are transferred from the reserve to the merchant
        funds_transfered = self.transferVisaToMerchant()
        if funds_transfered == True:
            # If the transfer is succeful the status is updated 
            status_updated = self.updateStatus()
            if status_updated:
                # If the status is updated, the program returns "fundsTransferred"
                return "fundsTransferred"
            else:
                # Otherwise it returns "Failed"
                return "Failed"
        else:
            return "Failed"

class BankEncryption:
    # Initialises the keys for the class
    def __init__(self, gateway_e, gateway_N, bank_d, bank_N):
        self.gateway_e = gateway_e
        self.gateway_N = gateway_N
        self.bank_d = bank_d
        self.bank_N = bank_N
    
    # Encrypts the message to be sent to the gateway
    def encryptMessage(self, msg):
        cipher = ""
        for c in msg:
            m = ord(c)
            cipher += str(pow(m, self.gateway_e, self.gateway_N)) + " "

        return cipher

    # Decrypts the message it's recieved
    def decryptMessage(self, cipher):
        msg = ""
        cipher = str(cipher)
        parts = cipher.split()
        for part in parts:
            if part:
                c = int(part)
                msg += chr(pow(c, self.bank_d, self.bank_N))

        return msg
