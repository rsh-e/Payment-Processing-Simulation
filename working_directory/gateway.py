import socket
import threading
import logging
import colorlog
from gateway_server import *

# This function processes the received message and returns the destination bank
def process_message(message_type, bank_name):
    if message_type in ["9", "8", "7", "1", "0"]:
        # If the message is part of the valid group of messages, then bank2 is returned if the message came from bank 1 and vice versa
        return "bank2" if bank_name == "Bank1" else "bank1"
    else:
        return None

# This function handles communications received by the banks
def handle_bank(conn, bank_name, other_conn):
    logging.debug(f"[{bank_name}] Connected.")
    while True:
        try:
            # Receive an encrypted message from the bank
            encrypted_message = conn.recv(30000).decode()
            if encrypted_message != "":
                # Decrypt the message using GatewayEncryption class
                decrypted_message = crypto.decryptMessage(encrypted_message)
                # Create a GatewayServer object with the decrypted message
                Gateway = GatewayServer(decrypted_message)
                logging.debug(f"[{bank_name}] Received encrypted message: {encrypted_message}")
                logging.debug(f"[{bank_name}] Decrypted Message: {decrypted_message}")
                # Validate the message
                valid_message = Gateway.validMessage()
                if valid_message == True:
                    # If the message is valid, get the message type
                    message_type = Gateway.getMessageType()
                    # Figure out the destination bank with the process function
                    dest_bank = process_message(message_type, bank_name)
                    if dest_bank == "bank1":
                        # If the destination bank is bank 1, encrypt the message and send it to bank 1
                        logging.debug("Forwarding message to bank1")
                        encrypted_message = crypto.encryptBank1(decrypted_message)
                        other_conn.send(encrypted_message.encode())
                    elif dest_bank == "bank2":
                        # If the destination bank is bank 2, encrypt the message and send it to bank 2
                        logging.debug("[Forwarding message to bank2")
                        encrypted_message = crypto.encryptBank2(decrypted_message)
                        other_conn.send(encrypted_message.encode())
                else:
                    #logging.error("Invalid Message")
                    pass
            else:
                #logging.error("Invalid Message")
                pass
        except Exception as e:
            #logging.error(f"[{bank_name}] Error: {e}")
            pass
            
    
    #logging.debug(f"[{bank_name}] Closing connection.")
    #conn.close()

# This function starts listening and processing threads
def start():
    # Set bank_name to None
    global bank_name
    bank_name = None
    # Create a socket for the gateway server and bind it to a port
    gateway = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER = socket.gethostbyname(socket.gethostname())
    PORT1 = 49160
    PORT2 = 49162
    ADDR1 = (SERVER, PORT1)
    ADDR2 = (SERVER, PORT2)

    gateway.bind(ADDR1)
    # Listen for incoming connections from Bank1
    gateway.listen()

    logging.info("Listening for Bank1 connection...")
    # accept a connection from bank 1
    conn1, addr1 = gateway.accept()
    bank_name = "Bank1"
    logging.info("Bank1 connected.")

    # Start a socket for bank1 and listen for a connection
    bank2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bank2.bind(ADDR2)
    bank2.listen()

    logging.info("Listening for Bank2 connection...")
    # Accept the connection from bank 2
    conn2, addr2 = bank2.accept()
    bank_name = "Bank2"
    logging.info("Bank2 connected.")

    # Start threads to handle communication with each bank
    thread1 = threading.Thread(target=handle_bank, args=(conn1, "Bank1", conn2))
    thread2 = threading.Thread(target=handle_bank, args=(conn2, "Bank2", conn1))
    thread1.start()
    thread2.start()

if __name__ == "__main__":
    # Set up logging
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
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.DEBUG)
    
    logging.info("Starting...")

    # Create an object for GatewayEncryption
    crypto = GatewayEncryption()
    # Run the start function
    start()
