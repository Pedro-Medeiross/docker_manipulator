import os
import time
import pytz
import api
import asyncio
import concurrent.futures
import multiprocessing
from iqoption import IqOption
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

print('Iniciando bot...')
# Pares que serão monitorados
monitored_pairs = []
# Velas que serão monitoradas para cada par
candles_streams = {}

# ID do usuário
user_id = os.getenv('USER_ID')
# Instância da API da IQ Option
Iq = IqOption(user_id)
print('Conectando à API...')
# Conexão à API
Iq.connect()
Iq.set_account_type()
instance = Iq.instance()
print('Conectado à API...')

asyncio.run(api.reset_management_values(user_id))
print('Valores de gerenciamento resetados...')

start_balance = instance.get_balance()
print('Saldo: ', start_balance)
asyncio.run(api.set_balance(user_id, start_balance))
print('Saldo atualizado...')

# Status do bot
status_bot = asyncio.run(api.get_status_bot(user_id))
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


async def update_monitored_pairs(user_id: int):
    print('Atualizando pares monitorados...')
    # Obtém os pares de moedas disponíveis para negociação
    trade_info_pairs = await(api.get_trade_info_pairs(user_id))
    # Adiciona os pares que ainda não estão sendo monitorados
    for par in trade_info_pairs:
        if par not in monitored_pairs:
            monitored_pairs.append(par)
    # for p in monitored_pairs:
    #     if p not in candles_streams:
    #         await start_candle_stream(p)


async def start_candle_stream(pairs: str):
    print('Iniciando stream de velas para o par: ', pairs)
    # Inicia o stream de velas para o par
    for pairx in instance.get_all_ACTIVES_OPCODE():
        if pairx not in instance.get_all_ACTIVES_OPCODE():
            if pairx in candles_streams:
                instance.stop_candles_stream(pairs)
                candles_streams.pop(pairs)
    candles_streams[pairs] = instance.start_candles_stream(pairs, 1, 1)


async def get_candles(pair: str):
    print('Obtendo velas para o par: ', pair)
    horario = time.time()
    candles = instance.get_candles(pair, 5, 2, horario)
    return candles


async def stop_by_loss():
    print('Verificando se o bot deve ser parado por perda...')
    management_values = await api.get_management_values(user_id)
    stop_loss = management_values['stop_loss']
    value_loss = management_values['value_loss']
    value_gain = management_values['value_gain']
    lucro = value_gain - value_loss
    print(f'loss {lucro}')
    if lucro < 0:
        print('lucro menor que 0')
        if lucro <= stop_loss:
            print('Parando bot por perda...')
            await api.stop_by_loss(user_id)


async def stop_by_win():
    print('Verificando se o bot deve ser parado por ganho...')
    management_values = await api.get_management_values(user_id)
    stop_win = management_values['stop_win']
    value_gain = management_values['value_gain']
    value_loss = management_values['value_loss']
    lucro = value_gain - abs(value_loss)
    print(f'gain {lucro}')
    if lucro > 0:
        print('lucro maior que 0')
        if lucro >= stop_win:
            print('Parando bot por ganho...')
            await api.stop_by_win(user_id)



async def get_value_gain(user_id):
    management_values = await api.get_management_values(user_id)
    return management_values['value_gain']


async def get_value_loss(user_id):
    management_values = await api.get_management_values(user_id)
    return management_values['value_loss']


async def digital_check_win(check_id: int, balance: float):
    while True:
        print(f'checando digital win do id {check_id}')
        check_status, win = instance.check_win_digital_v2(check_id)
        print(f'digital {check_id}, status: {check_status}, win: {win}')
        await asyncio.sleep(1)
        if check_status:
            break
    if win < 0:
        print("you loss " + str(win) + "$")
        value_loss = await get_value_loss(user_id)
        new_balance = balance - value_loss
        new_value_loss = value_loss + win
        await api.update_management_values_loss(user_id=user_id, balance=new_balance, value_loss=new_value_loss)
        management = await api.get_management_status(user_id)
        if management:
            print('Checando se é para ser parado')
            await stop_by_loss()
            await stop_by_win()
    else:
        print("you win " + str(win) + "$")
        value_gain = await get_value_gain(user_id)
        new_balance = balance + value_gain
        new_value_gain = value_gain + win
        await api.update_management_values_gain(user_id=user_id, balance=new_balance, value_gain=new_value_gain)
        management = await api.get_management_status(user_id)
        if management:
            print('Checando se é para ser parado')
            await stop_by_loss()
            await stop_by_win()


