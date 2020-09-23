import threading
from socket import AF_INET, socket, SOCK_STREAM, gaierror
from threading import Thread
import tkinter
from tkinter import messagebox
import queue


class MessageReceiver(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # Handles message receiving
        while True:
            try:
                msg = client_socket.recv(BUFSIZ).decode("utf8")
                message_queue.put(msg)
            except OSError:  # Possible that client has left the chat
                break


def send(event=None):  # event argument is passed by binders
    # Handles message sending
    msg = my_msg.get()
    my_msg.set("")  # Clears input field
    client_socket.send(bytes(msg, "utf8"))
    if msg == "{quit}":
        client_socket.close()
        top.destroy()


def on_closing(event=None):
    # To be called when gui window is closed
    client_socket.close()
    top.destroy()


def on_closing_connect(event=None):
    # To be called when the connection gui window is closed
    client_socket.close()
    cwindow.destroy()
    top.destroy()


def connect(event=None):
    HOST = hostfieldvar.get()
    PORT = portfieldvar.get()
    if HOST is None or HOST == "Hostname" or HOST == "":
        HOST = "localhost"  # Default host value
    if PORT is None or PORT == "Port" or PORT == "":
        PORT = 33000  # Default port value
    else:
        PORT = int(PORT)
    ADDR = (HOST, PORT)
    try:
        client_socket.connect(ADDR)
        receiver = MessageReceiver()
        receiver.start()
        cwindow.destroy()
    except gaierror:
        tkinter.messagebox.showerror(title=f"Hostname could not be resolved - {HOST}:{PORT}", message="Please check "
                                                                                                      "that you are "
                                                                                                      "attempting to "
                                                                                                      "connect to a "
                                                                                                      "real  address.")
    except ConnectionRefusedError:
        tkinter.messagebox.showerror(title=f"Connection was refused - {HOST}:{PORT}", message="The server you are "
                                                                                              "attempting to connect "
                                                                                              "to may be offline.")


def check_for_messages():
    try:
        msg = message_queue.get(False)  # doesn't block
        msg_list.insert(tkinter.END, msg)
    except queue.Empty:  # raised when queue is empty
        return
    finally:
        top.after(2000, check_for_messages)


def on_entry_click(event):
    # function that gets called whenever entry is clicked
    if hostfield.get() == 'Hostname':
        hostfield.delete(0, "end")  # delete all the text in the entry
        hostfield.insert(0, '')  # Insert blank for user input
        hostfield.config(fg='black')
    if portfield.get() == 'Port':
        portfield.delete(0, "end")  # delete all the text in the entry
        portfield.insert(0, '')  # Insert blank for user input
        portfield.config(fg='black')


def on_focusout(event):
    if hostfield.get() == '':
        hostfield.insert(0, 'Hostname')
        hostfield.config(fg='grey')
    if portfield.get() == '':
        portfield.insert(0, 'Port')
        portfield.config(fg='grey')


cwindow = tkinter.Tk()
cwindow.title("Connect to a chatroom")
cwindow.geometry("200x200")

hostfieldvar = tkinter.StringVar(cwindow)
portfieldvar = tkinter.StringVar(cwindow)

hostfield = tkinter.Entry(cwindow, textvariable=hostfieldvar)
portfield = tkinter.Entry(cwindow, textvariable=portfieldvar)
hostfield.insert(0, 'Hostname')
hostfield.bind('<FocusIn>', on_entry_click)
hostfield.bind('<FocusOut>', on_focusout)
hostfield.config(fg='grey')
portfield.insert(0, 'Port')
portfield.bind('<FocusIn>', on_entry_click)
portfield.bind('<FocusOut>', on_focusout)
portfield.config(fg='grey')
hostfield.pack()
portfield.pack()
connect_button = tkinter.Button(cwindow, text="Connect", command=connect)
connect_button.pack()
cwindow.protocol("WM_DELETE_WINDOW", on_closing_connect)

top = tkinter.Tk()
top.title("Chatroom Client")
top.geometry("500x500")

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar(top)  # For the messages to be sent
my_msg.set("")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages

msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send)
send_button.pack()
top.protocol("WM_DELETE_WINDOW", on_closing)
client_socket = socket(AF_INET, SOCK_STREAM)
BUFSIZ = 1024
message_queue = queue.Queue()
top.after(2000, check_for_messages)
tkinter.mainloop()  # Starts GUI execution





