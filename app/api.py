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
        async with session.get(f'https://v1.investingbrazil.online/botoptions/{user_id}', headers=headers) as response:
            r = await response.json()
            status = r['status']
            return status


async def set_schedule_status(trade_id: int, status: int, user_id: int):
    """
    Atualiza o status do agendamento de um usuário.

    Args:
        trade_info_id (int): ID da trade cujo status do agendamento deve ser atualizado.
        status (int): novo status do agendamento.
    """
    data = {
        'status': status
    }
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        async with session.put(f'https://v1.investingbrazil.online/trade/associate/{trade_id}/{user_id}', json=data,
                               headers=headers) as response:
            return await response.json()


async def get_trade_info_pairs(user_id: int):
    """
    Retorna as moedas que podem ser negociadas.
    Returns:
        list: lista de moedas que podem ser negociadas.

    """
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        async with session.get(f'https://v1.investingbrazil.online/trades/{user_id}', headers=headers) as response:
            r = await response.json()
            ids = []
            pairs = []
            for i in r:
                ids.append(i['trade_id'])
            for j in ids:
                async with session.get(f'https://v1.investingbrazil.online/trade/{j}', headers=headers) as response:
                    r = await response.json()
                    pairs.append(r['pair'])
            return pairs


async def get_trade_user_info_scheduled(user_id: int):
    """
    Retorna as informações de trade do usuário com o ID fornecido.

    Args:
        user_id (int): ID do usuário cujas informações de trade devem ser retornadas.

    Returns:
        list: lista de dicionários contendo as informações de trade do usuário.
    """
    params = {
        'user_id': user_id
    }
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        async with session.get(f'https://v1.investingbrazil.online/trades/{user_id}', params=params,
                               headers=headers) as response:
            r = await response.json()
            all = []
            for i in r:
                all.append(i['trade_id'])
            return all

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
        async with session.get(f'https://v1.investingbrazil.online/trade/{trade_id}', headers=headers) as response:
            r = await response.json()
            return r


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
        async with session.get(f'https://v1.investingbrazil.online/trades/associated/{trade_id}/{user_id}', headers=headers) as response:
            r = await response.json()
            return r
