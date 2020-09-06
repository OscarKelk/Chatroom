from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

clients = {}
addresses = {}
HOST = ''
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)


def accept_incoming_connections():
    # Sets up handling for incoming client connections
    while True:
        client, client_address = SERVER.accept()
        print(f"[Server Info] {client_address} has connected.")
        client.send(bytes("Welcome! Type your name and press enter!", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):  # Takes client socket as argument
    # Handles a client connection
    name = client.recv(BUFSIZ).decode("utf8")
    welcome = "If you ever want to quit, type {quit} to exit."
    client.send(bytes(welcome, "utf8"))
    msg = f"{name} has joined the chatroom, say hello!"
    broadcast(bytes(msg, "utf8"))
    clients[client] = name
    while True:
        msg = client.recv(BUFSIZ)
        if msg != bytes("{quit}", "utf8"):
            broadcast(msg, name+": ")
        else:
            client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]
            broadcast(bytes(f"{name} has left the chatroom.", "utf8"))
            break


def broadcast(msg, prefix=""):  # Takes prefix argument for name identification
    # Broadcasts a message to all clients
    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)
    print(f"[Message] {prefix}{msg}")


if __name__ == "__main__":
    SERVER.listen(5)  # Listens for a maximum of 5 connections
    print("[Server Info] Waiting for incoming connections...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()  # Starts the infinite loop
    ACCEPT_THREAD.join()
    SERVER.close()
