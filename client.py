from tkinter import *
from tkinter import simpledialog

import threading
import grpc

import components.components_pb2 as chat
import components.components_pb2_grpc as rpc

address = 'localhost'
port = 11912

class Client:

    def __init__(self, u: str, window):
        self.window = window
        self.username = u

        # Creates gRPC channel
        channel = grpc.insecure_channel(address + ':' + str(port))

        # Creates the Stub for the client
        self.conn = rpc.ChatServerStub(channel)

        # Register the user on the server
        actualUser = chat.User()
        actualUser.username = self.username
        self.conn.Connect(actualUser)

        # Creates a listening thread for get new messages
        threading.Thread(target=self.__listen_for_messages, daemon=True).start()
        self.__setup_ui()
        self.window.mainloop()
        

    def __listen_for_messages(self):
        for mess in self.conn.ChatStream(chat.Empty()):

            # Verify that the actual user and the destinatary is the same
            # only if it is the message display on the UI
            if mess.destinatary == self.username:
                print("New message from: [{}]".format(mess.sender))
                self.chat_list.insert(END, "[{}] {}\n".format(mess.sender, mess.message)) 

    def send_message(self, event):
        # Get data from UI
        destinatary = self.entry_destinatary.get()
        message = self.entry_message.get()

        # If the message is not a empty one, create the protobuf message
        # and send it to the server
        if message != '':
            n = chat.Message()
            n.sender = self.username
            n.destinatary = destinatary
            n.message = message

            print("Sending new message to: [{}]".format(n.destinatary))
            self.conn.SendMessage(n)

    def __setup_ui(self):
        self.chat_list = Text()
        self.chat_list.grid(row=3, column=0, columnspan=4)

        self.lbl_username = Label(self.window, text=self.username)
        self.lbl_username.grid(row=0, column=0, columnspan=4)

        self.lbl_destinatary = Label(self.window, text='Destinatario: ')
        self.lbl_destinatary.grid(row=1, column=0, columnspan=2)
        
        self.entry_destinatary = Entry(self.window, bd=5)
        self.entry_destinatary.focus()
        self.entry_destinatary.grid(row=1, column=2, columnspan=2)

        self.lbl_message = Label(self.window, text='Mensaje: ')
        self.lbl_message.grid(row=2, column=0, columnspan=2)

        self.entry_message = Entry(self.window, bd=5)
        self.entry_message.bind('<Return>', self.send_message)
        self.entry_message.focus()
        self.entry_message.grid(row=2, column=2, columnspan=2)

if __name__ == '__main__':
    root = Tk()
    frame = Frame(root, width=300, height=300)
    frame.grid()
    root.withdraw()
    username = None

    while username is None:
        username = simpledialog.askstring("Nombre de Usuario", "Ingrese su nombre de usuario", parent=root)

    root.deiconify()

    # Start the connection with the open server
    c = Client(username, frame)