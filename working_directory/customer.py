import socket
import time
import hashlib
import datetime
import mysql.connector
import sys

# This function encrypts a message to be sent to either bank1 or bank2
def encrypt(e, N, msg):
    cipher = ""

    for c in message:
        m = ord(c)
        cipher += str(pow(m, e, N)) + " "

    return cipher

# This function decrypts message that are received
def decrypt(cipher):
        message = ""
        d = 420963772587006044991205558799
        N = 747992601946009934875593562007

        parts = cipher.split()
        for part in parts:
            if part:
                c = int(part)
                msg += chr(pow(c, d, N))

        return message


# This is code which is used for all authorisation messages
def authorisation():
    # A socket to recieve OTP messages is created
    ip = socket.gethostbyname(socket.gethostname())
    otp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    otp_socket.bind((ip, 8084))
    otp_socket.listen()
    # Once a connection has been recieved, its accepted
    print("Waiting for client socket...")
    otp_socket, address = otp_socket.accept()
    print("Client connected")


    #  The socket recieves the OTP, asks for verification and then sends it back
    print("Listening for otp....")
    data = otp_socket.recv(10) 
    message = data.decode()
    print(message)
    try:
        otp_verification = str(int(input("Input the OTP: ")))
        data = otp_verification.encode()
        otp_socket.send(data)
        otp_socket.close()
    except:
        print("Payment denied")
    
    # This waits for confirmation from the bank about the status of the payment
    print("Waiting for confirmation...")
    try:
        # If the payment is authorised, it's printed to the screen
        confirmation = client2bank.recv(750).decode()
        if confirmation[0] == '1':
            print(confirmation)
            print("Payment authorised")
            return True
        else:
            # Otherwise, a payment denied message is printed to the screen
            print(confirmation)
            print("Payment denied")
    except:
        print()
        print("Payment denied")
    client2bank.close()

def validate(card_no, cvv, expiry, order_no, funds, merchant_bank, merchant_id):
    valid_count = 0
    try:
        if int(card_no) and len(card_no) == 16:
            valid_count = valid_count + 1
        if int(cvv) and len(cvv) == 3:
            valid_count = valid_count + 1
        if int(expiry) and len(expiry) == 4:
            valid_count = valid_count + 1
        if int(order_no) and len(order_no) == 6:
            valid_count = valid_count + 1
        if int(merchant_bank) and len(merchant_bank) == 5:
            valid_count = valid_count + 1
        if int(merchant_id) and len(merchant_id) == 10:
            valid_count = valid_count + 1
        if int(funds) <= 9999 and int(funds) > 0:
            valid_count = valid_count + 1
    except:
        return False
    
    if valid_count == 7:
        return True
    else:
        return False


