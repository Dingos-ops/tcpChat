#!/usr/bin/env python
# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from socket import socket, AF_INET, SOCK_STREAM
from json import dumps, loads
from random import randint
from time import sleep
from threading import Thread
from json import loads
from urllib.request import urlopen
from re import search
import sys

class Main(App):
    def build(self):
        self.stop = False
        self.home = BoxLayout(orientation='vertical')
        self.user = f'User-{randint(1000, 9999)}'
        self.messages = TextInput(text=f'{self.user}', multiline=True, readonly=False)
        self.input = TextInput(text='Olá', multiline=True)
        self.buttons = BoxLayout(orientation='vertical')
        self.send_button = Button(text='Conectar')
        self.send_button.bind(on_press=lambda *args: self.func_button())
        self.func_button = Thread(target=self.connect_server, args=()).start
        self.exit_button = Button(text='Sair')
        self.exit_button.bind(on_press=lambda *args: self.exit())
        self.home.add_widget(self.messages)
        self.home.add_widget(self.input)
        self.buttons.add_widget(self.send_button)
        self.buttons.add_widget(self.exit_button)
        self.home.add_widget(self.buttons)
        return self.home
    def exit(self):
        self.stop = True
        sys.exit()
    def connect_server(self):
        text = self.messages.text.split('\n')
        self.user = self.messages.text.split('\n')[0].strip()
        if not self.user:
            self.user = f'User-{randint(1000, 9999)}'
        self.messages.text = self.user
        self.messages.readonly = True
        self.messages.text += '\nConectando...'
        self.send_button.text = 'Conectando...'
        self.func_button = lambda: None
        try:
            text = urlopen('http://tsa-whatsapp-bot.herokuapp.com/chat').read().decode()
        except Exception as error:
            self.fail_block(error)
            return
        json = loads(text)
        if json['status']:
            host = json['host']
            port = json['port']
        else:
            self.messages.text += f'\n{json}\nMensagem no telegram com as configurações apagada!'
            self.func_button = lambda *args: self.exit()
            self.send_button.text = 'Sair'
            return
        self.conn = socket(AF_INET, SOCK_STREAM)
        try:
            self.conn.connect((host, port))
            new_user = dumps({'type': 'new_member', 'name': self.user})
            test = dumps({'type': 'test'}).encode()
            self.conn.send(new_user.encode())
        except Exception as error:
            self.messages.text += '\nFalha ao conectar!'
            self.send_button.text = 'Sair'
            self.func_button = lambda *args: self.exit()
        else:
            self.messages.text += '\nConectado!'
            self.send_button.text = 'Enviar'
            self.func_button = self.send_msg
            Thread(target=lambda: self.teste_conn(), args=()).start()
            Thread(target=lambda: self.receive_msg(), args=()).start()
        return None
    def send_msg(self):
        if self.input.text:
            msg = dumps({'type': 'text', 'name': self.user, 'text': self.input.text.strip()})
            try:
                self.conn.send(msg.encode())
            except:
                self.fail_block()
            else:
                self.messages.text += f'\nVocê: -->\n{self.input.text.strip()}\n<--'
                self.input.text = ''
    def fail_block(self, error=None):
        self.send_button.text = 'Sair'
        self.func_button = sys.exit
        if error:
            self.messages.text += 'Erro: -->\n' + str(error) + '\n<--'
        else:
            self.messages.text += '\nFalha de conexão!'
        self.input.readonly = True
        self,stop = True
    def teste_conn(self):
        teste_msg = dumps({'type': 'test', 'name': self.user}).encode()
        while not self.stop:
            try:
                self.conn.send(teste_msg)
            except:
                self.fail_block()
            sleep(1)
    def receive_msg(self):
        self.conn.settimeout(0.4)
        while not self.stop:
            try:
                msg = self.conn.recv(16144)
                msg_json = loads(msg.decode())
            except Exception as error:
                sleep(0.3)
                continue
            if msg_json['type'] == 'text':
                self.messages.text += f"\n{msg_json['name']}: -->\n{msg_json['text']}\n<--"
            elif msg_json['type'] == 'new_member':
                self.messages.text += f"\nNovo membro -> {msg_json['name']}"
            else:
                self.messages.text += f"\nMensagem de {msg_json['name']} não suportada nessa versão"
    def on_pause(self):
        return True

app = Main()
app.run()
