import os
import time
import pytz
import api
from iqoption import IqOption
import asyncio
import concurrent.futures

# Pares que serão monitorados
monitored_pairs = []
# Velas que serão monitoradas para cada par
candles_streams = {}

# ID do usuário
user_id = os.getenv('USER_ID')
# Instância da API da IQ Option
Iq = IqOption(user_id)
# Conexão à API
Iq.connect()
Iq.set_account_type()
instance = Iq.instance()

# Status do bot
status_bot = asyncio.run(api.get_status_bot(user_id))

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
    for p in monitored_pairs:
        if p not in candles_streams:
            await start_candle_stream(p)


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
    candles = instance.get_realtime_candles(pair, 1)
    for key in list(candles.keys()):
        candlx = candles[key]["open"]
    return candlx


async def buy_trade(trade_info_id: int):
    print('Iniciando negociação: ', trade_info_id)
    trade_info = await(api.get_trade_info(trade_info_id))
    user_values = await(api.get_user_values_by_trade_id(trade_info_id, user_id))
    price = trade_info['price']
    action = trade_info['method']
    time_frame = trade_info['timeframe']
    amount = user_values['ammount']
    trade_status = user_values['status']
    type = trade_info['type']
    pair = trade_info['pair']
    news_status = api.get_news_status(user_id)
    localtime = time.localtime()
    now = time.strftime('%H:%M', localtime)
    if pair in monitored_pairs:
        candle = await(get_candles(pair))
        if action == 'put':
            num1 = (float(price) / 100000) * 5
            num2 = (float(price) / 100000) * 1
            zone1 = float(price) - num2
            zone2 = float(price) + num1
            if float(candle) >= zone1 and float(candle) <= zone2:
                print(f'Vela igual ao preço: {candle} = {price}')
                if news_status:
                    values = api.get_news_filter()
                    for x in values:
                        if x['pair'] == pair:
                            if now in x['range_hours']:
                                print('Notícia de alto impacto, não é recomendado negociar')
                                return
                if trade_status == 0:
                    if type == 'D':
                        print(
                            f'Comprando Digital {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                        instance.buy_digital_spot(active=pair, amount=amount, action=action,
                                                  duration=int(time_frame))
                        await(api.set_schedule_status(trade_id=trade_info_id, status=3, user_id=user_id))
                        await(api.set_trade_associated_exited_if_buy(trade_info_id))
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
                                instance.buy(price=amount, ACTIVES=pair, expirations=2, ACTION=action)
                                await(api.set_schedule_status(trade_id=trade_info_id, status=3, user_id=user_id))
                                await(api.set_trade_associated_exited_if_buy(trade_info_id))
                        elif remaining1 > 60 and time_frame == 2:
                            print(
                                f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                            instance.buy(price=amount, ACTIVES=pair, expirations=1, ACTION=action)
                            await(api.set_schedule_status(trade_id=trade_info_id, status=3, user_id=user_id))
                            await(api.set_trade_associated_exited_if_buy(trade_info_id))
                        if remaining3 < 210 and time_frame == 3:
                            if remaining3 > 150 and time_frame == 3:
                                print(
                                    f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                                instance.buy(price=amount, ACTIVES=pair, expirations=time_frame, ACTION=action)
                                await(api.set_schedule_status(trade_id=trade_info_id, status=3, user_id=user_id))
                                await(api.set_trade_associated_exited_if_buy(trade_info_id))
                        if remaining5 < 330 and time_frame == 5:
                            if remaining5 > 270 and time_frame == 5:
                                print(
                                    f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                                instance.buy(price=amount, ACTIVES=pair, expirations=time_frame, ACTION=action)
                                await(api.set_schedule_status(trade_id=trade_info_id, status=3, user_id=user_id))
                                await(api.set_trade_associated_exited_if_buy(trade_info_id))
        elif action == 'call':
            num1 = (float(price) / 100000) * 5
            num2 = (float(price) / 100000) * 1
            zone1 = float(price) - num1
            zone2 = float(price) + num2
            if float(candle) >= zone1 and float(candle) <= zone2:
                print(f'Vela igual ao preço: {candle} = {price}')
                if news_status:
                    values = api.get_news_filter()
                    for x in values:
                        if x['pair'] == pair:
                            if now in x['range_hours']:
                                print('Notícia de alto impacto, não é recomendado negociar')
                                return
                if trade_status == 0:
                    if type == 'D':
                        print(
                            f'Comprando Digital {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                        instance.buy_digital_spot(active=pair, amount=amount, action=action,
                                                  duration=int(time_frame))
                        await(api.set_schedule_status(trade_id=trade_info_id, status=3, user_id=user_id))
                        await(api.set_trade_associated_exited_if_buy(trade_info_id))
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
                                instance.buy(price=amount, ACTIVES=pair, expirations=2, ACTION=action)
                                await(api.set_schedule_status(trade_id=trade_info_id, status=3, user_id=user_id))
                                await(api.set_trade_associated_exited_if_buy(trade_info_id))
                        elif remaining1 > 60 and time_frame == 2:
                            print(
                                f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                            instance.buy(price=amount, ACTIVES=pair, expirations=1, ACTION=action)
                            await(api.set_schedule_status(trade_id=trade_info_id, status=3, user_id=user_id))
                            await(api.set_trade_associated_exited_if_buy(trade_info_id))
                        if remaining3 < 210 and time_frame == 3:
                            if remaining3 > 150 and time_frame == 3:
                                print(
                                    f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                                instance.buy(price=amount, ACTIVES=pair, expirations=time_frame, ACTION=action)
                                await(api.set_schedule_status(trade_id=trade_info_id, status=3, user_id=user_id))
                                await(api.set_trade_associated_exited_if_buy(trade_info_id))
                        if remaining5 < 330 and time_frame == 5:
                            if remaining5 > 270 and time_frame == 5:
                                print(
                                    f'Comprando Binário {pair} com valor de {price} em {time_frame} minutos, com range de {candle}, {zone1}, {zone2}')
                                instance.buy(price=amount, ACTIVES=pair, expirations=time_frame, ACTION=action)
                                await(api.set_schedule_status(trade_id=trade_info_id, status=3, user_id=user_id))
                                await(api.set_trade_associated_exited_if_buy(trade_info_id))

    await asyncio.sleep(1)

    if pair not in monitored_pairs:
        instance.stop_candles_stream(pair)
        candles_streams.pop(pair)
        monitored_pairs.remove(pair)


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
