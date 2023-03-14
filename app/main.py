import os
import time
import repository
from iqoption import IqOption

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
instance = Iq.instance()

# Status do bot
status_bot = repository.status_bot(user_id)

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
    trade_info_pairs = repository.get_trade_info_pairs()
    print(trade_info_pairs)
    # Adiciona os pares que ainda não estão sendo monitorados
    for par in trade_info_pairs:
        if par[0] not in monitored_pairs:
            monitored_pairs.append(par[0])
            print('Monitorando par: ', par[0])


while status_bot == 1:
    update_monitored_pairs()
    trade_info_values = repository.get_trade_info_and_values(user_id)
    trade_info = trade_info_values["trade_info"]
    user_values = trade_info_values["user_values"]
    for pair in monitored_pairs:
        print('Verificando par: ', pair)
        if pair not in candles_streams:
            candles_streams[pair] = instance.start_candles_stream(pair, 1, 1)
        candles = instance.get_realtime_candles(pair, 1)
        candle = 0
        for key in candles:
            candle = candles[key]["open"]
            print(f'par: {pair} candle: {candle}')
            for i in range(len(trade_info)):
                price = trade_info[i][0][1]
                actions = trade_info[i][0][2]
                time_frame = trade_info[i][0][3]
                if actions == "C":
                    action = "call"
                elif actions == "V":
                    action = "put"
                for j in range(len(user_values)):
                    if user_values and len(user_values) > j and user_values[j]:
                        amount = user_values[j][0][0]
                        trade_info_id = user_values[j][0][2]
                        trade_status = user_values[j][0][1]
                if candle == price:
                    if trade_status == 0:
                        print('Comprando', pair, 'com valor de', price, 'em', time_frame, 'minutos', )
                        instance.buy_digital_spot(active=pair, amount=amount, action=action,
                                                  duration=time_frame)
                        repository.set_schedule_status(trade_info_id, 1)

        if pair not in monitored_pairs:
            break
        time.sleep(1.5)
