import asyncio
import os
import api
import concurrent.futures
from iqoptionapi.stable_api import IQ_Option


def check_win_digital_process(check_id, iq):
    print('Verificando resultado da negociação Digital: ', check_id)
    while True:
        check_status, win = iq.check_win_digital_v2(check_id)
        if check_status is True:
            return win


async def digital_check_win(check_id: int, iq, user_id: int, balance: float):
    print('Iniciando verificação do resultado da negociação Digital: ', check_id)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        win = await asyncio.get_running_loop().run_in_executor(executor, check_win_digital_process, check_id, iq)
    print('Resultado da negociação Digital: ', win)
    if win < 0:
        print("you loss " + str(win) + "$")
        value_loss = await api.get_management_values(user_id)['value_loss']
        new_balance = balance - value_loss
        new_value_loss = value_loss + win
        await api.update_management_values_loss(user_id=user_id, balance=new_balance, value_loss=new_value_loss)
    else:
        print("you win " + str(win) + "$")
        value_gain = await api.get_management_values(user_id)['value_gain']
        new_balance = balance + value_gain
        new_value_gain = value_gain + win
        await api.update_management_values_gain(user_id=user_id, balance=new_balance, value_gain=new_value_gain)

if __name__ == "__main__":
    iq = IQ_Option('login', 'password')
    iq.connect()
    check_id = int(os.getenv('CHECK_ID'))
    user_id = int(os.getenv('USER_ID'))
    balance = float(os.getenv('BALANCE'))
    asyncio.run(digital_check_win(check_id, iq, user_id, balance))
