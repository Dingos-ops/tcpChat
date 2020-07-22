#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from socket import socket, SOCK_STREAM, AF_INET
from threading import Thread
from json import loads, dumps
from os import environ
import sys

# Configuração
CONFIG = ("0.0.0.0", int(environ.get("PORT", 5000)))

# Variaveis que vão guardar informações importantes
CONNECTION_LIST = [] # Não altere
MESSAGE_LIST = [] # O valor
USERS_NAMES = {} # Desses três.
TIMEOUT = 0.1 # Quanto maior mais lento e mais facíl de perder pacotes rápidos.
STOP = False # Não altere esse valor.

# Para compabilidade recriei essas duas funções internas
printx = lambda x: sys.stdout.write(str(x) + '\n')
inputx = sys.stdin.readline

# Inicia o objeto do servidor
SERVER = socket(AF_INET, SOCK_STREAM)
try:
    SERVER.bind(CONFIG)
except:
    printx("[!] Falha ao iniciar o servidor, talvez a porta {0[1]} já esteja em uso".format(CONFIG))
    sys.exit(1)
SERVER.settimeout(TIMEOUT)
SERVER.setblocking(False)
SERVER.listen(250)

printx("[*] Servidor iniciado em {0[0]}:{0[1]}".format(CONFIG))

def receive_msg():
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
                    printx("[!] {0[1[1][1]]} saiu do chat".format(USERS_NAMES, client))
                except:
                    continue
                MESSAGE_LIST.append(
                    (
                        dumps(
                            {
                                "type": "text",
                                "name": "Server Info",
                                "text": ["{0[1[1][1]]} saiu do chat".format(USERS_NAMES, client)]
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
                printx("[!] Falha ao transformar a mensagem em objeto")
                continue
            if message_json['type'] == 'test':
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
            printx("[*] Mensagem recebida")
            MESSAGE_LIST.append(
                (
                    message,
                    client[1]
                )
            )

def receive_conn():
    while not STOP:
        try:
            client, addr = SERVER.accept()
        except:
            continue
        printx("[*] Novo client => {0[0]}:{0[1]}".format(addr))
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
    while not STOP:
        for message in MESSAGE_LIST:
            for client in CONNECTION_LIST:
                if client[1] == message[1]:
                    continue
                try:
                    client[0].send(message[0].encode())
                except:
                    printx("[!] Falha ao enviar para {0[1][0]}:{0[1][1]}".format(client))
            MESSAGE_LIST.remove(message)

Thread(target=receive_conn, args=()).start()
Thread(target=receive_msg, args=()).start()
Thread(target=send_all, args=()).start()
printx("Pressione enter 5 vezes para fechar...")

try:
    for stop_count in range(0, 5):
        inputx()
except:
    pass

STOP = True
printx("[!] Servidor fechado")
