Dockerized Bot Control API
===============================
This project implements a Python API using the FastAPI framework to control an IQOption bot that is running inside a Docker container. It allows starting, stopping, and checking the status of the bot for a specific user.

Installation and Configuration
To install the project dependencies, execute the following command:

pip install -r requirements.txt

Before running the application, you need to create the following environment variables:

DB_HOST: database address
DB_NAME: database name
DB_PORT: database port
DB_USER: database user
DB_PASSWORD: database user's password

These variables can be defined in the .env file, following the example in the .env.example file.

Usage
Start the Bot
To start the bot for a specific user, make a GET request to the endpoint /start/{user_id}, where {user_id} is the ID of the user you want to start the bot for.

If the bot is already running for the provided user, the API will return the message "Bot already running."

If the user's credentials are not found in the database, the API will return the message "Credentials not found."

If the bot is not running for the provided user and there is no running container with the name bot_{user_id}, the API will create a new container with the docker_bot:latest image and the name bot_{user_id}, and return the message "Bot created and started."

If the bot is not running for the provided user and there is already a running container with the name bot_{user_id}, the API will start the existing container and return the message "Bot started."

Stop the Bot
To stop the bot for a specific user, make a GET request to the endpoint /stop/{user_id}, where {user_id} is the ID of the user you want to stop the bot for.

If the bot is already stopped for the provided user, the API will return the message "Bot already stopped."

If the bot is running for the provided user and there is a running container with the name bot_{user_id}, the API will stop the container and return the message "Bot stopped."

If the bot is not running for the provided user or there is no running container with the name bot_{user_id}, the API will return the message "Bot not found."

Check Bot Status
To check the status of the bot for a specific user, make a GET request to the endpoint /status/{user_id}, where {user_id} is the ID of the user you want to check the bot status for.

If the bot is running for the provided user and there is a running container with the name bot_{user_id}, the API will return the status of the container.

If the bot is not running for the provided user or there is no running container with the name bot_{user_id}, the API will return the message "Bot not found."




API de controle de bot dockerizado
===============================
Este projeto implementa uma API em Python usando o framework FastAPI para controle de um bot IQOption que está em um container Docker. É possível iniciar, parar e verificar o status do bot para um determinado usuário.

## Instalação e configuração
Para instalar as dependências do projeto, execute o seguinte comando:

    pip install -r requirements.txt

Antes de executar a aplicação, é necessário criar as seguintes variáveis de ambiente:

<ul>
<li> DB_HOST: endereço do banco de dados </li>
<li> DB_NAME: nome do banco de dados </li>
<li> DB_PORT: porta do banco de dados </li>
<li> DB_USER: usuário do banco de dados </li>
<li> DB_PASSWORD: senha do usuário do banco de dados </li>
</ul>

Essas variáveis podem ser definidas no arquivo .env, seguindo o exemplo do arquivo .env.example.

## Utilização

### Iniciar o bot

Para iniciar o bot para um determinado usuário, faça uma requisição GET para o endpoint /start/{user_id}, onde {user_id} é o ID do usuário para o qual se deseja iniciar o bot.

Se o bot já estiver em execução para o usuário informado, a API retornará a mensagem Bot already running.

Se as credenciais do usuário não foram encontradas no banco de dados, a API retornará a mensagem Credentials not found.

Se o bot não estiver em execução para o usuário informado e não existir um container em execução com o nome bot_{user_id}, a API criará um novo container com a imagem docker_bot:latest e o nome bot_{user_id}, e retornará a mensagem Bot created and started.

Se o bot não estiver em execução para o usuário informado e já existir um container em execução com o nome bot_{user_id}, a API iniciará o container existente e retornará a mensagem Bot started.

### Parar o bot

Para parar o bot para um determinado usuário, faça uma requisição GET para o endpoint /stop/{user_id}, onde {user_id} é o ID do usuário para o qual se deseja parar o bot.

Se o bot já estiver parado para o usuário informado, a API retornará a mensagem Bot already stopped.

Se o bot estiver em execução para o usuário informado e existir um container em execução com o nome bot_{user_id}, a API parará o container e retornará a mensagem Bot stopped.

Se o bot não estiver em execução para o usuário informado ou não existir um container em execução com o nome bot_{user_id}, a API retornará a mensagem Bot not found.

### Verificar status do bot

Para verificar o status do bot para um determinado usuário, faça uma requisição GET para o endpoint /status/{user_id}, onde {user_id} é o ID do usuário para o qual se deseja verificar o status do bot.

Se o bot estiver em execução para o usuário informado e existir um container em execução com o nome bot_{user_id}, a API retornará o status do container.

Se o bot não estiver em execução para o usuário informado ou não existir um container em execução com o nome bot_{user_id}, a API retornará a mensagem Bot not found.
