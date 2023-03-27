from iqoptionapi.stable_api import IQ_Option
import api
import base64
import time


class IqOption:
    # Construtor da classe
    def __init__(self, id):
        self.id = id
        self.iq_api = None

    # Função para realizar a conexão com a IQ Option
    def connect(self):
        # Obtendo o email e senha da IQ Option
        email = api.get_user_iqoption_email(self.id)
        password = base64.b64decode(api.get_user_iqoption_password(self.id)).decode()

        # Criando uma instância da IQ Option
        self.iq_api = IQ_Option(email, password)

        # Realizando a conexão
        self.iq_api.connect()

    # Função para obter o saldo da conta
    def balance(self):
        return self.iq_api.get_balance()

    # Função para obter a instância da IQ Option
    def instance(self):
        return self.iq_api
