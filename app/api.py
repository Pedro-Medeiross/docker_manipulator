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
        async with session.get(f'http://localhost:5000/api/status_bot/{user_id}', headers=headers) as response:
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
        async with session.get('http://localhost:3000/api/userextensions/', params=params, headers=headers) as response:
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
    async with aiohttp.ClientSession() as session:+
    auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
    headers = {'Authorization': auth.encode()}
        async with session.get('http://localhost:3000/api/userextensions/', params=params, headers=headers) as response:
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
        async with session.put('http://localhost:3000/api/usertrades/', params=params, headers=headers) as response:
            return await response.json()



