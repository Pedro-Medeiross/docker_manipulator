import mysqldb

def get_iqoption_credentials(id):
    """
    Obtém as credenciais do usuário a partir do seu ID.

    Args:
        id (int): O ID do usuário.

    Returns:
        list: Uma lista com as informações do usuário obtidas do banco de dados.
    """
    conn = mysqldb.get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM users_userextension where user_id=%s"
    cursor.execute(query, (id,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def status_bot(id):
    """
    Obtém o status atual do robô a partir do ID do usuário.

    Args:
        id (int): O ID do usuário.

    Returns:
        str: O status atual do robô.
    """
    conn = mysqldb.get_connection()
    cursor = conn.cursor()
    query = "SELECT status FROM iqoption_botoptions WHERE user_id = %s"
    cursor.execute(query, (id,))
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return result


def set_status_bot(id, status):
    """
    Define o status do robô para o valor fornecido, a partir do ID do usuário.

    Args:
        id (int): O ID do usuário.
        status (str): O novo status do robô.

    Returns:
        None
    """
    conn = mysqldb.get_connection()
    cursor = conn.cursor()
    query = "UPDATE iqoption_botoptions SET status = %s WHERE user_id = %s"
    cursor.execute(query, (status, id))
    cursor.close()
    conn.commit()
    conn.close()