async def binary_check_win(check_id: int, balance: float):
    while True:
        print(f'checando binary win do id {check_id}')
        check_status, win = instance.check_win_v4(check_id)
        print(f'binary {check_id}, status: {check_status}, win: {win}')
        await asyncio.sleep(1)
        if check_status:
            break
    if check_status == 'loose':
        print("you loss " + str(win) + "$")
        value_loss = await get_value_loss(user_id)
        new_balance = balance - value_loss
        new_value_loss = value_loss + win
        await api.update_management_values_loss(user_id=user_id, balance=new_balance, value_loss=new_value_loss)
        management = await api.get_management_status(user_id)
        if management:
            await stop_by_win()
            await stop_by_loss()
    elif check_status == 'win':
        print("you win " + str(win) + "$")
        value_gain = await get_value_gain(user_id)
        new_balance = balance + value_gain
        new_value_gain = value_gain + win
        await api.update_management_values_gain(user_id=user_id, balance=new_balance, value_gain=new_value_gain)
        management = await api.get_management_status(user_id)
        if management:
            await stop_by_win()
            await stop_by_loss()


async def check_win_digital_async(check_id, balance):
    await digital_check_win(check_id, balance)


async def check_win_binary_async(check_id, balance):
    await binary_check_win(check_id, balance)


