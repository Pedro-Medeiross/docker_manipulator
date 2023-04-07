import os
import asyncio
import api
from iqoption import IqOption

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


async def update_monitored_pairs(user_id: int):
    # Obtém os pares de moedas disponíveis para negociação
    trade_info_pairs = await api.get_trade_info_pairs(user_id)
    # Adiciona os pares que ainda não estão sendo monitorados
    for pair in trade_info_pairs:
        if pair not in monitored_pairs:
            monitored_pairs.append(pair)
            print('Monitorando par: ', pair)


async def monitor_pair(pair: str):
    print('Verificando par: ', pair)
    if pair not in candles_streams:
        candles_streams[pair] = Iq.start_candles_stream(pair, 60, 5)
    async for candle in candles_streams[pair]:
        print(f'par: {pair} candle: {candle}')
        for trade_info_id in trade_info_ids:
            trade_info = await api.get_trade_info(trade_info_id)
            user_values = await api.get_user_values_by_trade_id(trade_info_id)
            price = trade_info['price']
            action = trade_info['method']
            time_frame = trade_info['timeframe']
            amount = user_values['amount']
            trade_status = user_values['status']
            if candle["close"] == price:
                if trade_status == 0:
                    print('Comprando', pair, 'com valor de', price, 'em', time_frame, 'minutos', )
                    await Iq.buy_digital_spot(active=pair, amount=amount, action=action, duration=time_frame)
                    await api.set_schedule_status(trade_info_id, status=1, user_id=user_id)


async def main():
    global trade_info_ids
    while status_bot == 1:
        await update_monitored_pairs(user_id)
        tasks = [monitor_pair(pair) for pair in monitored_pairs]
        await asyncio.gather(*tasks)
        trade_info_ids = await api.get_trade_user_info_scheduled(user_id)

if __name__ == "__main__":
    asyncio.run(main())
