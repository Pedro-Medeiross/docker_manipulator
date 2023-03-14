from datetime import date
import mysqldb


# Obtém as credenciais da IQ Option do usuário com o ID fornecido
def get_iqoption_credentials(id):
    conn = mysqldb.get_connection()  # obtém a conexão com o banco de dados
    cursor = conn.cursor()  # cria um cursor para executar as consultas SQL
    query = "SELECT * FROM users_userextension where user_id=%s"  # consulta SQL para selecionar as
    # credenciais do usuário
    cursor.execute(query, (id,))  # executa a consulta SQL, passando o ID do usuário como parâmetro
    result = cursor.fetchall()  # obtém os resultados da consulta
    cursor.close()  # fecha o cursor
    conn.close()  # fecha a conexão com o banco de dados
    return result  # retorna as credenciais da IQ Option do usuário com o ID fornecido


# Obtém o status do bot da IQ Option para o usuário com o ID fornecido
def status_bot(id):
    conn = mysqldb.get_connection()  # obtém a conexão com o banco de dados
    cursor = conn.cursor()  # cria um cursor para executar as consultas SQL
    query = "SELECT status FROM iqoption_botoptions WHERE user_id = %s"  # consulta SQL para selecionar o status do bot
    cursor.execute(query, (id,))  # executa a consulta SQL, passando o ID do usuário como parâmetro
    result = cursor.fetchone()[0]  # obtém o resultado da consulta
    cursor.close()  # fecha o cursor
    conn.close()  # fecha a conexão com o banco de dados
    return result  # retorna o status do bot da IQ Option para o usuário com o ID fornecido


# Define o status do bot da IQ Option para o usuário com o ID fornecido
def set_status_bot(id, status):
    conn = mysqldb.get_connection()  # obtém a conexão com o banco de dados
    cursor = conn.cursor()  # cria um cursor para executar as consultas SQL
    query = "UPDATE iqoption_botoptions SET status = %s WHERE user_id = %s"  # consulta SQL para atualizar
    # o status do bot
    cursor.execute(query, (status, id))  # executa a consulta SQL, passando o status e o ID do usuário como parâmetros
    cursor.close()  # fecha o cursor
    conn.commit()  # confirma a transação no banco de dados
    conn.close()  # fecha a conexão com o banco de dados


def get_trade_info_and_values(id):
    # Estabelece conexão com o banco de dados
    conn = mysqldb.get_connection()
    cursor = conn.cursor()

    # Query para obter todas as informações de negociação agendadas do usuário com id =
    # id e programadas para hoje (schedule = 1)
    query = "select schedule, trade_info_id, user_id from iqoption_tradeuserinfo where user_id = %s and schedule = 1"
    cursor.execute(query, (id,))
    results = cursor.fetchall()

    trade_user_ids = []
    trade_info_ids = []
    trade_infos = []
    user_values = []

    # Para cada negociação agendada, armazena seu id
    for trade_info in results:
        trade_info_ids.append(trade_info[1])

    # Para cada id de negociação armazenado, obtem as informações de negociação
    for trade_info_id in trade_info_ids:
        query = "select tipo_moeda, cotacao, tipo_negocio, time from iqoption_tradeinfo where id = %s"
        cursor.execute(query, (trade_info_id,))
        result_query = cursor.fetchall()
        trade_infos.append(result_query)

    # Para cada id de negociação armazenado, obtem as informações de negociação do usuário
    for trade_info_id in trade_info_ids:
        query = "select value, status, trade_info_id from iqoption_usertrades where trade_info_id = %s"
        cursor.execute(query, (trade_info_id,))
        result_querys = cursor.fetchall()
        user_values.append(result_querys)

    # Fecha conexão com o banco de dados
    cursor.close()
    conn.close()

    # Retorna um dicionário com as informações das negociações agendadas e informações do usuário para essas negociações
    result = {
        "trade_info": trade_infos,
        "user_values": user_values,
    }
    return result


def get_trade_info_pairs():
    # Obtém conexão com o banco de dados
    conn = mysqldb.get_connection()

    # Cria um cursor para executar as queries
    cursor = conn.cursor()

    # Obtém a data atual
    date_now = date.today()

    # Query para selecionar as moedas disponíveis nas informações de trade
    query = "SELECT DISTINCT tipo_moeda FROM iqoption_tradeinfo"

    # Executa a query
    cursor.execute(query)

    # Obtém todos os resultados da query
    result = cursor.fetchall()

    # Fecha o cursor e a conexão com o banco de dados
    cursor.close()
    conn.close()

    # Retorna o resultado da query
    return result


def set_schedule_status(id, status):
    # Obtém conexão com o banco de dados
    conn = mysqldb.get_connection()

    # Cria um cursor para executar as queries
    cursor = conn.cursor()

    # Query para obter o ID do trade do usuário com base no ID da informação de trade
    get_usertade_id = "select id from iqoption_usertrades where trade_info_id = %s"
    cursor.execute(get_usertade_id, (id,))
    result = cursor.fetchone()[0]

    # Query para atualizar o status do trade do usuário com base no ID do trade
    query = "UPDATE iqoption_usertrades SET status = %s WHERE id = %s"
    cursor.execute(query, (status, result))

    # Fecha o cursor, faz o commit da transação e fecha a conexão com o banco de dados
    cursor.close()
    conn.commit()
    conn.close()
