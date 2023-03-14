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