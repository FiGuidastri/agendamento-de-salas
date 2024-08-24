import pymysql

def get_db_connection():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='asdqwe123!@#',
        database='agendamento_salas'
    )
    return connection