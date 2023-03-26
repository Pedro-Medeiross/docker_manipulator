import aiohttp


async def get_status_bot(user_id: int):
    """
    Retorna o status do bot do usuário com o ID fornecido.

    Args:
        user_id (int): ID do usuário cujo status do bot deve ser retornado.

    Returns:
        dict: dicionário contendo o status do bot do usuário.
    """
    params = {
        'user_id': user_id
    }
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:3000/api/botoptions/', params=params) as response:
            r = await response.json()
            status = r[0]['status']
            return status


async def set_status_bot(user_id: int, status: int):
    """
    Atualiza o status do bot do usuário com o ID fornecido.

    Args:
        user_id (int): ID do usuário cujo status do bot deve ser atualizado.
        status (int): novo status do bot.
    """
    params = {
        'user_id': user_id,
        'status': status
    }
    async with aiohttp.ClientSession() as session:
        async with session.put('http://localhost:3000/api/botoptions/', params=params) as response:
            pass

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
        async with session.get('http://localhost:3000/api/userextensions/', params=params) as response:
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
        async with session.get('http://localhost:3000/api/userextensions/', params=params) as response:
            r = await response.json()
            password = r[0]['iqoption_password']
            return password
