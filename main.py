import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import docker
import api

app = FastAPI()


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
async def start_bot(user_id: int):
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
        return {'message': 'Bot already running'}
    # Obtém as credenciais do usuário.
    email = await api.get_user_iqoption_email(user_id)
    password = await api.get_user_iqoption_password(user_id)
    if email is None or password is None:
        return {'message': 'Credentials not found'}
    # Verifica se há algum contêiner existente para esse usuário.
    containers = client.containers.list(all=True)
    env_vars = {
        'USER_ID': user_id,
        "EMAIL": email,
        "PASSWORD": password
    }
    for container in containers:
        if container.name == f'bot_{user_id}':
            if container.status == 'running':
                return {'message': 'Bot already running'}
            await api.set_status_bot(user_id, 1)
            container.start()
            return {'message': 'Bot started'}
    # Cria um novo contêiner para esse usuário.
    await api.set_status_bot(user_id, 1)
    client.containers.create(image='docker_bot:latest', name=f'bot_{user_id}', detach=True, environment=env_vars)
    client.containers.get(f'bot_{user_id}').start()
    return {'message': 'Bot created and started'}


@app.get("/stop/{user_id}")
async def stop_bot(user_id: int):
    """
    Para a execução do ‘cluster’ para um determinado usuário, se ele estiver em execução.

    Args:
        user_id (int): ID do usuário para o qual o ‘cluster’ deve ser interrompido.

    Returns:
        dict: dicionário contendo uma mensagem informando se o bot já estava parado ou se o bot foi parado com sucesso.
    """
    # Verifica se o bot já está parado.
    status_bot = await api.get_status_bot(user_id)
    if status_bot == 0:
        return {'message': 'Bot already stopped'}
    # Procura pelo contêiner do cluster e o para.
    containers = client.containers.list(all=True)
    for container in containers:
        if container.name == f'bot_{user_id}':
            await api.set_status_bot(user_id, 0)
            container.stop()
            return {'message': 'Bot stopped'}
    return {'message': 'Bot not found'}


@app.get("/status/{user_id}")
async def status_bot(user_id: int):
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
    for container in containers:
        if container.name == f'bot_{user_id}':
            return {'status': container.status}
    return {'status': 'Bot not found'}
