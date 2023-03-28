import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()


async def get_status_bot(user_id):
    """
        Retorna o status do bot do usuário com o ID fornecido.

        Args:
            user_id (int): O ID do usuário cujo status do bot deve ser retornado.

        Returns:
            dict: Um dicionário contendo o status do bot do usuário.
        """
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        async with session.get(f'https://v1.investingbrazil.online/api/status_bot/{user_id}', headers=headers) as response:
            status = await response.json()
            r = status[0]['status']
            return r


async def get_user_iqoption_email(user_id: int):
    """
    Retorna o email do usuário com o ID fornecido.

    Args:
        user_id (int): ID do usuário cujo email deve ser retornado.

    Returns:
        str: email do usuário.
    """
    params = {
        'user_id': user_id
    }
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        async with session.get('https://v1.investingbrazil.online/api/userextensions/', params=params,
                               headers=headers) as response:
            r = await response.json()
            email = r[0]['iqoption_email']
            return email


async def get_user_iqoption_password(user_id: int):
    """
    Retorna a senha do usuário com o ID fornecido.

    Args:
        user_id (int): ID do usuário cuja senha deve ser retornada.

    Returns:
        str: senha do usuário.
    """
    params = {
        'user_id': user_id
    }
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        async with session.get('https://v1.investingbrazil.online/api/userextensions/', params=params,
                               headers=headers) as response:
            r = await response.json()
            password = r[0]['iqoption_password']
            return password


async def set_schedule_status(trade_info_id: int, status: int):
    """
    Atualiza o status do agendamento de um usuário.

    Args:
        trade_info_id (int): ID da trade cujo status do agendamento deve ser atualizado.
        status (int): novo status do agendamento.
    """
    params = {
        'trade_info_id': trade_info_id,
        'status': status
    }
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        async with session.put('https://v1.investingbrazil.online/api/usertrades/', params=params,
                               headers=headers) as response:
            return await response.json()


async def get_trade_info_pairs():
    """
    Retorna as moedas que podem ser negociadas.
    Returns:
        list: lista de moedas que podem ser negociadas.

    """
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        async with session.get('https://v1.investingbrazil.online//api/tradeinfo/', headers=headers) as response:
            r = await response.json()
            pairs = []
            for i in r:
                if i['tipo_moeda'] not in pairs:
                    pairs.append(i['tipo_moeda'])
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
        async with session.get('https://v1.investingbrazil.online/api/tradeuserinfo/', params=params,
                               headers=headers) as response:
            r = await response.json()
            trade_info_ids = []
            for i in r:
                if i['trade_info'] not in trade_info_ids:
                    trade_info_ids.append(i['trade_info'])
            return trade_info_ids


async def get_trade_info(trade_info_id: int):
    """
    Retorna as informações de trade do usuário com o ID fornecido.

    Args:
        trade_info_id (int): ID do usuário cujas informações de trade devem ser retornadas.

    Returns:
        list: lista de dicionários contendo as informações de trade do usuário.
    """
    params = {
        'id': trade_info_id
    }
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        async with session.get('https://v1.investingbrazil.online/api/tradeinfo/', params=params,
                               headers=headers) as response:
            r = await response.json()
            return r


async def get_user_values_by_trade_id(trade_info_id: int):
    """
    Retorna os valores do usuário com o ID fornecido.

    Args:
        trade_info_id (int): ID do usuário cujos valores devem ser retornados.

    Returns:
        list: lista de dicionários contendo os valores do usuário.
    """
    params = {
        'trade_info_id': trade_info_id
    }
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        async with session.get('https://v1.investingbrazil.online/api/usertrades/', params=params,
                               headers=headers) as response:
            r = await response.json()
            return r