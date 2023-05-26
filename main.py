import os
import secrets
import docker
import api
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from fastapi import Depends, HTTPException, status

app = FastAPI()
security = HTTPBasic()


origins = ["http://localhost:3000", "http://127.0.0.1/8000", "http://localhost:8000", "http://localhost:3000",
           "https://v1.investingbrazil.online", "https://investingbrazil.online"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = docker.from_env()


def get_basic_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, os.getenv('API_USER'))
    correct_password = secrets.compare_digest(credentials.password, os.getenv('API_PASS'))
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# Verifica se a imagem docker já existe, senão constrói uma nova.
images = client.images.list()
if 'docker_bot:latest' not in [image.tags[0] for image in images]:
    print('Image not found, building new image, this may take a while...')
    print('Please wait...')
    client.images.build(path='.', dockerfile='./Dockerfile', tag='docker_bot:latest')
    print('Image built successfully')
else:
    print('Image found, skipping build')


@app.get("/start/{user_id}")
async def start_bot(user_id: int, credentials: HTTPBasicCredentials = Depends(get_basic_credentials)):
    """
    Inicia um novo contêiner para executar o ‘cluster’ para um determinado usuário, se ele ainda não estiver em
    execução.

    Args:
        user_id (int): ID do usuário para o qual o ‘cluster’ deve ser iniciado.

    Returns:
        dict: dicionário contendo uma mensagem informando se o ‘cluster’ já estava em execução, se as credenciais
         não foram encontradas, ou se o ‘cluster’ foi iniciado com sucesso.
    """
    # Verifica se o ‘cluster’ já está em execução.
    status_bot = await api.get_status_bot(user_id)
    if status_bot == 1:
        return {'message': 'App ja iniciado!'}
    # Obtém as credenciais do usuário.
    email = await api.get_user_iqoption_email(user_id)
    password = await api.get_user_iqoption_password(user_id)
    if email is None or password is None:
        return {'message': 'email e senha da corretora não cadastrados'}
    # Verifica se há algum contêiner existente para esse usuário.
    containers = client.containers.list(all=True)
    env_vars = {
        'USER_ID': user_id,
        "EMAIL": email,
        "PASSWORD": password,
        "ACCOUNT_TYPE": await api.get_account_type(user_id),
    }
    for container in containers:
        if container.name == f'bot_{user_id}':
            if container.status == 'running':
                return {'message': 'App ja iniciado!'}
            await api.set_status_bot(user_id, 1)
            container.start()
            return {'message': 'App iniciado!'}
    # Cria um novo contêiner para esse usuário.
    await api.set_status_bot(user_id, 1)
    client.containers.create(image='docker_bot:latest', name=f'bot_{user_id}', detach=True, environment=env_vars)
    client.containers.get(f'bot_{user_id}').start()
    return {'message': 'Bot created and started'}


@app.get("/stop/{user_id}")
async def stop_bot(user_id: int, credentials: HTTPBasicCredentials = Depends(get_basic_credentials)):
    """
    Para a execução do ‘cluster’ para um determinado usuário, se ele estiver em execução.

    Args:
        user_id (int): ID do usuário para o qual o ‘cluster’ deve ser interrompido.

    Returns:
        dict: dicionário contendo uma mensagem informando se o bot já estava parado ou se o bot foi parado com sucesso.
    """
    # Verifica se o bot já está parado.
    status_bot = await api.get_status_bot(user_id)
    if status_bot in [0, 2, 3]:
        return {'message': 'App ja parado!'}
    # Procura pelo contêiner do cluster e o para.
    containers = client.containers.list(all=True)
    for container in containers:
        if container.name == f'bot_{user_id}':
            await api.set_status_bot(user_id, 0)
            container.stop()
            return {'message': 'App Parado'}
    return {'message': 'Erro ao parar o App'}


@app.get("/status/{user_id}")
async def status_bot(user_id: int, credentials: HTTPBasicCredentials = Depends(get_basic_credentials)):
    """
    Endpoint que retorna o estado do ‘cluster’ do usuário com o ID fornecido.

    Args:
        user_id (int): ID do usuário cujo estado do ‘cluster’ deve ser retornado.

    Returns:
        Um dicionário JSON contendo o estado do ‘cluster’ do usuário.

        Exemplo de retorno bem-sucedido:
        {
            "status": "running"
        }

        Se o bot não for encontrado, retorna um dicionário com uma mensagem de erro.
        Exemplo de retorno de erro:
        {
            "status": "Bot not found"
        }
    """
    containers = client.containers.list(all=True)
    status = api.get_status_bot(user_id)
    for container in containers:
        if container.name == f'bot_{user_id}':
            if container.status == 'exited' and status == 2:
                return {'status': 'Parado por stop win!'}
            elif container.status == 'exited' and status == 3:
                return {'status': 'Parado por stop loss!'}
            elif container.status == 'exited' and status== 0:
                return {'status': 'Parado!'}
            elif container.status == 'running' and status == 1:
                return {'status': 'Rodando!'}
            elif container.status == 'exited' and status == 1:
                await api.restart_bot(user_id)
    return {'status': 'App não encontrado'}



