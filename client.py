#!/usr/bin/env python
# coding: utf-8

"Chat para conversa em grupo usando conexão TCP"

from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from json import dumps, loads
try:
    # Py 3
    from tkinter import Tk, Listbox, Button, Entry, Label, END
except ImportError:
    # Py 2
    from Tkinter import Tk, Listbox, Button, Entry, Label, END
import sys

HOST_NAME = None
HOST_PORT = None
USER_NAME = None
CONNECTION = None
STOP = False

def connect(host_param, port_param, name_param):
    "Conecta de acordo com as informações inseridas"
    global LOGIN_SCREEN, CONNECTION, USER_NAME
    USER_NAME = name_param
    CONNECTION = socket(
        AF_INET,
        SOCK_STREAM
    )
    LOGIN_SCREEN.destroy()
    connecting = Tk()
    connecting.title("Tentando conectar...")
    connecting.resizable(0, 0)
    connect_text = Label(
        connecting,
        text="Conectando..."
    )
    connect_text.pack()
    try:
        CONNECTION.connect(
            (
                host_param,
                int(port_param)
            )
        )
    except Exception as error:
        connect_text.destroy()
        Label(
            connecting,
            text="Falha ao conectar!\nErro: {0}".format(error)
        ).pack()
        Button(
            connecting,
            text="Sair",
            command=sys.exit
        ).pack()
    else:
        connecting.destroy()
    CONNECTION.settimeout(0.1)
    CONNECTION.setblocking(False)

LOGIN_SCREEN = Tk()
LOGIN_SCREEN.geometry("230x200")
LOGIN_SCREEN.resizable(0, 0)
LOGIN_SCREEN.title("Conectar")
Label(
    LOGIN_SCREEN,
    text="IP ou URL do servidor"
).pack()
HOST_ENTRY = Entry(LOGIN_SCREEN)
HOST_ENTRY.pack()
Label(
    LOGIN_SCREEN,
    text="Porta de conexão"
).pack()
PORT_ENTRY = Entry(LOGIN_SCREEN)
PORT_ENTRY.pack()
Label(
    LOGIN_SCREEN,
    text="Apelido no chat"
).pack()
NAME_ENTRY = Entry(LOGIN_SCREEN)
NAME_ENTRY.pack()
Button(
    LOGIN_SCREEN,
    text="Conectar",
    command=lambda: connect(
        HOST_ENTRY.get(),
        PORT_ENTRY.get(),
        NAME_ENTRY.get()
        )
    ).pack()
LOGIN_SCREEN.mainloop()

if not CONNECTION:
    sys.exit(1)

CHAT_SCREEN = Tk()
CHAT_SCREEN.geometry("400x360")
CHAT_SCREEN.resizable(0, 0)
try:
    CHAT_SCREEN.title("Conectado como '{0}'.".format(USER_NAME))
except Exception as error:
    sys.exit("{0}".format(error))
MESSAGE_LIST = Listbox(
    CHAT_SCREEN,
    width=100,
    height=13,
    bg="black",
    fg="white"
)
MESSAGE_LIST.pack()
TEXT_ENTRY = Entry(CHAT_SCREEN)
TEXT_ENTRY.pack()

def receive_msg():
    "Recebe as mensagens e mostra na tela"
    global STOP, CONNECTION, MESSAGE_LIST
    while not STOP:
        try:
            message = CONNECTION.recv(16144)
            message = loads(message.decode("utf-8"))
        except Exception:
            continue
        if message['type'] == 'new_member':
            MESSAGE_LIST.insert(
                0,
                "Novo membro '{0}'".format(message['name'])
            )
        elif message['type'] == 'text':
            for text in message['text']:
                MESSAGE_LIST.insert(
                    0,
                    "--> {0}: {1}".format(message['name'], text)
                )
        else:
            MESSAGE_LIST.insert(
                0,
                "Mensagem de {0} não suportada nessa versão!".format(message['name'])
            )
        continue

def send_msg():
    "Envia as mensagens quando o botão é clicado"
    global STOP, CONNECTION, TEXT_ENTRY, USER_NAME, CHAT_SCREEN, MESSAGE_LIST
    if not TEXT_ENTRY.get().strip():
        return
    message_array = []
    text = TEXT_ENTRY.get()
    temp = ''
    for message in text.split():
        total = len(message) + len(temp)
        if total >= 50:
            message_array.append(temp.strip())
            temp = message
        else:
            temp += ' ' + message
        if message == text.split()[-1]:
            message_array.append(temp.strip())
    message_array.reverse()
    msg = dumps(
        {
            "type": "text",
            "text": message_array,
            "name": USER_NAME
        }
    )
    try:
        CONNECTION.send(msg.encode())
        for message in message_array:
            MESSAGE_LIST.insert(
                0,
                "<-- {0}".format(message)
            )
    except Exception:
        CHAT_SCREEN.destroy()
        alert = Tk()
        alert.title("ERRO!")
        Label(
            alert,
            text="""Ouve algum erro na rede, talvez sua internet esteja
lenta ou o servidor está fora do alcance"""
        ).pack()
        Button(
            alert,
            text="Sair",
            command=alert.destroy
        ).pack()
        STOP = True
    TEXT_ENTRY.delete(
        0,
        END
    )

NEW_MEMBER = dumps(
    {
        "type": "new_member",
        "name": USER_NAME
    }
)
CONNECTION.send(NEW_MEMBER.encode())
Thread(
    target=receive_msg,
    args=()
).start()
Button(
    CHAT_SCREEN,
    text="Enviar",
    command=send_msg
).pack()
CHAT_SCREEN.mainloop()
STOP = True