async def buy_trade(trade_info_id: int):
    print('Iniciando negociação: ', trade_info_id)
    trade_info = await(api.get_trade_info(trade_info_id))
    user_values = await(api.get_user_values_by_trade_id(trade_info_id, user_id))
    price = trade_info['price']
    action = trade_info['method']
    time_frame = trade_info['timeframe']
    amount = user_values['amount']
    trade_status = await(api.get_trade_status_by_user_id_and_trade_id(user_id=user_id, trade_id=trade_info_id))
    type = trade_info['type']
    pair = trade_info['pair']
    pair1 = pair[0:3]
    pair2 = pair[3:6]
    news_status = await(api.get_news_status(user_id))
    localtime = time.localtime()
    now = time.strftime('%H:%M', localtime)
    if pair in monitored_pairs:
        candle = await(get_candles(pair))
        actual_candle = candle[0]['close']
        past_candle = candle[1]['close']
        if action == 'put':
            if actual_candle == past_candle:
                print(f'vela neutra: {actual_candle} = {past_candle}')
                if float(actual_candle) == float(price):
                    print(f'Vela igual ao preço: {candle} = {price}')
                    if news_status:
                        values = await(api.get_news_filter())
                        for x in values:
                            if x['pair'] == pair1 or x['pair'] == pair2:
                                if now in x['range_hours']:
                                    print('Notícia de alto impacto, não é recomendado negociar')
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=5, user_id=user_id))
                                    return
                    if trade_status == 2:
                        if type == 'D':
                            print(
                                f'Comprando Digital {pair} com valor de {price} em {time_frame} minutos, com range de {candle}')
                            check, id = instance.buy_digital_spot(active=pair, amount=amount, action=action,
                                                      duration=int(time_frame))
                            check_win = []
                            balance1 = instance.get_balance()
                            future = asyncio.create_task(check_win_digital_async(balance=balance1, check_id=id))
                            check_win.append(future)
                            await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                            await(api.set_trade_associated_exited_if_buy(trade_info_id))
                            await asyncio.gather(*check_win)
                        elif type == 'B':
                            remaining1 = instance.get_remaning(1)
                            remaining2 = instance.get_remaning(2)
                            remaining3 = instance.get_remaning(3)
                            remaining5 = instance.get_remaning(5)
                            print(f'Verificando tempo restante para compra de binário: {remaining1}, {remaining3}, {remaining5}')
                            if remaining1 < 60 and time_frame == 2:
                                if remaining2 > 90 and time_frame == 2:
                                    print(
                                        f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}')
                                    check, id = instance.buy(price=amount, ACTIVES=pair, expirations=2, ACTION=action)
                                    check_win = []
                                    balance2 = instance.get_balance()
                                    future = asyncio.create_task(check_win_binary_async(id, balance2))
                                    check_win.append(future)
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                    await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                    await asyncio.gather(*check_win)
                            elif remaining1 > 60 and time_frame == 2:
                                print(
                                    f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}')
                                check, id = instance.buy(price=amount, ACTIVES=pair, expirations=1, ACTION=action)
                                check_win = []
                                balance2 = instance.get_balance()
                                future = asyncio.create_task(check_win_binary_async(id, balance2))
                                check_win.append(future)
                                await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                await asyncio.gather(*check_win)
                            if remaining3 < 210 and time_frame == 3:
                                if remaining3 > 150 and time_frame == 3:
                                    print(
                                        f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}')
                                    check, id = instance.buy(price=amount, ACTIVES=pair, expirations=time_frame, ACTION=action)
                                    check_win = []
                                    balance2 = instance.get_balance()
                                    future = asyncio.create_task(check_win_binary_async(id, balance2))
                                    check_win.append(future)
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                    await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                    await asyncio.gather(*check_win)
                            if remaining5 < 330 and time_frame == 5:
                                if remaining5 > 270 and time_frame == 5:
                                    print(
                                        f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}')
                                    check, id = instance.buy(price=amount, ACTIVES=pair, expirations=time_frame, ACTION=action)
                                    check_win = []
                                    balance2 = instance.get_balance()
                                    future = asyncio.create_task(check_win_binary_async(id, balance2))
                                    check_win.append(future)
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                    await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                    await asyncio.gather(*check_win)
            if actual_candle > past_candle:
                print(f'vela verde: {actual_candle} > {past_candle}')
                num1 = (float(price) / 100000) * 4.25
                zone1 = float(price)
                zone2 = zone1 + num1
                if zone1 <= float(actual_candle) <= zone2:
                    print("A vela atual está na zona verde.")
                    print(f'Vela igual ao preço: {candle} = {price}')
                    if news_status:
                        values = await(api.get_news_filter())
                        for x in values:
                            if x['pair'] == pair1 or x['pair'] == pair2:
                                if now in x['range_hours']:
                                    print('Notícia de alto impacto, não é recomendado negociar')
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=5, user_id=user_id))
                                    return
                    if trade_status == 2:
                        if type == 'D':
                            print(
                                f'Comprando Digital {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                            check, id = instance.buy_digital_spot(active=pair, amount=amount, action=action,
                                                      duration=int(time_frame))
                            check_win = []
                            balance1 = instance.get_balance()
                            future = asyncio.create_task(check_win_digital_async(balance=balance1, check_id=id))
                            check_win.append(future)
                            await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                            await(api.set_trade_associated_exited_if_buy(trade_info_id))
                            await asyncio.gather(*check_win)
                        elif type == 'B':
                            remaining1 = instance.get_remaning(1)
                            remaining2 = instance.get_remaning(2)
                            remaining3 = instance.get_remaning(3)
                            remaining5 = instance.get_remaning(5)
                            print(f'Verificando tempo restante para compra de binário: {remaining1}, {remaining3}, {remaining5}')
                            if remaining1 < 60 and time_frame == 2:
                                if remaining2 > 90 and time_frame == 2:
                                    print(
                                        f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                                    check, id = instance.buy(price=amount, ACTIVES=pair, expirations=2, ACTION=action)
                                    check_win = []
                                    balance2 = instance.get_balance()
                                    future = asyncio.create_task(check_win_binary_async(id, balance2))
                                    check_win.append(future)
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                    await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                    await asyncio.gather(*check_win)
                            elif remaining1 > 60 and time_frame == 2:
                                print(
                                    f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                                check, id = instance.buy(price=amount, ACTIVES=pair, expirations=1, ACTION=action)
                                check_win = []
                                balance2= instance.get_balance()
                                future = asyncio.create_task(check_win_binary_async(id, balance2))
                                check_win.append(future)
                                await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                await asyncio.gather(*check_win)
                            if remaining3 < 210 and time_frame == 3:
                                if remaining3 > 150 and time_frame == 3:
                                    print(
                                        f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                                    check, id = instance.buy(price=amount, ACTIVES=pair, expirations=time_frame, ACTION=action)
                                    check_win = []
                                    balance2 = instance.get_balance()
                                    future = asyncio.create_task(check_win_binary_async(id, balance2))
                                    check_win.append(future)
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                    await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                    await asyncio.gather(*check_win)
                            if remaining5 < 330 and time_frame == 5:
                                if remaining5 > 270 and time_frame == 5:
                                    print(
                                        f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                                    check, id = instance.buy(price=amount, ACTIVES=pair, expirations=time_frame, ACTION=action)
                                    check_win = []
                                    balance2 = instance.get_balance()
                                    future = asyncio.create_task(check_win_binary_async(id, balance2))
                                    check_win.append(future)
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                    await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                    await asyncio.gather(*check_win)
            elif actual_candle < past_candle:
                print(f'vela vermelha: {actual_candle} < {past_candle}')
                num1 = (float(price) / 100000) * 3.75
                zone2 = float(price)
                zone1 = zone2 - num1
                if zone1 <= float(actual_candle) <= zone2:
                    print("A vela atual está na zona vermelha.")
                    print(f'Vela igual ao preço: {candle} = {price}')
                    if news_status:
                        values = await(api.get_news_filter())
                        for x in values:
                            if x['pair'] == pair1 or x['pair'] == pair2:
                                if now in x['range_hours']:
                                    print('Notícia de alto impacto, não é recomendado negociar')
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=5, user_id=user_id))
                                    return
                    if trade_status == 2:
                        if type == 'D':
                            print(
                                f'Comprando Digital {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                            check, id = instance.buy_digital_spot(active=pair, amount=amount, action=action,
                                                      duration=int(time_frame))
                            check_win = []
                            balance1 = instance.get_balance()
                            future = asyncio.create_task(check_win_digital_async(balance=balance1, check_id=id))
                            check_win.append(future)
                            await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                            await(api.set_trade_associated_exited_if_buy(trade_info_id))
                            await asyncio.gather(*check_win)
                        elif type == 'B':
                            remaining1 = instance.get_remaning(1)
                            remaining2 = instance.get_remaning(2)
                            remaining3 = instance.get_remaning(3)
                            remaining5 = instance.get_remaning(5)
                            print(
                                f'Verificando tempo restante para compra de binário: {remaining1}, {remaining3}, {remaining5}')
                            if remaining1 < 60 and time_frame == 2:
                                if remaining2 > 90 and time_frame == 2:
                                    print(
                                        f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                                    check, id = instance.buy(price=amount, ACTIVES=pair, expirations=2, ACTION=action)
                                    check_win = []
                                    balance2 = instance.get_balance()
                                    future = asyncio.create_task(check_win_binary_async(id, balance2))
                                    check_win.append(future)
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                    await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                    await asyncio.gather(*check_win)
                            elif remaining1 > 60 and time_frame == 2:
                                print(
                                    f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                                check, id = instance.buy(price=amount, ACTIVES=pair, expirations=1, ACTION=action)
                                check_win = []
                                balance2 = instance.get_balance()
                                future = asyncio.create_task(check_win_binary_async(id, balance2))
                                check_win.append(future)
                                await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                await asyncio.gather(*check_win)
                            if remaining3 < 210 and time_frame == 3:
                                if remaining3 > 150 and time_frame == 3:
                                    print(
                                        f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                                    check, id = instance.buy(price=amount, ACTIVES=pair, expirations=time_frame, ACTION=action)
                                    check_win = []
                                    balance2 = instance.get_balance()
                                    future = asyncio.create_task(check_win_binary_async(id, balance2))
                                    check_win.append(future)
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                    await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                    await asyncio.gather(*check_win)
                            if remaining5 < 330 and time_frame == 5:
                                if remaining5 > 270 and time_frame == 5:
                                    print(
                                        f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                                    check, id = instance.buy(price=amount, ACTIVES=pair, expirations=time_frame, ACTION=action)
                                    check_win = []
                                    balance2 = instance.get_balance()
                                    future = asyncio.create_task(check_win_binary_async(id, balance2))
                                    check_win.append(future)
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                    await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                    await asyncio.gather(*check_win)
        elif action == 'call':
            if actual_candle == past_candle:
                print(f'vela neutra: {actual_candle} = {past_candle}')
                if float(actual_candle) == float(price):
                    print(f'Vela igual ao preço: {candle} = {price}')
                    if news_status:
                        values = await(api.get_news_filter())
                        for x in values:
                            if x['pair'] == pair1 or x['pair'] == pair2:
                                if now in x['range_hours']:
                                    print('Notícia de alto impacto, não é recomendado negociar')
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=5, user_id=user_id))
                                    return
                    if trade_status == 2:
                        if type == 'D':
                            print(
                                f'Comprando Digital {pair} com valor de {price} em {time_frame} minutos, com range de {candle}')
                            check, id = instance.buy_digital_spot(active=pair, amount=amount, action=action,
                                                      duration=int(time_frame))
                            check_win = []
                            balance1 = instance.get_balance()
                            future = asyncio.create_task(check_win_digital_async(balance=balance1, check_id=id))
                            check_win.append(future)
                            await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                            await(api.set_trade_associated_exited_if_buy(trade_info_id))
                            await asyncio.gather(*check_win)
                        elif type == 'B':
                            remaining1 = instance.get_remaning(1)
                            remaining2 = instance.get_remaning(2)
                            remaining3 = instance.get_remaning(3)
                            remaining5 = instance.get_remaning(5)
                            print(f'Verificando tempo restante para compra de binário: {remaining1}, {remaining3}, {remaining5}')
                            if remaining1 < 60 and time_frame == 2:
                                if remaining2 > 90 and time_frame == 2:
                                    print(
                                        f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}')
                                    check, id = instance.buy(price=amount, ACTIVES=pair, expirations=2, ACTION=action)
                                    check_win = []
                                    balance2 = instance.get_balance()
                                    future = asyncio.create_task(check_win_binary_async(id, balance2))
                                    check_win.append(future)
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                    await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                    await asyncio.gather(*check_win)
                            elif remaining1 > 60 and time_frame == 2:
                                print(
                                    f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}')
                                check, id = instance.buy(price=amount, ACTIVES=pair, expirations=1, ACTION=action)
                                check_win = []
                                balance2 = instance.get_balance()
                                future = asyncio.create_task(check_win_binary_async(id, balance2))
                                check_win.append(future)
                                await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                await asyncio.gather(*check_win)
                            if remaining3 < 210 and time_frame == 3:
                                if remaining3 > 150 and time_frame == 3:
                                    print(
                                        f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}')
                                    check, id = instance.buy(price=amount, ACTIVES=pair, expirations=time_frame, ACTION=action)
                                    check_win = []
                                    balance2 = instance.get_balance()
                                    future = asyncio.create_task(check_win_binary_async(id, balance2))
                                    check_win.append(future)
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                    await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                    await asyncio.gather(*check_win)
                            if remaining5 < 330 and time_frame == 5:
                                if remaining5 > 270 and time_frame == 5:
                                    print(
                                        f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}')
                                    check, id = instance.buy(price=amount, ACTIVES=pair, expirations=time_frame, ACTION=action)
                                    check_win = []
                                    balance2 = instance.get_balance()
                                    future = asyncio.create_task(check_win_binary_async(id, balance2))
                                    check_win.append(future)
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                    await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                    await asyncio.gather(*check_win)
            if actual_candle > past_candle:
                print(f'vela verde: {actual_candle} > {past_candle}')
                num1 = (float(price) / 100000) * 4
                zone1 = float(price)
                zone2 = zone1 + num1
                if zone1 <= float(actual_candle) <= zone2:
                    print("A vela atual está na zona verde.")
                    print(f'Vela igual ao preço: {candle} = {price}')
                    if news_status:
                        values = await(api.get_news_filter())
                        for x in values:
                            if x['pair'] == pair1 or x['pair'] == pair2:
                                if now in x['range_hours']:
                                    print('Notícia de alto impacto, não é recomendado negociar')
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=5, user_id=user_id))
                                    return
                    if trade_status == 2:
                        if type == 'D':
                            print(
                                f'Comprando Digital {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                            check, id = instance.buy_digital_spot(active=pair, amount=amount, action=action,
                                                      duration=int(time_frame))
                            check_win = []
                            balance1 = instance.get_balance()
                            future = asyncio.create_task(check_win_digital_async(balance=balance1, check_id=id))
                            check_win.append(future)
                            await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                            await(api.set_trade_associated_exited_if_buy(trade_info_id))
                            await asyncio.gather(*check_win)
                        elif type == 'B':
                            remaining1 = instance.get_remaning(1)
                            remaining2 = instance.get_remaning(2)
                            remaining3 = instance.get_remaning(3)
                            remaining5 = instance.get_remaning(5)
                            print(f'Verificando tempo restante para compra de binário: {remaining2}')
                            if remaining1 < 60 and time_frame == 2:
                                if remaining2 > 90 and time_frame == 2:
                                    print(
                                        f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                                    check, id = instance.buy(price=amount, ACTIVES=pair, expirations=2, ACTION=action)
                                    check_win = []
                                    balance2 = instance.get_balance()
                                    future = asyncio.create_task(check_win_binary_async(id, balance2))
                                    check_win.append(future)
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                    await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                    await asyncio.gather(*check_win)
                            elif remaining1 > 60 and time_frame == 2:
                                print(
                                    f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                                check, id = instance.buy(price=amount, ACTIVES=pair, expirations=1, ACTION=action)
                                check_win = []
                                balance2 = instance.get_balance()
                                future = asyncio.create_task(check_win_binary_async(id, balance2))
                                check_win.append(future)
                                await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                await asyncio.gather(*check_win)
                            if remaining3 < 210 and time_frame == 3:
                                if remaining3 > 150 and time_frame == 3:
                                    print(
                                        f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                                    check, id = instance.buy(price=amount, ACTIVES=pair, expirations=time_frame, ACTION=action)
                                    check_win = []
                                    balance2 = instance.get_balance()
                                    future = asyncio.create_task(check_win_binary_async(id, balance2))
                                    check_win.append(future)
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                    await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                    await asyncio.gather(*check_win)
                            if remaining5 < 330 and time_frame == 5:
                                if remaining5 > 270 and time_frame == 5:
                                    print(
                                        f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                                    check, id = instance.buy(price=amount, ACTIVES=pair, expirations=time_frame, ACTION=action)
                                    check_win = []
                                    balance2 = instance.get_balance()
                                    future = asyncio.create_task(check_win_binary_async(id, balance2))
                                    check_win.append(future)
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                    await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                    await asyncio.gather(*check_win)
            elif actual_candle < past_candle:
                print(f'vela vermelha: {actual_candle} < {past_candle}')
                num1 = (float(price) / 100000) * 4
                zone2 = float(price)
                zone1 = zone2 - num1
                if zone1 <= float(actual_candle) <= zone2:
                    print("A vela atual está na zona vermelha.")
                    print(f'Vela igual ao preço: {candle} = {price}')
                    if news_status:
                        values = await(api.get_news_filter())
                        for x in values:
                            if x['pair'] == pair1 or x['pair'] == pair2:
                                if now in x['range_hours']:
                                    print('Notícia de alto impacto, não é recomendado negociar')
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=5, user_id=user_id))
                                    return
                    if trade_status == 2:
                        if type == 'D':
                            print(
                                f'Comprando Digital {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                            check, id = instance.buy_digital_spot(active=pair, amount=amount, action=action,
                                                      duration=int(time_frame))
                            check_win = []
                            balance1 = instance.get_balance()
                            future = asyncio.create_task(check_win_digital_async(balance=balance1, check_id=id))
                            check_win.append(future)
                            await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                            await(api.set_trade_associated_exited_if_buy(trade_info_id))
                            await asyncio.gather(*check_win)
                        elif type == 'B':
                            remaining1 = instance.get_remaning(1)
                            remaining2 = instance.get_remaning(2)
                            remaining3 = instance.get_remaning(3)
                            remaining5 = instance.get_remaning(5)
                            print(f'Verificando tempo restante para compra de binário: {remaining2}')
                            if remaining1 < 60 and time_frame == 2:
                                if remaining2 > 90 and time_frame == 2:
                                    print(
                                        f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                                    check, id = instance.buy(price=amount, ACTIVES=pair, expirations=2, ACTION=action)
                                    check_win = []
                                    balance2 = instance.get_balance()
                                    future = asyncio.create_task(check_win_binary_async(id, balance2))
                                    check_win.append(future)
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                    await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                    await asyncio.gather(*check_win)
                            elif remaining1 > 60 and time_frame == 2:
                                print(
                                    f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                                check, id = instance.buy(price=amount, ACTIVES=pair, expirations=1, ACTION=action)
                                check_win = []
                                balance2 = instance.get_balance()
                                future = asyncio.create_task(check_win_binary_async(id, balance2))
                                check_win.append(future)
                                await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                await asyncio.gather(*check_win)
                            if remaining3 < 210 and time_frame == 3:
                                if remaining3 > 150 and time_frame == 3:
                                    print(
                                        f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                                    check, id = instance.buy(price=amount, ACTIVES=pair, expirations=time_frame,
                                                             ACTION=action)
                                    check_win = []
                                    balance2 = instance.get_balance()
                                    future = asyncio.create_task(check_win_binary_async(id, balance2))
                                    check_win.append(future)
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                    await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                    await asyncio.gather(*check_win)
                            if remaining5 < 330 and time_frame == 5:
                                if remaining5 > 270 and time_frame == 5:
                                    print(
                                        f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                                    check, id = instance.buy(price=amount, ACTIVES=pair, expirations=time_frame,
                                                             ACTION=action)
                                    check_win = []
                                    balance2 = instance.get_balance()
                                    future = asyncio.create_task(check_win_binary_async(id, balance2))
                                    check_win.append(future)
                                    await(api.set_schedule_status(trade_id=trade_info_id, status=4, user_id=user_id))
                                    await(api.set_trade_associated_exited_if_buy(trade_info_id))
                                    await asyncio.gather(*check_win)


    # if pair not in monitored_pairs:
    #     instance.stop_candles_stream(pair)
    #     candles_streams.pop(pair)
    #     monitored_pairs.remove(pair)


async def main():
    print('Iniciando negociação...')
    trade_info_ids = await(api.get_trade_user_info_scheduled(user_id))
    print('Negociações agendadas: ', trade_info_ids)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        print(f'Iniciando {len(trade_info_ids)} negociações...')
        buy_tasks = []
        for trade_info_id in trade_info_ids:
            future = asyncio.ensure_future(buy_trade(trade_info_id))
            buy_tasks.append(future)
        print(f'Iniciando {len(trade_info_ids)} negociações...')
        await asyncio.gather(*buy_tasks)
        print('Negociações finalizadas')


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

while True:
    print('Iniciando loop...')
    loop.run_until_complete(update_monitored_pairs(user_id))
    loop.run_until_complete(main())
