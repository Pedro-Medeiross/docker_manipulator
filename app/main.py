import base64
import os
import time
import pytz
import api
import asyncio
import concurrent.futures
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from quotexapi.stable_api import Quotex

executor = ThreadPoolExecutor()

print('Iniciando bot...')
# Pares que serão monitorados
monitored_pairs = []
# Velas que serão monitoradas para cada par
candles_streams = {}

# ID do usuário
user_id = os.getenv('USER_ID')
email = os.getenv('EMAIL')
password = base64.b64decode(os.getenv('PASSWORD')).decode()
# Instância da API da IQ Option
instance = Quotex(email, password)
instance.connect()
print('Conectando à API...')
# Conexão à API
if not instance.check_connect():
    instance.connect()
instance.change_account(os.getenv('ACCOUNT_TYPE'))
print('Conectado à API...')

asyncio.run(api.reset_management_values(int(user_id)))
print('Valores de gerenciamento resetados...')

if not instance.check_connect():
    instance.connect()
start_balance = instance.get_balance()
print('Saldo: ', start_balance)
asyncio.run(api.set_balance(int(user_id), start_balance))
print('Saldo atualizado...')

# Status do bot
status_bot = asyncio.run(api.get_status_bot(int(user_id)))
print('Status do bot: ', status_bot)

# Status da negociação atual
trade_status = None
# ID das informações da negociação atual
trade_info_id = None
# Valor da negociação atual
amount = None
# Ação da negociação atual (PUT ou CALL)
action = None
# Valor para não nulificar a negociação
candle = None

check_win_ids = {}
check_win_ids_balance = {}
check_win_ids_profit = {}


async def handle_win_checks():
    print('checando win')
    for ids in check_win_ids:
        if check_win_ids[ids] == 'binary':
            balance = check_win_ids_balance[ids]
            profit = instance.check_win(ids)
            await binary_check_win(check_id=ids, balance=balance, profit=profit)


async def update_monitored_pairs(user_id: int):
    instance.get_balance()
    print('Atualizando pares monitorados...')
    # Obtém os pares de moedas disponíveis para negociação
    trade_info_pairs = await(api.get_trade_info_pairs(user_id))
    # Adiciona os pares que ainda não estão sendo monitorados
    for par in trade_info_pairs:
        if par not in monitored_pairs:
            monitored_pairs.append(par)
    for p in monitored_pairs:
        if p not in candles_streams:
            await start_candle_stream(p)


async def start_candle_stream(pairx: str):
    print('Iniciando stream de velas para o par: ', pairx)
    instance.get_balance()
    # Inicia o stream de velas para o par
    first_par = pairx[:3].upper()
    second_par = pairx[3:].upper()
    par_changed = f'{first_par}/{second_par}'
    if "_OTC" in second_par:
        otc = "(OTC)"
        par_changed = f'{first_par}/{second_par} {otc}'
        par_changed = par_changed.replace("_OTC", "")
    if not instance.check_asset_open(par_changed):
        if pairx in candles_streams:
            instance.stop_candles_stream(pairx)
            candles_streams.pop(pairx)
    candles_streams[pairx] = instance.start_candles_stream(pairx, 1, 5)


async def get_candles(pair: str):
    print('Obtendo velas para o par: ', pair)
    candles = instance.get_realtime_candles(pair)
    return candles


async def stop_by_loss():
    print('Verificando se o bot deve ser parado por perda...')
    management_values = await api.get_management_values(int(user_id))
    stop_loss = management_values['stop_loss']
    value_loss = management_values['value_loss']
    value_gain = management_values['value_gain']
    lucro = value_gain - abs(value_loss)
    loss_value = stop_loss * -1
    print(f'loss {lucro}')
    if lucro < 0:
        print('lucro menor que 0')
        if lucro <= loss_value:
            print(f'{lucro} <= {loss_value}')
            print('Parando bot por perda...')
            await api.stop_by_loss(int(user_id))


async def stop_by_win():
    print('Verificando se o bot deve ser parado por ganho...')
    management_values = await api.get_management_values(int(user_id))
    stop_win = management_values['stop_win']
    value_gain = management_values['value_gain']
    value_loss = management_values['value_loss']
    lucro = value_gain - abs(value_loss)
    print(f'gain {lucro}')
    if lucro > 0:
        print('lucro maior que 0')
        if lucro >= stop_win:
            print(f'{lucro} >= {stop_win}')
            print('Parando bot por ganho...')
            await api.stop_by_win(int(user_id))


async def get_value_gain(user_id):
    management_values = await api.get_management_values(user_id)
    return management_values['value_gain']


async def get_value_loss(user_id):
    management_values = await api.get_management_values(user_id)
    return management_values['value_loss']


