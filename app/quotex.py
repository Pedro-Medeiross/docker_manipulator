from quotexapi.stable_api import Quotex
import api
import base64
import time
import os


class QuotexApi:
    # Construtor da classe
    def __init__(self, id):
        self.id = id
        self.qt_api = None

    # Função para realizar a conexão com a IQ Option
    def connect(self):
        # Obtendo o email e senha da IQ Option
        email = os.getenv('EMAIL')
        password = base64.b64decode(os.getenv('PASSWORD')).decode()

        # Criando uma instância da IQ Option
        self.qt_api = Quotex(email, password)

        # Realizando a conexão
        self.qt_api.connect()
        print(self.qt_api)

    # Função para obter o saldo da conta
    def balance(self):
        return self.qt_api.get_balance()

    # Função para obter a instância da IQ Option
    def instance(self):
        return self.qt_api

    def set_account_type(self):
        self.qt_api.change_account(os.getenv('ACCOUNT_TYPE'))
