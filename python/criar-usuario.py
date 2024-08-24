from flask_bcrypt import Bcrypt
from db import get_db_connection

bcrypt = Bcrypt()

# Conexão com o banco de dados
conn = get_db_connection()
cursor = conn.cursor()

# Gerar senha hashada
username = 'filipe.guidastri'
password = 'fag250811'
hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

# Inserir usuário no banco de dados
cursor.execute("INSERT INTO tab_usuarios (username, password_hash) VALUES (%s, %s)", (username, hashed_password))

# Confirmar e fechar conexão
conn.commit()
cursor.close()
conn.close()

print(f"Usuário {username} criado com sucesso!")