if __name__ == "__main__":
    db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Marlinspike.42*",
        )

    SERVER = socket.gethostbyname(socket.gethostname())
    PORT_BANK1 = 49161
    ADDR_BANK1 = (SERVER, PORT_BANK1)
    PORT_BANK2 = 49163
    ADDR_BANK2 = (SERVER, PORT_BANK2)

    connect_to_bank1 = True # set to True to connect to Bank1, False to connect to Bank2

    # these are the public and private keys
    bank1_e = 604710583306877
    bank1_N = 403246574997455042743991405701

    bank2_e = 751530808771457
    bank2_N = 799152948108675269481101450069

    client_private = 601357889498540958036731116595
    client_N = 605412704415548500357091026483


    # This is the data to be sent
    
    
    # TEST DATA 1 DATA: Valid EXPECTED OUTPUT: Authorised Transaction
    '''
    connect_to_bank1 = True
    card_no = "4554402769419581" 
    cvv = "434" 
    expiry = "1223" 
    date = (datetime.datetime.today()).strftime("%d%m%y")
    save_date = date
    time = (datetime.datetime.now()).strftime("%H%M%S")
    save_time = time
    order_no = "000001" 
    funds = "0060" 
    merchant_bank = "53981"
    merchant_id = "1382907774"
    cust_bank =  card_no[1:6]
    if validate(card_no, cvv, expiry, order_no, funds, merchant_bank, merchant_id) == True:
        print("Payment has been validated")
        raw_message = (card_no + cvv + expiry + date + time + order_no + funds + merchant_bank + merchant_id)
        print(len(raw_message))
        hashed_message = hashlib.md5(raw_message.encode()).hexdigest()
        print(len(hashed_message))
    else:
        print("Payment not validated")
    '''
    
    
    # TEST DATA 2 DATA: Valid EXPECTED OUTPUT: Authorised Transaction
    connect_to_bank1 = True
    card_no = "4539816573456341" 
    cvv = "561" 
    expiry = "1224" 
    date = (datetime.datetime.today()).strftime("%d%m%y")
    save_date = date
    time = (datetime.datetime.now()).strftime("%H%M%S")
    save_time = time
    order_no = "000001" 
    funds = "0350" 
    merchant_bank = "53981"
    merchant_id = "4124911789"
    cust_bank =  card_no[1:6]
    if validate(card_no, cvv, expiry, order_no, funds, merchant_bank, merchant_id) == True:
        raw_message = (card_no + cvv + expiry + date + time + order_no + funds + merchant_bank + merchant_id)
        print(len(raw_message))
        hashed_message = hashlib.md5(raw_message.encode()).hexdigest()
        print(len(hashed_message))
    else:
        print("Payment not validated")
   
    

    ''' 
    # TEST DATA 3 DATA: Funds Invalid EXPECTED OUTPUT: Unauthorised Transaction
    connect_to_bank1 = False
    card_no = "4554402769419581" 
    cvv = "434" 
    expiry = "1223" 
    date = (datetime.datetime.today()).strftime("%d%m%y")
    save_date = date
    time = (datetime.datetime.now()).strftime("%H%M%S")
    save_time = time
    order_no = "000001" 
    funds = "0000" 
    merchant_bank = "55440" 
    merchant_id = "1382907774" 
    if validate(card_no, cvv, expiry, order_no, funds, merchant_bank, merchant_id) == True:
        raw_message = (card_no + cvv + expiry + date + time + order_no + funds + merchant_bank + merchant_id)
        hashed_message = hashlib.md5(raw_message.encode()).hexdigest()
    else:
        print("Payment not validated")
        sys.exit()
    '''
    
    '''
    # TEST DATA 4 DATA: Funds Invalid EXPECTED OUTPUT: Unauthorised Transaction
    connect_to_bank1 = False
    card_no = "4539816573456341" 
    cvv = "561" 
    expiry = "1224" 
    date = (datetime.datetime.today()).strftime("%d%m%y")
    save_date = date
    time = (datetime.datetime.now()).strftime("%H%M%S")
    save_time = time
    order_no = "000001" 
    funds = "0000" 
    merchant_bank = "55440" # "53981"
    merchant_id = "5124911889" 
    if validate(card_no, cvv, expiry, order_no, funds, merchant_bank, merchant_id) == True:
        raw_message = (card_no + cvv + expiry + date + time + order_no + funds + merchant_bank + merchant_id)
        hashed_message = hashlib.md5(raw_message.encode()).hexdigest()
    else:
        print("Payment not validated") 
        sys.exit()  
    '''
    '''
    # TEST DATA 5 DATA: CardNo Invalid EXPECTED OUTPUT: Unauthorised Transaction
    connect_to_bank1 = False
    card_no = "455449581" 
    cvv = "434" 
    expiry = "1223" 
    date = (datetime.datetime.today()).strftime("%d%m%y")
    save_date = date
    time = (datetime.datetime.now()).strftime("%H%M%S")
    save_time = time
    order_no = "000001" 
    funds = "0100" 
    merchant_bank = "55440" # "53981"
    merchant_id = "1382907774" 
    if validate(card_no, cvv, expiry, order_no, funds, merchant_bank, merchant_id) == True:
        raw_message = (card_no + cvv + expiry + date + time + order_no + funds + merchant_bank + merchant_id)
        hashed_message = hashlib.md5(raw_message.encode()).hexdigest()
    else:
        print("Payment not validated") 
        sys.exit()
    '''

    '''
    # TEST DATA 6 DATA: CardNo Invalid EXPECTED OUTPUT: Unauthorised Transaction
    connect_to_bank1 = False
    card_no = "453981659" 
    cvv = "434" 
    expiry = "1223" 
    date = (datetime.datetime.today()).strftime("%d%m%y")
    save_date = date
    time = (datetime.datetime.now()).strftime("%H%M%S")
    save_time = time
    order_no = "000001" 
    funds = "0000" 
    merchant_bank = "55440" # "53981"
    merchant_id = "5124911889"
    if validate(card_no, cvv, expiry, order_no, funds, merchant_bank, merchant_id) == True: 
        raw_message = (card_no + cvv + expiry + date + time + order_no + funds + merchant_bank + merchant_id)
        hashed_message = hashlib.md5(raw_message.encode()).hexdigest()
    else:
        print("Payment not validated") 
        sys.exit()
    '''
    

    '''
    # TEST DATA 7 DATA: CVV Invalid EXPECTED OUTPUT: Unauthorised Transaction
    connect_to_bank1 = False
    card_no = "4554402769419581" 
    cvv = "562" 
    expiry = "1224" 
    date = (datetime.datetime.today()).strftime("%d%m%y")
    save_date = date
    time = (datetime.datetime.now()).strftime("%H%M%S")
    save_time = time
    order_no = "000001" 
    funds = "0050" 
    merchant_bank = "55440"
    merchant_id = "5124911889" 
    if validate(card_no, cvv, expiry, order_no, funds, merchant_bank, merchant_id) == True:
        raw_message = (card_no + cvv + expiry + date + time + order_no + funds + merchant_bank + merchant_id)
        hashed_message = hashlib.md5(raw_message.encode()).hexdigest()
    else:
        print("Payment not validated")
        exit()
    '''
    

    '''
    # TEST DATA 8 DATA: Expiry Invalid EXPECTED OUTPUT: Unauthorised Transaction
    connect_to_bank1 = True
    card_no = "4539816573456341" 
    cvv = "561" 
    expiry = "1231" 
    date = (datetime.datetime.today()).strftime("%d%m%y")
    save_date = date
    time = (datetime.datetime.now()).strftime("%H%M%S")
    save_time = time
    order_no = "000001" 
    funds = "0050" 
    merchant_bank = "53981"
    merchant_id = "5124911889"
    if validate(card_no, cvv, expiry, order_no, funds, merchant_bank, merchant_id) == True: 
        raw_message = (card_no + cvv + expiry + date + time + order_no + funds + merchant_bank + merchant_id)
        hashed_message = hashlib.md5(raw_message.encode()).hexdigest()
    else:
        print("Payment not validated")
        sys.exit()
    '''
    

    '''    
    # TEST DATA 9 DATA: Funds is "negative" and CardNo is Invalid EXPECTED OUTPUT: Unauthorised Transaction
    connect_to_bank1 = True
    card_no = "45398165-73456341" 
    cvv = "561" 
    expiry = "1224" 
    date = (datetime.datetime.today()).strftime("%d%m%y")
    save_date = date
    time = (datetime.datetime.now()).strftime("%H%M%S")
    save_time = time
    order_no = "000001" 
    funds = "-0050" 
    merchant_bank = "53981"
    merchant_id = "5124911889" 
    if validate(card_no, cvv, expiry, order_no, funds, merchant_bank, merchant_id) == True:
        raw_message = (card_no + cvv + expiry + date + time + order_no + funds + merchant_bank + merchant_id)
        hashed_message = hashlib.md5(raw_message.encode()).hexdigest()
    else:
        print("Payment not validated")
        sys.exit()   
   
   '''
    '''
    # TEST DATA 10 DATA: Card is Expired EXPECTED OUTPUT: Unauthorised Transaction
    connect_to_bank1 = True
    card_no = "4539816573456457" 
    cvv = "334" 
    expiry = "1222" 
    date = (datetime.datetime.today()).strftime("%d%m%y")
    save_date = date
    time = (datetime.datetime.now()).strftime("%H%M%S")
    save_time = time
    order_no = "000001" 
    funds = "0050" 
    merchant_bank = "53981"
    merchant_id = "1382907774" 
    if validate(card_no, cvv, expiry, order_no, funds, merchant_bank, merchant_id) == True:
        raw_message = (card_no + cvv + expiry + date + time + order_no + funds + merchant_bank + merchant_id)
        hashed_message = hashlib.md5(raw_message.encode()).hexdigest()
    else:
        print("Payment not validated")
        sys.exit()
    '''
    



    ###############################################################
    ###############################################################
    message = "9" + raw_message + str(hashed_message) 
                                                          
    print("Message to be sent:", message)   
    # Based on the bank which is connected, the message is encrypted                                          
    if connect_to_bank1:                                           
        bank_addr = ADDR_BANK1                                     
        print("Connecting to Bank1...")                            
        encrypted_message = encrypt(bank1_e, bank1_N, message)     
    else:                                                           
        bank_addr = ADDR_BANK2                                     
        print("Connecting to Bank2...")                            
        encrypted_message = encrypt(bank2_e, bank2_N, message)      

    # A socket is created and connected to the bank         
    client2bank = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client2bank.connect(bank_addr)                                 
    print("Connected to bank")                                     

    # The message is sent
    print("Sending message...")
    client2bank.send(encrypted_message.encode()) 
    # The authorisation function executes and the result of the authorisation is stored in the successful variable                  
    successful = authorisation()
    if successful:
        # If the authorisation is successful, a cursor object is created and the merchant database is used
        cursor = db.cursor()
        cursor.execute("USE merchant")
        cursor.execute("")

        # The previous hash is selected
        cursor.execute("SELECT Hash FROM Batch ORDER BY TransactionNo DESC LIMIT 1")
        prev_hash = "".join(cursor.fetchone())
        values = (card_no, merchant_id, cust_bank, merchant_bank, save_date, save_time, funds, raw_message, hashed_message, prev_hash, "NO")

        # The details or the payment are inserted into the batch file and are committed.
        cursor.execute("INSERT INTO Batch (CustID, AcqID, CustBank, AcqBank, Date, Time, Funds, Message, Hash, PrevHash, Settled) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", values)
        db.commit()
                     
    #################################################################
    #################################################################