app.get("/stop_loss/{user_id}")
async def stop_loss(user_id: int, credentials: HTTPBasicCredentials = Depends(get_basic_credentials)):
    """
    Para a execução do ‘cluster’ para um determinado usuário, se ele estiver em execução.

    Args:
        user_id (int): ID do usuário para o qual o ‘cluster’ deve ser interrompido.

    Returns:
        dict: dicionário contendo uma mensagem informando se o bot já estava parado ou se o bot foi parado com sucesso.
    """
    # Verifica se o bot já está parado.
    status_bot = await api.get_status_bot(user_id)
    if status_bot in [0, 2, 3]:
        return {'message': 'App ja parado!'}
    # Procura pelo contêiner do cluster e o para.
    containers = client.containers.list(all=True)
    for container in containers:
        if container.name == f'bot_{user_id}':
            await api.set_status_bot(user_id, 3)
            container.stop()
            return {'message': 'App Parado por stop loss!'}
    return {'message': 'Erro ao parar o App'}


@app.get("/stop_win/{user_id}")
async def stop_win(user_id: int, credentials: HTTPBasicCredentials = Depends(get_basic_credentials)):
    """
    Para a execução do ‘cluster’ para um determinado usuário, se ele estiver em execução.

    Args:
        user_id (int): ID do usuário para o qual o ‘cluster’ deve ser interrompido.

    Returns:
        dict: dicionário contendo uma mensagem informando se o bot já estava parado ou se o bot foi parado com sucesso.
    """
    # Verifica se o bot já está parado.
    status_bot = await api.get_status_bot(user_id)
    if status_bot in [0, 2, 3]:
        return {'message': 'App ja parado!'}
    # Procura pelo contêiner do cluster e o para.
    containers = client.containers.list(all=True)
    for container in containers:
        if container.name == f'bot_{user_id}':
            await api.set_status_bot(user_id, 2)
            container.stop()
            return {'message': 'App Parado por stop win!'}
    return {'message': 'Erro ao parar o App'}


@app.get("/restart/{user_id}")
async def restart_bot(user_id: int, credentials: HTTPBasicCredentials = Depends(get_basic_credentials)):
    """
    Reinicia o ‘cluster’ para um determinado usuário, se ele estiver em execução.

    Args:
        user_id (int): ID do usuário para o qual o ‘cluster’ deve ser reiniciado.

    Returns:
        dict: dicionário contendo uma mensagem informando se o bot já estava parado ou se o bot foi reiniciado com sucesso.
    """
    # Verifica se o bot já está parado.
    status_bot = await api.get_status_bot(user_id)
    # Procura pelo contêiner do cluster e o para.
    containers = client.containers.list(all=True)
    for container in containers:
        if container.name == f'bot_{user_id}':
            container.restart()
            return {'message': 'App reiniciado!'}
    return {'message': 'Erro ao reiniciar o App'}


@app.get("/stop/win/{user_id}")
async def stop_win(user_id: int, credentials: HTTPBasicCredentials = Depends(get_basic_credentials)):
    """
    Para a execução do ‘cluster’ para um determinado usuário, se ele estiver em execução.

    Args:
        user_id (int): ID do usuário para o qual o ‘cluster’ deve ser interrompido.

    Returns:
        dict: dicionário contendo uma mensagem informando se o bot já estava parado ou se o bot foi parado com sucesso.
    """
    # Verifica se o bot já está parado.
    status_bot = await api.get_status_bot(user_id)
    if status_bot in [0, 2, 3]:
        return {'message': 'App ja parado!'}
    # Procura pelo contêiner do cluster e o para.
    containers = client.containers.list(all=True)
    for container in containers:
        if container.name == f'bot_{user_id}':
            await api.set_status_bot(user_id, 2)
            container.stop()
            return {'message': 'App Parado por stop win!'}
    return {'message': 'Erro ao parar o App'}


@app.get("/stop/loss/{user_id}")
async def stop_loss(user_id: int, credentials: HTTPBasicCredentials = Depends(get_basic_credentials)):
    """
    Para a execução do ‘cluster’ para um determinado usuário, se ele estiver em execução.

    Args:
        user_id (int): ID do usuário para o qual o ‘cluster’ deve ser interrompido.

    Returns:
        dict: dicionário contendo uma mensagem informando se o bot já estava parado ou se o bot foi parado com sucesso.
    """
    # Verifica se o bot já está parado.
    status_bot = await api.get_status_bot(user_id)
    if status_bot in [0, 2, 3]:
        return {'message': 'App ja parado!'}
    # Procura pelo contêiner do cluster e o para.
    containers = client.containers.list(all=True)
    for container in containers:
        if container.name == f'bot_{user_id}':
            await api.set_status_bot(user_id, 3)
            container.stop()
            return {'message': 'App Parado por stop loss!'}
    return {'message': 'Erro ao parar o App'}