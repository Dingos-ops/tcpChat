#!/usr/bin/env python
# -*- coding: utf-8 -*-

from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from json import dumps, loads
from time import sleep
from os import environ

CONFIG = ('0.0.0.0', int(environ.get('PORT', 5000)))
MESSAGES = []
USERS = []
CLIENTS = []
DELAY = 0.1
BUFFER  = 16144
STOP = False

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(CONFIG)
SERVER.settimeout(DELAY)
SERVER.listen(1000)

def receive_msg(client):
    client[0].settimeout(1)
    while not STOP:
        try:
            msg = client[0].recv(BUFFER).decode()
        except:
            continue
        if not msg.strip():
            for user in USERS:
                if user[1] == client[1]:
                    exited = USERS.remove(user)
                    break
            MESSAGES.append({'type': 'text', 'name': 'Server Bot', 'text': '{0} saiu do chat'.format(exited)})
            return
        try:
            msg_json = loads(msg)
        except:
            continue
        if not (msg_json['name'], client[1]) in USERS:
            USERS.append((msg_json['name'], client[1]))
        if msg_json['type'] == 'test':
            pass
        elif msg_json['type'] == 'text' and msg_json['text'].strip() == '/list':
            resp = 'Lista de usuários:'
            for user in USERS:
                resp += '\n>>> {0[0]} <<<'.format(user)
            MESSAGES.append(({'type': 'text', 'name': 'Server bot', 'text': resp}, CONFIG))
        else:
            MESSAGES.append((msg_json, client[1]))
        sleep(DELAY)

def receive_conn():
    while not STOP:
        try:
            client, addr = SERVER.accept()
        except:
            pass
        else:
            client.send(dumps({'type': 'text', 'name': 'Server bot', 'text': 'Seja bem vindo ao chat!'}).encode())
            CLIENTS.append((client, addr))
            Thread(target=lambda: receive_msg((client, addr)), args=()).start()
        sleep(DELAY)

def send_msg():
    while not STOP:
        for msg in MESSAGES:
            for conn in CLIENTS:
                if msg[1] == conn[1]:
                    continue
                for a in range(0, 3):
                    try:
                        conn[0].send(dumps(msg[0]).encode())
                    except:
                        continue
                    else:
                        break
            MESSAGES.remove(msg)
        sleep(DELAY)

Thread(target=receive_conn, args=()).start()
Thread(target=send_msg, args=()).start()
print(f'[*] Servidor iniciado em {CONFIG[0]} => {CONFIG[1]}\nPara fechar pressione CTRL+C...')
while not STOP:
    try:
        sleep(5)
    except:
        STOP = True
STOP = True
