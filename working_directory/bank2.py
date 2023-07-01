import socket
import threading
import select
import time
import logging
import colorlog
from bank_server import *

global host_bank
host_bank = "55440"

def process(decrypted_message, sender, conn=None):
    # Create objects using BankServer, Authorisation, and Settlement classes with the decrypted message and host_bank parameter
    Bank = BankServer(decrypted_message, host_bank)
    Authorise = Authorisation(decrypted_message, host_bank)
    Settle = Settlement(decrypted_message, host_bank)
    # Get the message type from Bank object
    message_type = Bank.getMessageType()
    # Check the hash of the message using Bank instance
    check_hash = Bank.checkHash() 
    if check_hash:
        # If the hash is true, check the type of the message
        if message_type in ["9", "1", "0"]:#
            if message_type == "9":
                # If the message type is a "9", handle the authorisation
                logging.debug("Recieved authorisation request")
                action = Authorise.handleAuthorisation(host_bank)
                if action == "sendToGateway":
                    # If the action is send to gateway, encrypt the message and send it to the gateway
                    logging.debug("Sending to the gateway...")
                    encrypted_message = crypto.encryptMessage(decrypted_message)
                    gateway_socket.send(encrypted_message.encode())
                    logging.debug("Sent to gateway")
                    return True
                elif action == "authorisedPayment":
                    # If the customer's account is in this bank and the payment is authorised, an approval message is sent
                    logging.debug("Payment is authorised. Sending approval")
                    # First we try to send it to a connected client, if it does not exist, it's sent to the gateway
                    try:
                        decrypted_message = "1" + decrypted_message[1:]
                        encrypted_message = crypto.encryptMessage(decrypted_message)
                        conn.send(decrypted_message.encode())
                        conn.close()
                    except:
                        decrypted_message = "1" + decrypted_message[1:]
                        encrypted_message = crypto.encryptMessage(decrypted_message)
                        gateway_socket.send(encrypted_message.encode())
                        logging.debug("Sent to gateway")
                elif action == "unauthorisedPayment":
                    # If the customer's account is in this bank but the payment could not be authorised, a disapproval message is sent
                    logging.debug("Payment is unauthorised. Sending disapproval...")
                    try:
                        # First we try to send it to a connected client, if it does not exist, it's sent to the gateway
                        decrypted_message = "0" + decrypted_message[1:]
                        encrypted_message = crypto.encryptMessage(decrypted_message)
                        conn.send(encrypted_message.encode())
                        logging.debug("Sent to client")
                        conn.close()
                    except:
                        decrypted_message = "0" + decrypted_message[1:]
                        encrypted_message = crypto.encryptMessage(decrypted_message)
                        gateway_socket.send(encrypted_message.encode())
                        logging.debug("Sent to gateway")
            else:
                logging.debug("Sending to client")
                conn.send("1".encode())
                logging.debug("sent")
                return True


        elif message_type == "8":
            # If the message recieved is a settlement request, the request is handled
            logging.debug("Recieved settlement request")
            action = Settle.handleSettlement(host_bank)
            print(action)
            if action == "sendToGateway":
                # # If the server finds that the customer's account is not in this bank, it sends the message to the gateway
                logging.debug("Customer is not in this bank")
                # The message is ecrypted and then sent to the gateway
                encrypted_message = crypto.encryptMessage(decrypted_message)
                gateway_socket.send(encrypted_message)
                logging.debug("Sent to gateway")
            elif action == "directPaymentMade":
                # If the server finds that the merchant's account and the customer's account is in the same bank, then a direct payment is made
                decrypted_message = "1" + decrypted_message[1:]
                try:
                    conn.send(decrypted_message.encode())
                    conn.close()
                    logging.debug("Sent to client")
                except:
                    encrypted_message = crypto.encryptMessage(decrypted_message)
                    gateway_socket.send(encrypted_message)
                    logging.debug("Sent to gateway")
            elif action == "heldFundsTransfered":
                # If the funds are transaferred to the gateway/reserve account, a "hold" message is created by preappending "7" to the message
                logging.debug("Funds on hold transferred to Gateway")
                decrypted_message = "7" + decrypted_message[1:]
                # The message is then encrypted and sent to the gateway
                encrypted_message = crypto.encryptMessage(decrypted_message)
                gateway_socket.send(encrypted_message.encode())
            else:
                # If any of the tests fail for any reason, a dissproval message is sent to the client 
                decrypted_message = "0" + decrypted_message[1:]
                print("below is the problem")
                conn.send(decrypted_message.encode())
                conn.close()
                logging.debug("Sent to client")
            return True

        else:
            logging.debug("Invalid")

    
