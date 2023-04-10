import os
import time
import api
from iqoption import IqOption
import asyncio
from asyncio import tasks

# Pares que serão monitorados
monitored_pairs = []
# Velas que serão monitoradas para cada par
candles_streams = {}

buy_tasks = []

# ID do usuário
print('Iniciando bot...')
user_id = os.getenv('USER_ID')
# Instância da API da IQ Option
Iq = IqOption(user_id)
# Conexão à API
Iq.connect()
Iq.set_account_type()
print('Conectado à API')
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
    # Obtém os pares de moedas disponíveis para negociação
    trade_info_pairs = await(api.get_trade_info_pairs(user_id))
    # Adiciona os pares que ainda não estão sendo monitorados
    for par in trade_info_pairs:
        if par not in monitored_pairs:
            monitored_pairs.append(par)
            print('Monitorando par: ', par)
    for p in monitored_pairs:
        if p not in candles_streams:
            await start_candle_stream(p)


async def start_candle_stream(pairs: str):
    # Inicia o stream de velas para o par
    for pairx in instance.get_all_ACTIVES_OPCODE():
        if pairx not in instance.get_all_ACTIVES_OPCODE():
            print('Par não disponível para negociação: ', pairs)
            if pairx in candles_streams:
                instance.stop_candles_stream(pairs)
                candles_streams.pop(pairs)
    candles_streams[pairs] = instance.start_candles_stream(pairs, 1, 1)
    print('Iniciando stream de velas para o par: ', pairs)


async def get_candles(pair: str):
    candles = instance.get_realtime_candles(pair, 1)
    for key in list(candles.keys()):
        candlx = candles[key]["open"]
    return candlx


async def buy_trade(trade_info_id : int):
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
    if pair in monitored_pairs:
        candle = await(get_candles(pair))
        print(f'price: {price}, candle: {candle}')
        if candle == float(price):
            print(f'Vela igual ao preço: {candle} = {price}')
            if trade_status == 0:
                if type == 'D':
                    instance.buy_digital_spot(active=pair, amount=amount, action=action,
                                              duration=int(time_frame))
                    await(api.set_schedule_status(trade_id=trade_info_id, status=1, user_id=user_id))
                elif type == 'B':
                    print('Comprando Binario', pair, 'com valor de', price, 'em', time_frame, 'minutos', )
                    instance.buy(price=amount, ACTIVES=pair, expirations=time_frame, ACTION=action)
                    await(api.set_schedule_status(trade_id=trade_info_id, status=1, user_id=user_id))

    if pair not in monitored_pairs:
        instance.stop_candles_stream(pair)
        candles_streams.pop(pair)
        monitored_pairs.remove(pair)
        print('Par não está mais sendo monitorado: ', pair)


async def main():
    await update_monitored_pairs(user_id)
    trade_info_ids = await(api.get_trade_user_info_scheduled(user_id))
    for trade_id in trade_info_ids:
        for task in buy_tasks:
            print(f'task: {task}, {buy_tasks}')
            if task.get_name() != str(trade_info_id):
                task = asyncio.create_task(buy_trade(trade_id), name=str(trade_info_id))
                buy_tasks.append(task)
    await asyncio.gather(*buy_tasks)


while True:
    asyncio.run(main())
