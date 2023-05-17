import asyncio
import os
import aiohttp


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
            async with session.get(f'https://v1.investingbrazil.online/management/values/{user_id}', headers=headers) as response:
                r = await response.json()
                return r
        except:
            if response.status != 200:
                new_attempt = await get_management_values(user_id)
                return new_attempt


async def update_management_values_loss(user_id: int, balance: float, value_loss: float):
    """
    Atualiza o status do agendamento de todos os usuários que não aceitaram a trade até o momento da compra.

    Args:
        trade_id = ID da trade cujo status do agendamento deve ser atualizado.
    """
    json = {
        {
            "balance": balance,
            "value_loss": value_loss
        }
    }
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        try:
            async with session.put(f'https://v1.investingbrazil.online/management/update/values/{user_id}', json=json, headers=headers) as response:
                return await response.json()
        except:
            if response.status != 200:
                new_attempt = await update_management_values_loss(user_id, balance, value_loss)
                return new_attempt


async def update_management_values_gain(user_id: int, balance: float, value_gain: float):
    """
    Atualiza o status do agendamento de todos os usuários que não aceitaram a trade até o momento da compra.

    Args:
        trade_id = ID da trade cujo status do agendamento deve ser atualizado.
    """
    json = {
        {
            "balance": balance,
            "value_gain": value_gain
        }
    }
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        try:
            async with session.put(f'https://v1.investingbrazil.online/management/update/values/{user_id}', json=json, headers=headers) as response:
                return await response.json()
        except:
            if response.status != 200:
                new_attempt = await update_management_values_gain(user_id, balance, value_gain)
                return new_attempt
