# Import the required libraries
import socket
import time
import hashlib
import datetime
import mysql.connector

# Connect to the database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Marlinspike.42*",
)

# Create a cursor and select the database to be used
cursor = db.cursor()
cursor.execute("USE merchant")

# Encrypt the message
def encrypt(e, N, message):
    cipher = ""

    for c in message:
        m = ord(c)
        cipher += str(pow(m, e, N)) + " "

    return cipher

# Decrypt the message
def decryptMessage(cipher):
        message = ""
        d = 420963772587006044991205558799
        N = 747992601946009934875593562007

        parts = cipher.split()
        for part in parts:
            if part:
                c = int(part)
                msg += chr(pow(c, d, N))

        return message

# Use a merge sort to sort the payments
def sort_payments(batch, bank_id):
    # If the batch has only one or zero payment(s), it doesn't need to be sorted and is returned.
    if len(batch) <= 1:
        return batch

    # Find the middle index of the batch and split the list into half at that index.
    mid = len(batch) // 2
    left_half = batch[:mid]
    right_half = batch[mid:]

    # Recursively call the merge_sort function on the left and right halves
    left_half = sort_payments(left_half, bank_id)
    right_half = sort_payments(right_half, bank_id)

    # The sorted left and right halves are merged using the merge function,
    return merge(left_half, right_half, bank_id)

# Merge the sorted lists
def merge(left_half, right_half, bank_id):
    # Initialises an empty list to store the merged lists
    result = []
    # Initialises the left and right index for the left and right halves
    left_index = 0
    right_index = 0

    # Iterate through the left and right halves of the lists while they still have elements.
    while left_index < len(left_half) and right_index < len(right_half):
        # Extract the current left and right elements.
        left_string = left_half[left_index]
        right_string = right_half[right_index]

        # If the left element starts with the bank ID and the right element does not:
        if left_string[2:7] == bank_id and right_string[2:7] != bank_id:
            # Append the left element to the result list and increment the left index.
            result.append(left_string)
            left_index += 1
        # If the right element starts with the bank ID and the left element does not:
        elif right_string[2:7] == bank_id and left_string[2:7] != bank_id:
            # Append the right element to the result list and increment the right index.
            result.append(right_string)
            right_index += 1
        # If neither element starts with the bank ID:
        else:
            # Compare the left and right elements and append the smaller one to the result list.
            if left_string < right_string:
                result.append(left_string)
                left_index += 1
            else:
                result.append(right_string)
                right_index += 1
    # Append any remaining elements from the left or right half of the lists.
    result += left_half[left_index:]
    result += right_half[right_index:]
    # Return the merged and sorted list.
    return result

# This functions performs the settlement of the funds
def settlement():
    print("Waiting for fund transfer message...")
    # receives transfer message from client to bank and decodes it
    transfer_message = client2bank.recv(20000).decode()
    #decrypted_message = decryptMessage(transfer_message)
    #print(decrypted_message)
    # extracts hash value from transfer message
    hash = transfer_message[61:93]
    # checks if first character in transfer message is '1', indicating successful fund transfer
    print(transfer_message)
    if transfer_message[0] == '1':
        # connects to merchant database and updates Batch table with 'Settled' = 'YES' for the corresponding hash value
        cursor.execute("USE merchant")
        query = "UPDATE `Batch` SET Settled = 'YES' WHERE Hash = %s"
        values = (hash,)
        print(hash)
        cursor.execute(query, values)
        db.commit()
        print("Funds have been transferred successfully. All accounts are settled.")
    else:
        print("Funds have not been transferred. Try again.")


