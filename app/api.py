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


def get_user_iqoption_email(user_id: int):
    """
    Retorna o email do usuário com o ID fornecido.

    Args:
        user_id (int): ID do usuário cujo email deve ser retornado.

    Returns:
        str: email do usuário.
    """
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        async with session.get(f'https://v1.investingbrazil.online/user/id/{user_id}', headers=headers) as response:
            r = await response.json()
            email = r['brokerage_email']
            return email


def get_user_iqoption_password(user_id: int):
    """
    Retorna a senha do usuário com o ID fornecido.

    Args:
        user_id (int): ID do usuário cuja senha deve ser retornada.

    Returns:
        str: senha do usuário.
    """
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        async with session.get(f'https://v1.investingbrazil.online/user/id/{user_id}', headers=headers) as response:
            r = await response.json()
            password = r['brokerage_password']
            return password


def get_account_type(user_id: int):
    """
    Retorna o tipo de conta do usuário com o ID fornecido.
    Args:
        user_id: ID do usuário cujo tipo de conta deve ser retornado.

    Returns: tipo de conta do usuário.

    """
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        async with session.get(f'https://v1.investingbrazil.online/user/id/{user_id}', headers=headers) as response:
            r = await response.json()
            account_type = r['account_type']
            return account_type


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
        async with session.put(f'https://v1.investingbrazil.online/trade/associate/{trade_id}/{user_id}', data=data,
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
            trade_info_ids = []
            for i in r:
                trade_info_ids.append(i['trade_id'])
            return trade_info_ids


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
            print(r)
            return r


async def get_user_values_by_trade_id(trade_id: int):
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
        async with session.get(f'https://v1.investingbrazil.online/trades/associated/{trade_id}', headers=headers) as response:
            r = await response.json()
            return r

import asyncio
print(asyncio.run(get_user_values_by_trade_id(1)))