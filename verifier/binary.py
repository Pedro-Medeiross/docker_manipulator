import asyncio
import os
import api
import multiprocessing
import concurrent.futures
from iqoptionapi.stable_api import IQ_Option


def check_win_process(check_id, queue, iq):
    while True:
        check_status, win = iq.check_win_v4(check_id)
        if check_status is True:
            queue.put(win)
            break


async def binary_check_win(check_id: int, iq, user_id: int, balance: float):
    print('Verificando resultado da negociação Binária: ', check_id)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        queue = multiprocessing.Manager().Queue()
        executor.submit(check_win_process, check_id, queue, iq)

    while True:
        if not queue.empty():
            win = queue.get()
            break
        else:
            await asyncio.sleep(0.1)

    if win == 'loose':
        print("you loss " + str(win) + "$")
        value_loss = await api.get_management_values(user_id)['value_loss']
        new_balance = balance - value_loss
        new_value_loss = value_loss + win
        await api.update_management_values_loss(user_id=user_id, balance=new_balance, value_loss=new_value_loss)
    if win == 'win':
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
    asyncio.run(binary_check_win(check_id=check_id, iq=iq, user_id=user_id, balance=balance))