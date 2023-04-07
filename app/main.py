import os
import time
import api
from iqoption import IqOption
import asyncio

# Pares que serão monitorados
monitored_pairs = []
# Velas que serão monitoradas para cada par
candles_streams = {}

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


def update_monitored_pairs(user_id: int):
    # Obtém os pares de moedas disponíveis para negociação
    trade_info_pairs = asyncio.run(api.get_trade_info_pairs(user_id))
    # Adiciona os pares que ainda não estão sendo monitorados
    for par in trade_info_pairs:
        for pairs in instance.get_all_ACTIVES_OPCODE():
            if pairs == par:
                if par not in monitored_pairs:
                    monitored_pairs.append(par)
                    print('Monitorando par: ', par)
    for p in monitored_pairs:
        if p not in candles_streams:
            start_candle_stream(p)
        if p not in instance.get_all_ACTIVES_OPCODE():
            print('Par não disponível para negociação: ', p)
            instance.stop_candles_stream(p)
            monitored_pairs.remove(p)


def start_candle_stream(pair: str):
    # Inicia o stream de velas para o par
    candles_streams[pair] = instance.start_candles_stream(pair, "all", 1)
    print('Iniciando stream de velas para o par: ', pair)


while status_bot == 1:
    update_monitored_pairs(user_id)
    trade_info_ids = asyncio.run(api.get_trade_user_info_scheduled(user_id))
    for pair in monitored_pairs:
        print('Verificando par: ', pair)
        candles = instance.get_realtime_candles(pair, "all")
        candle = 0
        for key in list(candles.keys()):
            candle = candles[key]["open"]
            print(f'par: {pair} candle: {candle}')
            for trade_info_id in trade_info_ids:
                trade_info = asyncio.run(api.get_trade_info(trade_info_id))
                user_values = asyncio.run(api.get_user_values_by_trade_id(trade_info_id))
                price = trade_info['price']
                action = trade_info['method']
                time_frame = trade_info['timeframe']
                amount = user_values['ammount']
                trade_status = user_values['status']
                if candle == price:
                    if trade_status == 0:
                        print('Comprando', pair, 'com valor de', price, 'em', time_frame, 'minutos', )
                        instance.buy_digital_spot(active=pair, amount=amount, action=action,
                                                  duration=time_frame)
                        asyncio.run(api.set_schedule_status(trade_info_id, status=1, user_id=user_id))

        if pair not in monitored_pairs:
            instance.stop_candles_stream(pair)
        time.sleep(1)
