#!/usr/bin/env python3

"Servidor socket TCP para iniciar o chat"

from socket import socket, SOCK_STREAM, AF_INET
from threading import Thread
from json import loads, dumps
from os import environ
import sys

# Configuração
CONFIG = (
    "0.0.0.0",
    int(
        environ.get(
            "PORT",
            5000
        )
    )
)

# Variaveis que vão guardar informações importantes
CONNECTION_LIST = []
MESSAGE_LIST = []
USERS_NAMES = {}
TIMEOUT = 0.1
STOP = False # Não altere esse valor

# Inicia o objeto do servidor
SERVER = socket(
    AF_INET,
    SOCK_STREAM
)
try:
    SERVER.bind(CONFIG)
except:
    print(f"[!] Falha ao iniciar o servidor, talvez a porta {CONFIG[1]} já esteja em uso")
    sys.exit(1)
SERVER.settimeout(TIMEOUT)
SERVER.setblocking(False)
SERVER.listen()

print(f"[*] Servidor iniciado em {CONFIG[0]}:{CONFIG[1]}")

def receive_msg():
    "Quando receber mensagem de qualquer usuario"
    global CONNECTION_LIST, MESSAGE_LIST
    while not STOP:
        for client in CONNECTION_LIST:
            try:
                message = client[0].recv(16144)
                message = message.decode()
            except:
                continue
            if not message:
                CONNECTION_LIST.remove(client)
                try:
                    print(f"[!] {USERS_NAMES[client[1][1]]} saiu do chat")
                except:
                    continue
                MESSAGE_LIST.append(
                    (
                        dumps(
                            {
                                "type": "text",
                                "name": "Server Info",
                                "text": [f"{USERS_NAMES[client[1][1]]} saiu do chat"]
                            }
                        ),
                        (
                            "localhost",
                            5000
                        )
                    )
                )
                USERS_NAMES.pop(client[1][1])
                continue
            try:
                message_json = loads(message)
            except:
                print("[!] Falha ao transformar a mensagem em objeto")
                continue
            USERS_NAMES[client[1][1]] = message_json["name"]

            if "text" in message_json and message_json["text"] == ["/list"]:
                users = ["Lista de usuarios:"]
                for user in USERS_NAMES:
                    users.append(USERS_NAMES[user])
                users.reverse()
                MESSAGE_LIST.append(
                    (
                        dumps(
                            {
                                "type": "text",
                                "name": "Server Bot",
                                "text": users
                            }
                        ),
                        (
                            "localhost",
                            5000
                        )
                    )
                )
                continue
            print("[*] Mensagem recebida")
            MESSAGE_LIST.append(
                (
                    message,
                    client[1]
                )
            )

def receive_conn():
    "Fica aguardando novas conexões"
    global CONNECTION_LIST, SERVER, TIMEOUT
    while not STOP:
        try:
            client, addr = SERVER.accept()
        except:
            continue
        print(f"[*] Novo client => {addr[0]}:{addr[1]}")
        client.settimeout(TIMEOUT)
        client.setblocking(False)
        msg = dumps(
            {
                "type": "text",
                "name": "Server Bot",
                "text": ["Seja bem vindo ao chat!"]
            }
        )
        client.send(msg.encode())
        CONNECTION_LIST.append((client, addr))

def send_all():
    "Espalha as mensagens recebidas"
    global CONNECTION_LIST, MESSAGE_LIST, SERVER
    while not STOP:
        for message in MESSAGE_LIST:
            for client in CONNECTION_LIST:
                if client[1] == message[1]:
                    continue
                try:
                    client[0].send(message[0].encode())
                except:
                    print(f"[!] Falha ao enviar para {client[1][0]}:{client[1][1]}")
            MESSAGE_LIST.remove(message)

Thread(target=receive_conn, args=()).start()
Thread(target=receive_msg, args=()).start()
Thread(target=send_all, args=()).start()
print("Pressione enter 5 vezes para fechar...")

try:
    for stop_count in range(0, 5):
        input()
except:
    pass

STOP = True
print("[!] Servidor fechado")
