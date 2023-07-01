# Import the nessecary libraries
import socket # import the socket library to allow the server to communicate
import threading # import the threading library to create threads
import select # import the select library to manipulate connections
import logging # import the logging library to print logs to the screen
import colorlog # import the colorlog library to print the logs in different colours
from bank_server import * # import all the classes from the bank_server, which includes BankServer(), Authorisation(), Settlement(), BankEncryption()

global host_bank # The global variable is declared so that it can be easily used throughout the code
host_bank = "53981" # This bank server is assigned the bank code, "53981"

# This function processes the messages recieved from the client or the gateway
def process(decrypted_message, source):
    # The host bank code is printed to the screen
    print("below")
    print("Host Bank:", host_bank)
    # Objects of the classes BankServer, Authorisation and Settlement are created
    Bank = BankServer(decrypted_message, host_bank)
    Authorise = Authorisation(decrypted_message, host_bank)
    Settle = Settlement(decrypted_message, host_bank)
    # The message type is retrieved from the message
    message_type = Bank.getMessageType()
    # The bank checks if the hash is correct
    check_hash = Bank.checkHash()
    if check_hash:
        # If the hash is correct, the bank proceeds to identify the type of message it has recieved
        if message_type in ["9", "1", "0"]:
            if message_type == "9":
                # If the bank recieves an authorisation request, it logs it and handles the authorisation
                logging.debug("Recieved authorisation request")
                action = Authorise.handleAuthorisation(host_bank)
                if action == "sendToGateway":
                    # If the function identifies that the customer's account isn't in this bank, then it sends it to the gateway
                    logging.info("Customer not in this bank. Sending message to gateway.")
                    # The message is encrypted and then sent
                    encrypted_message = crypto.encryptMessage(decrypted_message)
                    gateway2bank.send(encrypted_message.encode())
                    logging.debug("Sent to gateway")
                elif action == "authorisedPayment":
                    # If the customer's account is in the bank, and the payment is authorised, it's logged
                    logging.info("Payment is authorised")
                    # An approval message is then sent to either the user or the gateway, by checking the connections queue
                    try:
                        for conn in connections:
                            decrypted_message = "1" + decrypted_message[1:]
                            #encrypted_message = crypto.encryptMessage(decrypted_message)
                            conn.send(decrypted_message.encode())
                        logging.debug("Approval sent to client")
                    except:
                        decrypted_message = "1" + decrypted_message[1:]
                        encrypted_message = crypto.encryptMessage(decrypted_message)
                        gateway2bank.send(encrypted_message.encode())
                        logging.debug("Approval sent to gateway")
                elif action == "unauthorisedPayment":
                    # If the customer's account is in the bank, and the payment is not authorised, it's logged
                    logging.info("Payment is unauthorised")
                    # A disapproval message is then sent to either the user or the gateway, by checking the connections queue
                    try:
                        for conn in connections:
                            decrypted_message = "0" + decrypted_message[1:]
                            #encrypted_message = crypto.encryptMessage(decrypted_message)
                            conn.send(decrypted_message.encode())
                            logging.debug("Disapproval sent to client")
                    except:
                        decrypted_message = "0" + decrypted_message[1:]
                        encrypted_message = crypto.encryptMessage(decrypted_message)
                        gateway2bank.send(encrypted_message.encode())
                        logging.debug("Disapproval sent to gateway")
            ### CHECK IF YOU NEED THE BELOW ###
            else:
                print("The problem is below")
                logging.debug(f"Forwarding message to client")
                for conn in connections:
                    conn.send(message.encode())
            ### CHECK IF YOU NEED THE ABOVE ###

        elif message_type == "8":
            # If the server recieves a settlement request, then it logs it and handles the settlements request
            logging.info("Recieved settlement request")
            action = Settle.handleSettlement(host_bank) 
            if action == "sendToGateway":
                # If the server finds that the customer's account is not in this bank, it sends the message to the gateway
                logging.info("Customer is not in this bank. Sending to gateway.")
                # The message is ecrypted and then sent to the gateway
                encrypted_message = crypto.encryptMessage(decrypted_message)
                gateway2bank.send(encrypted_message.encode())
                logging.debug("Sent to gateway")
            elif action == "directPaymentMade":
                # If the server finds that the merchant's account and the customer's account is in the same bank, then a direct payment is made
                for conn in connections:
                    # An approval messge is then sent to the client using the connections queue
                    decrypted_message = "1" + decrypted_message[1:]
                    conn.send(decrypted_message.encode())
                    logging.debug("Sent to client")
            elif action == "heldFundsTransferred":
                # If the funds are transaferred to the gateway/reserve account, a "hold" message is created by preappending "7" to the message
                logging.info("Funds on hold transferred to Gateway Account")
                decrypted_message = "7" + decrypted_message[1:]
                # The message is then encrypted and sent to the gateway
                encrypted_message = crypto.encryptMessage(decrypted_message)
                gateway2bank.send(encrypted_message.encode())
            else:
                # If any of the tests fail for any reason, a dissproval message is sent to the client using the connections queue
                for conn in connections:
                    decrypted_message = "0" + decrypted_message[1:]
                    conn.send(decrypted_message.encode())
                    logging.debug("Sent to client")


