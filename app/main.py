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


def update_monitored_pairs():
    # Obtém os pares de moedas disponíveis para negociação
    trade_info_pairs = asyncio.run(api.get_trade_info_pairs())
    print(trade_info_pairs)
    # Adiciona os pares que ainda não estão sendo monitorados
    for par in trade_info_pairs:
        if par[0] not in monitored_pairs:
            monitored_pairs.append(par[0])
            print('Monitorando par: ', par[0])


while status_bot == 1:
    print('Verificando status do bot...')
    update_monitored_pairs()
    trade_info_ids = asyncio.run(api.get_trade_user_info_scheduled(user_id))
    for pair in monitored_pairs:
        print('Verificando par: ', pair)
        if pair not in candles_streams:
            candles_streams[pair] = instance.start_candles_stream(pair, 1, 1)
        candles = instance.get_realtime_candles(pair, 1)
        candle = 0
        for key in candles:
            candle = candles[key]["open"]
            print(f'par: {pair} candle: {candle}')
            for trade_info_id in trade_info_ids:
                trade_info = asyncio.run(api.get_trade_info(trade_info_id))
                user_values = asyncio.run(api.get_user_values_by_trade_id(trade_info_id))
                price = trade_info['cotacao']
                actions = trade_info['tipo_negocio']
                time_frame = trade_info['time']
                if actions == "C":
                    action = "call"
                elif actions == "P":
                    action = "put"
                amount = user_values['value']
                trade_status = user_values['status']
                if candle == price:
                    if trade_status == 0:
                        print('Comprando', pair, 'com valor de', price, 'em', time_frame, 'minutos', )
                        instance.buy_digital_spot(active=pair, amount=amount, action=action,
                                                  duration=time_frame)
                        asyncio.run(api.set_schedule_status(trade_info_id, 1))

        if pair not in monitored_pairs:
            break
        time.sleep(1.0)
