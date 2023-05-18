import os
import api
from iqoptionapi.stable_api import IQ_Option

def check_win_digital_process(check_id, login, password):
    print('Verificando resultado da negociação Digital: ', check_id)
    iq = IQ_Option(login, password)
    iq.connect()
    while True:
        print('Verificando resultado da negociação Digital: ', check_id)
        check_status, win = iq.check_win_digital_v2(check_id)
        if check_status is True:
            print('Resultado da negociação Digital: ', win)
            return win

def digital_check_win(check_id: int, login: str, password: str, user_id: int, balance: float):
    print('Iniciando verificação do resultado da negociação Digital: ', check_id)
    win = check_win_digital_process(check_id, login, password)
    print('Resultado da negociação Digital: ', win)
    if win < 0:
        print("you loss " + str(win) + "$")
        value_loss = api.get_management_values(user_id)['value_loss']
        new_balance = balance - value_loss
        new_value_loss = value_loss + win
        api.update_management_values_loss(user_id=user_id, balance=new_balance, value_loss=new_value_loss)
    else:
        print("you win " + str(win) + "$")
        value_gain = api.get_management_values(user_id)['value_gain']
        new_balance = balance + value_gain
        new_value_gain = value_gain + win
        api.update_management_values_gain(user_id=user_id, balance=new_balance, value_gain=new_value_gain)

if __name__ == "__main__":
    check_id = int(os.getenv('CHECK_ID'))
    user_id = int(os.getenv('USER_ID'))
    balance = float(os.getenv('BALANCE'))
    login = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    digital_check_win(check_id, login, password, user_id, balance)