# This function handles messages that are to be recieved by the client
def handle_client(conn, addr):
    # A new connection is added to the connections queue
    logging.info(f"[NEW CONNECTION] {addr} connected.")
    connections.append(conn)

    # A while loop is used to continously recieve messages from the client
    while True:
        # An encyrpted message is recieved
        encrypted_message = conn.recv(30000).decode()
        if encrypted_message != "":
            logging.info("Encrypted Message has been recieved from the gateway: %s", encrypted_message)
            # If the message is not empty, then it's decrypted
            decrypted_message = crypto.decryptMessage(encrypted_message)
            logging.info("Decrypted Message: %s", decrypted_message)
            # The message is then passed into the process function along with the connection
            process(decrypted_message, conn)

    conn.close()
    # Once the client has finished, the connection is removed from the connections queue
    connections.remove(conn)


# This function handles the messages that are recieved from the gateway
def handle_gateway():
    # A while loop is used to recieve messages from the gateway continously
    while True:
        try:
            # Wait to receive message from gateway
            encrypted_message = gateway2bank.recv(30000).decode()
            if encrypted_message != '':
                # Decrypt the received message if it's not empty
                logging.info("Encrypted Message has been recieved from the gateway: %s", encrypted_message)
                decrypted_message = crypto.decryptMessage(encrypted_message)
                logging.info("Decrypted Message: %s", decrypted_message)
                # Check if an approval or disapproval message has been recieved
                if decrypted_message[0] in ["1", "0"]:
                    logging.debug("Approval/Disapproval has been recieved")
                    # If it has been recieved, then the message is sent to the connected client in the queue
                    for conn in connections:
                        conn.send(decrypted_message.encode())
                        logging.debug("Approval/Disapproval sent")
                # Check if a process message has been recieved        
                elif decrypted_message[0] in ["9", "8", "7"]:
                    if decrypted_message[0] == "7":
                        # Create objects of classes BankServer and Settlement if "Hold" message has been recieved
                        Bank = BankServer(decrypted_message, host_bank)
                        Settle = Settlement(decrypted_message, host_bank)
                        logging.info("Recieved hold transfer request")
                        # The request is handled 
                        action = Settle.handleHold(host_bank)
                        print("I have finished that section")
                        # If the funds are transferred into the merchant account, then an approval message is sent
                        if action == "fundsTransferred": 
                            print("I am here")
                            for conn in connections:
                                print("I am nested inside here")
                                print("I am here at the 1 sections")
                                decrypted_message = "1" + decrypted_message[1:]
                                conn.send(decrypted_message.encode())
                                logging.debug("Sent to client")
                        else:
                            # Otherwise, a disapproval message is sent
                            for conn in connections:
                                decrypted_message = "0" + decrypted_message[1:]
                                conn.send(decrypted_message.encode())
                                logging.debug("Sent to client")
                    else:
                        logging.debug("Processing message")
                        process(decrypted_message, source)
                        logging.debug("Sent to gateway")
        except Exception as e:
            # Any trouble in reciveing messages is logged as an error
            logging.error(f"Error while receiving message: {e}")
            break
    gateway2bank.close()

# This function starts the threads
def start():
    client_socket.listen()
    logging.debug("Waiting for client")
    # Use a while loop to accept incoming client connections and start a new thread for each connection
    while True:
        # Check for incoming client connections using select
        readable, _, _ = select.select([client_socket], [], [], 1)
        if client_socket in readable:
            # Accept the client connection and start a new thread to handle the client's requests
            conn_client, addr_client = client_socket.accept()
            thread_client = threading.Thread(target=handle_client, args=(conn_client, addr_client))
            thread_client.start()
        else:
            # Accept the client connection and start a new thread to handle the client's requests
            thread_gateway = threading.Thread(target=handle_gateway, args=())
            thread_gateway.start()

if __name__ == "__main__":
    # Create a handler that will format log messages with colors
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s[%(asctime)s] - %(levelname)s - %(message)s',
        log_colors={
            'DEBUG': 'purple',
            'INFO': 'yellow',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    ))
    # Add the handler to the default logger and set the log level to debug
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.DEBUG)

    logging.info("This is the bank1 server")
    
    # Get the IP address of the current machine
    SERVER = socket.gethostbyname(socket.gethostname())
    # Create a BankEncryption object to encrypt and decrypt messages
    crypto = BankEncryption(666192648131279, 747992601946009934875593562007, 147276700497160985403069405313 , 403246574997455042743991405701)

    # Set up a socket to listen for client connections
    PORT_CLIENT = 49161
    ADDR_CLIENT = (SERVER, PORT_CLIENT)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.bind(ADDR_CLIENT)

    # Set up a socket to connect to the gateway
    PORT_GATEWAY = 49160
    ADDR_GATEWAY = (SERVER, PORT_GATEWAY)
    gateway2bank = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    gateway2bank.connect(ADDR_GATEWAY)
    logging.info("Gateway connected")

    # Create an empty queue to store connections to clients
    connections = []

    logging.info("Starting")
    # Call the start function
    start()