async def binary_check_win(check_id: str, balance: float, profit: float):
    print(f'checando binary win do id {check_id}')
    check_status = instance.check_win(check_id)
    print(f'binary {check_id}, status: {check_status}, win: {profit}')
    if not check_status:
        print("you loss " + str(profit) + "$")
        value_loss = await get_value_loss(user_id)
        new_balance = balance - value_loss
        new_value_loss = value_loss + profit
        await api.update_management_values_loss(user_id=int(user_id), balance=new_balance, value_loss=new_value_loss)
        management = await api.get_management_status(int(user_id))
        rc = check_win_ids.pop(check_id)
        rcb = check_win_ids_balance.pop(check_id)
        print(f'removido {rc} {rcb}')
        if management:
            await stop_by_loss()
            await stop_by_win()
    elif check_status:
        print("you win " + str(profit) + "$")
        value_gain = await get_value_gain(user_id)
        new_balance = balance + value_gain
        new_value_gain = value_gain + profit
        await api.update_management_values_gain(user_id=int(user_id), balance=new_balance, value_gain=new_value_gain)
        management = await api.get_management_status(int(user_id))
        rc = check_win_ids.pop(check_id)
        rcb = check_win_ids_balance.pop(check_id)
        print(f'removido {rc} {rcb}')
        if management:
            await stop_by_loss()
            await stop_by_win()


async def buy_trade(trade_info_id: int):
    print('Iniciando negociação: ', trade_info_id)
    trade_info = await(api.get_trade_info(trade_info_id))
    user_values = await(api.get_user_values_by_trade_id(trade_info_id, int(user_id)))
    price = trade_info['price']
    action = trade_info['method']
    time_frame = trade_info['timeframe']
    amount = user_values['amount']
    trade_status = user_values['status_trade']
    type = trade_info['type']
    pair = trade_info['pair']
    pair1 = pair[0:3]
    pair2 = pair[3:6]
    news_status = await(api.get_news_status(int(user_id)))
    localtime = time.localtime()
    now = time.strftime('%H:%M', localtime)
    if pair in monitored_pairs:
        candle = await(get_candles(pair))
        actual_candle = candle[0]['price']
        print(f'Vela atual: {actual_candle}')
        if action == 'put':
            print('Ação: PUT')
            if float(actual_candle) == float(price):
                print(f'Vela igual ao preço: {candle} = {price}')
                if news_status:
                    values = await(api.get_news_filter())
                    for x in values:
                        if x['pair'] == pair1 or x['pair'] == pair2:
                            if now in x['range_hours']:
                                print('Notícia de alto impacto, não é recomendado negociar')
                                await(api.set_schedule_status(trade_id=trade_info_id, status=5, user_id=int(user_id)))
                                return
                if trade_status == 2:
                    if type == 'B':
                        print('Negociação binária')
                        print(f'all values {time_frame} {amount} {pair} {action}')
                        buyed = instance.buy(price=amount, asset=pair, direction=action, duration=int(time_frame))
                        print(f'buyed {buyed}')
                        id = buyed[1]['id']
                        profit = buyed[1]['profit']
                        balance2 = instance.get_balance()
                        check_win_ids[id] = 'binary'
                        check_win_ids_balance[id] = balance2
                        check_win_ids_profit[id] = profit
                        await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                        await(api.set_trade_associated_exited_if_buy(trade_info_id))
        elif action == 'call':
            print('Ação: CALL')
            if float(actual_candle) == float(price):
                print(f'Vela igual ao preço: {candle} = {price}')
                if news_status:
                    values = await(api.get_news_filter())
                    for x in values:
                        if x['pair'] == pair1 or x['pair'] == pair2:
                            if now in x['range_hours']:
                                print('Notícia de alto impacto, não é recomendado negociar')
                                await(api.set_schedule_status(trade_id=trade_info_id, status=5, user_id=int(user_id)))
                                return
                if trade_status == 2:
                    if type == 'B':
                        print('Negociação binária')
                        print(f'all values {time_frame} {amount} {pair} {action}')
                        buyed = instance.buy(price=amount, asset=pair, direction=action, duration=int(time_frame))
                        print(f'buyed {buyed}')
                        id = buyed[1]['id']
                        profit = buyed[1]['profit']
                        balance2 = instance.get_balance()
                        check_win_ids[id] = 'binary'
                        check_win_ids_balance[id] = balance2
                        check_win_ids_profit[id] = profit
                        await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=int(user_id)))
                        await(api.set_trade_associated_exited_if_buy(trade_info_id))
    if pair not in monitored_pairs:
        instance.stop_candles_stream(pair)
        candles_streams.pop(pair)
        monitored_pairs.remove(pair)


async def main():
    instance.get_balance()
    print('Iniciando negociação...')
    trade_info_ids = await(api.get_trade_user_info_scheduled(int(user_id)))
    print('Negociações agendadas: ', trade_info_ids)
    buy_tasks = []
    for trade_info_id in trade_info_ids:
        task = asyncio.ensure_future(buy_trade(trade_info_id))
        buy_tasks.append(task)
    print(f'Iniciando {len(trade_info_ids)} negociações...')
    await asyncio.gather(*buy_tasks)
    print('Negociações finalizadas')


async def check_win():
    if check_win_ids:
        asyncio.create_task(handle_win_checks())


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

if not instance.check_connect():
    instance.connect()

while True:
    print('Iniciando loop...')
    if not instance.check_connect():
        instance.connect()
    print(instance.get_balance())
    loop.run_until_complete(update_monitored_pairs(int(user_id)))
    loop.run_until_complete(main())
    loop.run_until_complete(check_win())
