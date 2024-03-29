import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()


async def get_status_bot(user_id: int):
    """
    Retorna o status do bot do usuário com o ID fornecido.

    Args:
        user_id (int): ID do usuário cujo status do bot deve ser retornado.

    Returns:
        dict: dicionário contendo o status do bot do usuário.
    """
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        try:
            async with session.get(f'https://v1.investingbrazil.online/bot/botoptions/id/{user_id}',
                                   headers=headers) as response:
                r = await response.json()
                status = r['status']
                return status
        except:
            if response.status != 200:
                new_attempt = await get_status_bot(user_id)
                return new_attempt


async def set_status_bot(user_id: int, status: int):
    """
    Atualiza o status do bot do usuário com o ID fornecido.

    Args:
        user_id (int): ID do usuário cujo status do bot deve ser atualizado.
        status (int): novo status do bot.
    """
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        async with session.put(f'https://v1.investingbrazil.online/bot/botoptions/status/{user_id}/{status}',
                               headers=headers) as response:
            r = await response.json()
            return r


async def get_news_status(user_id: int):
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        try:
            async with session.get(f'https://v1.investingbrazil.online/bot/botoptions/id/{user_id}',
                                   headers=headers) as response:
                r = await response.json()
                news = r['news']
                return news
        except:
            if response.status != 200:
                new_attempt = await get_news_status(user_id)
                return new_attempt


async def get_management_status(user_id: int):
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        try:
            async with session.get(f'https://v1.investingbrazil.online/bot/botoptions/id/{user_id}',
                                   headers=headers) as response:
                r = await response.json()
                management = r['management']
                return management
        except:
            if response.status != 200:
                new_attempt = await get_management_status(user_id)
                return new_attempt


async def set_schedule_status(trade_id: int, status: int, user_id: int):
    """
    Atualiza o status da trade de um usuário.

    Args:
        trade_info_id (int): ID da trade cujo status do agendamento deve ser atualizado.
        status (int): novo status do agendamento.
    """
    data = {
        'user_id': user_id,
        'trade_id': trade_id,
        'status_trade': status
    }
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        try:
            async with session.put(
                    f'https://v1.investingbrazil.online/bot/trades/update/status/{trade_id}/{user_id}',
                    json=data,
                    headers=headers) as response:
                return await response.json()
        except:
            if response.status != 200:
                new_attempt = await set_schedule_status(trade_id, status, user_id)
                return new_attempt


async def get_trade_info_pairs(user_id: int):
    """
    Retorna as moedas que podem ser negociadas.
    Returns:
        list: lista de moedas que podem ser negociadas.

    """
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        try:
            async with session.get(f'https://v1.investingbrazil.online/bot/trades/pairs/users/id/{user_id}',
                                   headers=headers) as response:
                r = await response.json()
                all = []
                for i in r:
                    all.append(i['pair'])
                return all
        except:
            if response.status != 200:
                new_attempt = await get_trade_info_pairs(user_id)
                return new_attempt


async def get_trade_user_info_scheduled(user_id: int):
    """
    Retorna as informações de trade do usuário com o ID fornecido.

    Args:
        user_id (int): ID do usuário cujas informações de trade devem ser retornadas.

    Returns:
        list: lista de dicionários contendo as informações de trade do usuário.
    """
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        try:
            async with session.get(f'https://v1.investingbrazil.online/bot/trades/user/id/{user_id}',
                                   headers=headers) as response:
                r = await response.json()
                all = []
                for i in r:
                    all.append(i['trade_id'])
                return all
        except:
            if response.status != 200:
                new_attempt = await get_trade_user_info_scheduled(user_id)
                return new_attempt


async def get_trade_info(trade_id: int):
    """
    Retorna as informações de trade do usuário com o ID fornecido.

    Args:
        trade_info_id (int): ID do usuário cujas informações de trade devem ser retornadas.

    Returns:
        list: lista de dicionários contendo as informações de trade do usuário.
    """
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        try:
            async with session.get(f'https://v1.investingbrazil.online/bot/trades/id/{trade_id}',
                                   headers=headers) as response:
                r = await response.json()
                return r
        except:
            if response.status != 200:
                new_attempt = await get_trade_info(trade_id)
                return new_attempt


async def get_user_values_by_trade_id(trade_id: int, user_id: int):
    """
    Retorna os valores do usuário com o ID fornecido.

    Args:
        trade_info_id (int): ID do usuário cujos valores devem ser retornados.

    Returns:
        list: lista de dicionários contendo os valores do usuário.
    """
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        try:
            async with session.get(f'https://v1.investingbrazil.online/bot/trades/status/id/{user_id}/{trade_id}',
                                   headers=headers) as response:
                r = await response.json()
                return r
        except:
            if response.status != 200:
                new_attempt = await get_user_values_by_trade_id(trade_id, user_id)
                return new_attempt


async def set_trade_associated_exited_if_buy(trade_id: int):
    """
    Atualiza o status do agendamento de todos os usuários que não aceitaram a trade até o momento da compra.

    Args:
        trade_id = ID da trade cujo status do agendamento deve ser atualizado.
    """
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        try:
            async with session.post(f'https://v1.investingbrazil.online/bot/trades/accept/all/id/{trade_id}',
                                    headers=headers) as response:
                return await response.json()
        except:
            if response.status != 200:
                new_attempt = await set_trade_associated_exited_if_buy(trade_id)
                return new_attempt


