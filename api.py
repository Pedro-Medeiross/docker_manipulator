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
        async with session.get(f'https://v1.investingbrazil.online/bot/botoptions/id/{user_id}', headers=headers) as response:
            r = await response.json()
            status = r['status']
            return status


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
        async with session.put(f'https://v1.investingbrazil.online/bot/botoptions/status/{user_id}/{status}', headers=headers) as response:
            r = await response.json()
            return r


async def get_user_iqoption_email(user_id: int):
    """
    Retorna o email do usuário com o ID fornecido.

    Args:
        user_id (int): ID do usuário cujo email deve ser retornado.

    Returns:
        str: email do usuário.
    """
    payload = {
    "user_id": user_id
    }
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        async with session.get(f'https://v1.investingbrazil.online/bot/user/{user_id}', headers=headers, json=payload) as response:
            r = await response.json()
            email = r['brokerage_email']
            return email


async def get_user_iqoption_password(user_id: int):
    """
    Retorna a senha do usuário com o ID fornecido.

    Args:
        user_id (int): ID do usuário cuja senha deve ser retornada.

    Returns:
        str: senha do usuário.
    """
    payload = {
    "user_id": user_id
    }
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        async with session.get(f'https://v1.investingbrazil.online/bot/user/{user_id}', headers=headers, json=payload) as response:
            r = await response.json()
            password = r['brokerage_password']
            return password


async def get_account_type(user_id: int):
    """
    Retorna o tipo de conta do usuário com o ID fornecido.
    Args:
        user_id: ID do usuário cujo tipo de conta deve ser retornado.

    Returns: tipo de conta do usuário.

    """
    payload = {
    "user_id": user_id
    }
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        async with session.get(f'https://v1.investingbrazil.online/bot/user/{user_id}', headers=headers, json=payload) as response:
            r = await response.json()
            account_type = r['account_type']
            return account_type


async def restart_bot(user_id: int):
    """
    Reinicia o bot do usuário com o ID fornecido.

    Args:
        user_id (int): ID do usuário cujo bot deve ser reiniciado.
    """
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        async with session.post(f'https://bot.investingbrazil.online/restart/{user_id}', headers=headers) as response:
            r = await response.json()
            return r
