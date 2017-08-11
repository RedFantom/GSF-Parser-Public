# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import socket
from tools.utilities import get_temp_directory
from datetime import datetime
from os import path
import queue


class ClientHandler(object):
    """
    Object that handles the communication with a Client through an *unencrypted* socket
    """
    # TODO: Support encryption for Servers that have certificates
    def __init__(self, sock, address, server_queue):
        """
        :param sock: socket object from server_socket.accept
        :param address: IP-address of the Client (only used for logging purposes)
        :param server_queue: Queue object in which commands are placed
        """
        self.socket = sock
        self.address = address
        self.name = None
        self.role = None
        self.server_queue = server_queue
        # The client_queue is for the server to put commands in
        self.client_queue = queue.Queue()
        # The message_queue is used for communication with the Client
        self.message_queue = queue.Queue()

    def update(self):
        """
        A function to be regularly called by the Server in its loop to perform the basic functionality of the
        ClientHandler. Checks the message_queue and the client_queue, and uses the server_queue.
        """
        if not self.client_queue.empty():
            # The ClientHandler received a command from the server
            # The data is directly sent to the Client of the ClientHandler, as it must either be login/logout for the
            # master Client, or it is a Map operation
            self.write_log("ClientHandler {0} client_queue is not empty".format(self.name))
            server_command = self.client_queue.get()
            self.write_log("ClientHandler received server_command {0}".format(server_command))
            # If the sending of the command fails, end this update()
            # It may have been a one-time error where the pipe was broke, in which case there is no damage by not
            # continuing this cycle. However, the socket may be closed, in which case the close() function is already
            # called and continuing the cycle would result in errors.
            if not self.send(server_command):
                return
        # Call receive() to update the contents of the message_queue
        self.receive()
        # Process *one* message from the message_queue
        if not self.message_queue.empty():
            message = self.message_queue.get()
        else:
            # No messge was received, and thus the cycle ends
            return
        # The message is decoded from bytes into a str
        self.write_log("ClientHandler for {0} received data: {1}".format(self.name, message))
        # The command is processed in a separate function
        self.process_message(message)

    def process_message(self, message):
        """
        Function to process the command received from the Client. See line comments for more details.
        :param message: raw bytes message received
        :return: None
        """
        # First process the raw message
        messaged = message.decode()
        elements = messaged.split("_")
        command = elements[0]

        # Start checking for a command match
        if command == "login":
            # The Client requests a login

            # Check if the data received is valid
            if elements[1] != "master" and elements[1] != "client":
                # The data is not valid, so a disconnect is started
                self.close()
                return
            # The data is valid, and thus the login is accepted and put in the server queue
            self.role = elements[1]
            self.name = elements[2]
            self.write_log("ClientHandler for {0} sent b'login'".format(self.name))
            # Send the response back to the Client to acknowledge the login
            self.socket.send(b"login")
            # Notify the Server of the login
            if self.role == "master":
                self.server_queue.put(("master_login", self))
            else:
                self.server_queue.put(("client_login", self))

        elif command == "strategy":
            # The Client wants to send a Strategy (serialized into a string)

            self.write_log("ClientHandler received a strategy")
            # Elements == ["strategy", serialized_strategy]
            assert len(elements) == 2
            if self.role != "master":
                # Pushing Strategies is something only the master Client can do
                raise RuntimeError("Attempted to share a strategy while not master")
            # Put the request into the server_queue for distribution to other Clients
            self.server_queue.put((message, self))

        elif command == "move":
            # The Client wants to move an item on the Map

            # Elements == ["move", strategy_name, phase_name, item_name, new_x, new_y]
            assert len(elements) == 6
            # Put the request into the server_queue for distribution to other Clients
            self.server_queue.put((message, self))

        elif command == "add":
            # The Client wants to add an item to the Map

            # Elements == ["add", strategy_name, phase_name, item_text, item_font_tuple, item_color_hex]
            assert len(elements) == 6
            # Put the request into the server_queue for distribution to other Clients
            self.server_queue.put((message, self))

        elif command == "del":
            # The Client wants to delete an item from the Map

            # Elements == ["del", strategy_name, phase_name, item_text]
            assert len(elements) == 4
            # Put the request into the server_queue for distribution to other Clients
            self.server_queue.put((message, self))

        elif command == "logout":
            # The Client wants to logout

            # Elements == ["logout"]
            assert len(elements) == 1
            self.close()
        else:
            self.write_log("ClientHandler received unknown command: {0}".format(message))
        return

    def send(self, command):
        """
        Send data to the Client on the other side of the socket. This function processed the data first, as it must be
        sent in a certain format. The data must be sent as a bytes object, ending with a '+' to indicate the end of
        a message to the Client as the socket does *not* separate messages.
        :param command: data to send
        :return: True if successful, False if not
        :raises: ValueError if not one (1) b'_' is found in the command to send (both more and less raise an error)
        """
        self.write_log("ClientHandler sending {0}".format(command))
        if isinstance(command, bytes):
            to_send = command + b"+"
        elif isinstance(command, str):
            string = command + "+"
            to_send = string.encode()
        else:
            raise ValueError("Received invalid type as command: {0}, {1}".format(type(command), command))
        try:
            self.socket.send(to_send)
        except ConnectionError:
            self.close()
            return False
        return True

    def close(self):
        """
        For whatever reason close the socket and notify the server of the logout
        """
        self.write_log("ClientHandler closing")
        self.socket.close()
        self.server_queue.put(("logout", self))

    def write_log(self, line):
        """
        Write a line to the log file, but also check if the log file is not too bit and truncate if required

        Copied from server.strategy_server.write_log(line) but with different file_name
        """
        file_name = path.join(get_temp_directory(), "client_handler_{0}.log".format(self.address))
        if not path.exists(file_name):
            with open(file_name, "w") as fo:
                fo.write("")
        # First read the current contents of the file
        with open(file_name, "r") as fi:
            lines = fi.readlines()
        # Add the line that should be written to the file
        lines.append("[{0}] {1}".format(datetime.now().strftime("%H:%M:%S"), line))
        # Limit the file size to a 1000 lines, and truncate to 800 lines if limit is reached
        if len(lines) > 1000:
            lines = lines[len(lines) - 200:]
        # Write the new contents of the file
        with open(file_name, "w") as fo:
            fo.writelines(lines)
        return

    def receive(self):
        """
        Receives data from the Client in a particular format and then puts the separated messages into the message_queue
        """
        self.socket.setblocking(0)
        total = b""
        while True:
            try:
                message = self.socket.recv(16)
                if message == b"":
                    self.close()
                    break
                self.write_log("ClientHandler received message: {0}".format(message))
            except socket.error:
                break
            elements = message.split(b"+")
            total += elements[0]
            if len(elements) >= 2:
                self.message_queue.put(total)
                for item in elements[1:-1]:
                    self.message_queue.put(item)
                total = elements[-1]
        return











