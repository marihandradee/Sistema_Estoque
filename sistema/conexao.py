import mysql.connector
from mysql.connector import Error
from config_local import DB_CONFIG


def conectar():
    try:
        banco = mysql.connector.connect(**DB_CONFIG)
        return banco
    except Error as erro:
        print("Erro na conexão com o banco:", erro)
        return None