# This function handles messages that are to be recieved by the client
def handle_client(conn, addr):
    logging.info(f"[NEW CONNECTION] {addr} connected.")
    # Start an infinite loop to receive and process messages from the client
    while True:
        try:
            # Receive an encrypted message from the client using the conn.recv() function and store it in the encrypted_message variable
            encrypted_message = conn.recv(30000).decode()
            # If nothing has been recieved, break out of the loop
            if not encrypted_message:
                break
            if encrypted_message != "":
                logging.info("Encrypted Message has been recieved from the gateway: %s", encrypted_message)
                # If the message recieved is not an empty string, decrypt it
                decrypted_message = crypto.decryptMessage(encrypted_message)
                logging.info("Decrypted Message: %s", decrypted_message)
                # Call the process() function with the decrypted_message parameter, the "client" message_type parameter, and the conn=conn parameter, and check if the function returns True or False
                if not process(decrypted_message, "client", conn=conn):
                    conn.send("Invalid message".encode())
        except Exception as e:
            logging.error(f"Error while receiving message: {e}")
            break

    conn.close()

# This function handles the messages that are recieved from the gateway
def handle_gateway(conn):
    # A while loop is used to recieve messages from the gateway continously
    while True:
        try:
            # Wait to receive message from gateway
            encrypted_message = gateway_socket.recv(30000).decode()
            # If nothing has been recived then the loop breaks
            if not encrypted_message:
                break
            if encrypted_message != "":
                logging.info("Encrypted Message has been recieved from the gateway: %s", encrypted_message)
                # Decrypt the received message if it's not empty
                decrypted_message = crypto.decryptMessage(encrypted_message)
                logging.info("Decrypted Message: %s", decrypted_message)
                # Check if an approval or disapproval message has been recieved
                if decrypted_message[0] in ["1", "0"]:
                    logging.debug("Approval/Disapproval has been recieved")
                    # If it has been recieved, then the message is sent to the client in the queue
                    conn.send(decrypted_message.encode())
                    logging.debug("sent")
                else:
                    # Create objects of classes BankServer and Settlement if "Hold" message has been recieved
                    Bank = BankServer(decrypted_message, host_bank)
                    Settle = Settlement(decrypted_message, host_bank)
                    message_type = Bank.getMessageType()
                    if message_type == "7":
                        # If it's a hold transfer messsage, the request is handled
                        logging.debug("Recieved hold transfer request")
                        action = Settle.handleHold(host_bank)
                        if action == "fundsTransferred":
                            # If the funds are transferred into the merchant account, then an approval message is sent
                            decrypted_message = "1" + decrypted_message[1:]
                            encrypted_message = crypto.encryptMessage(decrypted_message)
                            conn.send(encrypted_message)
                            logging.debug("Sent to client")
                            conn.close()
                        else:
                            # If the funds are transferred into the merchant account, then an approval message is sent
                            decrypted_message = "0" + decrypted_message[1:]
                            encrypted_message = crypto.encryptMessage(decrypted_message)
                            conn.send(encrypted_message)
                            logging.debug("Sent to client")
                            conn.close()
                    else:
                        # If the message is a 9 or 8, it goes into the process function
                        process(decrypted_message, "gateway")
        except Exception as e:
            #print("Error is at the gateway thread")
            logging.error(f"Error while receiving message: {e}")
            break

    gateway_socket.close()

# This function starts the threads
def start():
    client_socket.listen()
    logging.info("Waiting for client...")
    conn = None
    # Use a while loop to accept incoming client connections and start a new thread for each connection
    while True:
        # Check for incoming client connections using select
        readable, _, _ = select.select([client_socket], [], [], 1)
        if client_socket in readable:
            # Accept the client connection and start a new thread to handle the client's requests
            conn, addr = client_socket.accept()
            thread_client = threading.Thread(target=handle_client, args=(conn, addr))
            thread_client.start()
        else:
            # Accept the client connection and start a new thread to handle the client's requests
            thread_gateway = threading.Thread(target=handle_gateway, args=(conn,))
            thread_gateway.start()

    client_socket.close()

if __name__ == "__main__":
    # Create a handler that will format log messages with colors
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s[%(asctime)s] - %(levelname)s  - [%(message)s]',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    ))
    # Add the handler to the default logger and set the log level to debug
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.DEBUG)

    logging.info("This is the bank2 server")

    # Get the IP address of the current machine
    SERVER = socket.gethostbyname(socket.gethostname())
    # Create a BankEncryption object to encrypt and decrypt messages
    crypto = BankEncryption(666192648131279, 747992601946009934875593562007, 627138925738717948861294138229, 799152948108675269481101450069)
    
    # Set up a socket to listen for client connections
    PORT_CLIENT = 49163
    ADDR_CLIENT = (SERVER, PORT_CLIENT)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.bind(ADDR_CLIENT)

    # Set up a socket to connect to the gateway
    PORT_GATEWAY = 49162
    ADDR_GATEWAY = (SERVER, PORT_GATEWAY)
    gateway_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    gateway_socket.connect(ADDR_GATEWAY)
    logging.info("Gateway Connected")

    logging.info("Starting...")
    start()
