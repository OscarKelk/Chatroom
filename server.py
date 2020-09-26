from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import sys

if len(sys.argv) > 2:
    print("Error: Too many arguments were supplied; Expected maximum 1")
    exit()


clients = {}
addresses = {}
tags = {}
commands = ["/users"]
HOST = ''
if len(sys.argv) < 2:
    PORT = 33000
else:
    PORT = int(sys.argv[1])
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
        Thread(target=handle_client, args=(client, client_address,)).start()


def handle_client(client, client_address):  # Takes client socket as argument
    # Handles a client connection
    try:
        name = client.recv(BUFSIZ).decode("utf8")
        welcome = "If you ever want to quit, type {quit} to exit."
        client.send(bytes(welcome, "utf8"))
        msg = f"{name} has joined the chatroom, say hello!"
        broadcast(bytes(msg, "utf8"))
        clients[client] = name
        while True:
            msg = client.recv(BUFSIZ)
            if msg.decode().startswith("/"):
                process_command(client, msg.decode())
                continue
            if msg == bytes("{quit}", "utf8"):
                client.send(bytes("{quit}", "utf8"))
                client.close()
                del clients[client]
                broadcast(bytes(f"{name} has left the chatroom.", "utf8"))
                break
            else:
                broadcast(msg, name+": ")
    except ConnectionResetError:
        client.close()
        try:
            del clients[client]
        except KeyError:
            pass
        try:
            broadcast(bytes(f"{name} has left the chatroom.", "utf8"))
        except UnboundLocalError:
            print(f"[Server Info] Connection at {client_address} has disconnected.")


def broadcast(msg, prefix=""):  # Takes prefix argument for name identification
    # Broadcasts a message to all clients
    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)
    print(f"[Message] {prefix}{msg.decode()}")


def process_command(client, msg):
    if msg in commands:
        if msg == "/users":
            client.send(bytes(f"Users in this chatroom:", "utf8"))
            for x in clients.keys():
                client.send(bytes(f"{clients[x]}", "utf8"))
                client.send(bytes(f"   ", "utf8"))
        print(f"[Command] {clients[client]} issued the command: {msg}")

    else:
        client.send(bytes(f"{msg} is not a command!", "utf8"))
        print(f"[Command] {clients[client]} attempted to issue the command: {msg}")


if __name__ == "__main__":
    SERVER.listen(5)  # Listens for a maximum of 5 connections
    print(f"[Server Info] Starting server on port {PORT}")
    print("[Server Info] Waiting for incoming connections...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()  # Starts the infinite loop
    ACCEPT_THREAD.join()
    SERVER.close()
