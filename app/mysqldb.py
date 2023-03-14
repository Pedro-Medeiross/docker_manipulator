import mysql.connector
import dotenv
import os

dotenv.load_dotenv()


def get_connection():
    """
    Cria uma conexão com o banco de dados MySQL, utilizando informações fornecidas em variáveis de ambiente.

    Returns:
        mysql.connector.connection.MySQLConnection: Uma conexão com o banco de dados MySQL.
    """
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        port=os.environ.get("DB_PORT"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
    )