async def get_news_filter():
    """
    Retorna os horarios de noticias para cancelar entradas temporariamente.
    Returns:
        list: lista de notícias que podem ser negociadas.

    """
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        try:
            async with session.get(f'https://v1.investingbrazil.online/news/get_filter_news',
                                   headers=headers) as response:
                r = await response.json()
                return r
        except:
            if response.status != 200:
                new_attempt = await get_news_filter()
                return new_attempt


async def get_trade_status_by_user_id_and_trade_id(trade_id: int, user_id: int):
    """
    Retorna os valores do usuário com o ID fornecido.

    Args:
        trade_info_id (int): ID do usuário cujos valores devem ser retornados.

    Returns:
        list: lista de dicionários contendo os valores do usuário.
    """
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        try:
            async with session.get(f'https://v1.investingbrazil.online/bot/trades/status/id/{user_id}/{trade_id}',
                                   headers=headers) as response:
                r = await response.json()
                return r['status_trade']
        except:
            if response.status != 200:
                new_attempt = await get_user_values_by_trade_id(trade_id, user_id)
                return new_attempt


async def set_balance(user_id: int, balance: float):
    """
    Atualiza o status do agendamento de todos os usuários que não aceitaram a trade até o momento da compra.

    Args:
        trade_id = ID da trade cujo status do agendamento deve ser atualizado.
    """
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        data = {
            'balance': balance
        }
        try:
            async with session.post(f'https://v1.investingbrazil.online/bot/management/update/values/id/{user_id}', data=data,
                                    headers=headers) as response:
                return await response.json()
        except:
            if response.status != 200:
                new_attempt = await set_balance(user_id, balance)
                return new_attempt


async def reset_management_values(user_id: int):
    """
    Atualiza o status do agendamento de todos os usuários que não aceitaram a trade até o momento da compra.

    Args:
        trade_id = ID da trade cujo status do agendamento deve ser atualizado.
    """
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        try:
            async with session.get(f'https://v1.investingbrazil.online/bot/management/reset/id/{user_id}',
                                   headers=headers) as response:
                return await response.json()
        except:
            if response.status != 200:
                new_attempt = await reset_management_values(user_id)
                return new_attempt


async def get_management_values(user_id: int):
    """
    Atualiza o status do agendamento de todos os usuários que não aceitaram a trade até o momento da compra.

    Args:
        trade_id = ID da trade cujo status do agendamento deve ser atualizado.
    """
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        try:
            async with session.get(f'https://v1.investingbrazil.online/bot/management/id/{user_id}',
                                   headers=headers) as response:
                r = await response.json()
                return r
        except:
            if response.status != 200:
                new_attempt = await get_management_values(user_id)
                return new_attempt


async def update_management_values_gain(user_id: int, balance: float, value_gain: float):
    """
    Atualiza o status do agendamento de todos os usuários que não aceitaram a trade até o momento da compra.

    Args:
        trade_id = ID da trade cujo status do agendamento deve ser atualizado.
    """
    print(f'atualizando ganho user: {user_id}, balance: {balance}, ganho: {value_gain}')
    json = {
        "balance": balance,
        "value_gain": value_gain
    }
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        try:
            async with session.put(f'https://v1.investingbrazil.online/bot/management/update/values/id/{user_id}', json=json,
                                   headers=headers) as response:
                return await response.json()
        except:
            if response.status != 200:
                new_attempt = await update_management_values_gain(user_id, balance, value_gain)
                return new_attempt


async def update_management_values_loss(user_id: int, balance: float, value_loss: float):
    """
    Atualiza o status do agendamento de todos os usuários que não aceitaram a trade até o momento da compra.

    Args:
        trade_id = ID da trade cujo status do agendamento deve ser atualizado.
    """
    print(f'atualizando perca user: {user_id}, balance: {balance}, perca: {value_loss}')
    json = {
        "balance": balance,
        "value_loss": value_loss
    }
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        try:
            async with session.put(f'https://v1.investingbrazil.online/bot/management/update/values/id/{user_id}', json=json,
                                   headers=headers) as response:
                return await response.json()
        except:
            if response.status != 200:
                new_attempt = await update_management_values_loss(user_id, balance, value_loss)
                return new_attempt


async def stop_by_win(user_id: int):
    """
    Retorna os valores do usuário com o ID fornecido.

    Args:
        trade_info_id (int): ID do usuário cujos valores devem ser retornados.

    Returns:
        list: lista de dicionários contendo os valores do usuário.
    """
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        try:
            async with session.get(f'https://bot.investingbrazil.online/stop_win/{user_id}',
                                   headers=headers) as response:
                r = await response.json()
                return r
        except:
            if response.status != 200:
                new_attempt = await stop_by_win(user_id)
                return new_attempt


async def stop_by_loss(user_id: int):
    """
    Retorna os valores do usuário com o ID fornecido.

    Args:
        trade_info_id (int): ID do usuário cujos valores devem ser retornados.

    Returns:
        list: lista de dicionários contendo os valores do usuário.
    """
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        try:
            async with session.get(f'https://bot.investingbrazil.online/stop_loss/{user_id}',
                                   headers=headers) as response:
                r = await response.json()
                return r
        except:
            if response.status != 200:
                new_attempt = await stop_by_loss(user_id)
                return new_attempt