if __name__ == "__main__":
    # Create the addresses to access the sockets of bank 1 and bank 2
    SERVER = socket.gethostbyname(socket.gethostname())
    PORT_BANK1 = 49161
    ADDR_BANK1 = (SERVER, PORT_BANK1)
    PORT_BANK2 = 49163
    ADDR_BANK2 = (SERVER, PORT_BANK2)

    connect_to_bank1 = True # set to True to connect to Bank1, False to connect to Bank2
    # A bank code is assigned to help the merge sort in sorting the payments
    if connect_to_bank1:
        bank_id = "53981"
    else:
        bank_id = "55440"

    # This is the public key and modulus for bank 1
    bank1_e = 604710583306877
    bank1_N = 403246574997455042743991405701

    # This is the public key and modulus for bank 2
    bank2_e = 751530808771457
    bank2_N = 799152948108675269481101450069

    # This is the private key and modulus for merchant
    client_private = 601357889498540958036731116595
    client_N = 605412704415548500357091026483


    # An empty list of batch orders and encrypted orders
    batch_orders = []
    encrypted_batch_orders = []

    # The orders are selected from the Batch file and are then added onto the batch_orders list
    cursor.execute("SELECT Message, Hash FROM Batch WHERE Settled = 'NO'")
    result = cursor.fetchall()
    
    for i in result:
        full_message = "8" + i[0] + i[1]
        batch_orders.append(full_message)
    
    
    # The orders are then sorted with the payment requests having the merchant bank being given first preference
    sorted_batch_orders = sort_payments(batch_orders, bank_id)
    
    for i in sorted_batch_orders:
        print(i)
    
    print()

    #for i in batch_orders:
    #    print(i)

    
    ###############################################################
    ###############################################################
    

    # The merchant selects address of the bank it will connect to, which has been selected earlier
    if connect_to_bank1:                                           
            bank_addr = ADDR_BANK1                                     
            print("Connecting to Bank1...")                            
    else:                                                           
        bank_addr = ADDR_BANK2                                     
        print("Connecting to Bank2...")                            

    # The merchant connects with the bank socket
    client2bank = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client2bank.connect(bank_addr)                                 
    print("Connected to bank")

    '''
    if connect_to_bank1:                                           
        bank_addr = ADDR_BANK1                                     
        print("Connecting to Bank1...")
        # The order is encrypted and added to the list of encrypted orders                            
        encrypted_order = encrypt(bank1_e, bank1_N, order) 
        client2bank.send(encrypted_order.encode())    
        # The settlement function is then called               
        settlement()  
    else:                                                           
        bank_addr = ADDR_BANK2                                     
        print("Connecting to Bank2...")
        # The order is encrypted and added to the list of encrypted orders                            
        encrypted_order = encrypt(bank2_e, bank2_N, order)     
        client2bank.send(encrypted_order.encode())    
        # The settlement function is then called               
        settlement()  
    ## TEST CODE ONLY

'''   
    # For each order in the sorted orders, the program decides which keys to use to encrypt the data based on where it needs to be sent
    for order in sorted_batch_orders:                                                                                                                   
        if connect_to_bank1:                                           
            bank_addr = ADDR_BANK1                                     
            print("Connecting to Bank1...")
            # The order is encrypted and added to the list of encrypted orders                            
            encrypted_order = encrypt(bank1_e, bank1_N, order) 
            encrypted_batch_orders.append(encrypted_order)
        else:                                                           
            bank_addr = ADDR_BANK2                                     
            print("Connecting to Bank2...")
            # The order is encrypted and added to the list of encrypted orders                            
            encrypted_order = encrypt(bank2_e, bank2_N, order)     
            encrypted_batch_orders.append(encrypted_order) 
                                                                                                             
    if len(encrypted_batch_orders) == 0:
        # If there are no batch orders, then the merchant is notified that there are no payments to settle
        print("All accounts are settled. No more batch payments present.")
    for encrypted_order in encrypted_batch_orders:
        # Otherwise send the encrypted orders one by one to the bank
        client2bank.send(encrypted_order.encode())    
        # The settlement function is then called               
        settlement()  
                     
    #################################################################
    #################################################################
    



