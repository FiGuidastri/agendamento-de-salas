import calendar
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from db import get_db_connection
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Você pode usar uma chave secreta gerada para segurança

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelo de usuário
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, password_hash FROM tab_usuarios WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(id=user[0], username=user[1], password=user[2])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password_hash FROM tab_usuarios WHERE username = %s', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.check_password_hash(user[2], password):
            user_obj = User(id=user[0], username=user[1], password=user[2])
            login_user(user_obj)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Usuário ou senha incorretos', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    today = datetime.today()
    year = today.year
    month = today.month
    meses = {
        1: "Janeiro",
        2: 'Fevereiro',
        3: 'Março',
        4: 'Abril',
        5: 'Maio',
        6: 'Junho',
        7: 'Julho',
        8: 'Agosto',
        9: 'Setembro',
        10: 'Outubro',
        11: 'Novembro',
        12: 'Dezembro'
    }

    # Gerar um calendário para o mês atual
    cal = calendar.Calendar()
    month_days = cal.itermonthdays(year, month)

    # Conectar ao banco de dados
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obter os agendamentos e os nomes dos usuários
    cursor.execute("""
        SELECT a.id, a.sala_id, a.data, a.horario_inicio, a.horario_fim, a.quantidade_pessoas, a.motivo, u.username 
        FROM tab_agendamentos a
        JOIN tab_usuarios u ON a.usuario_id = u.id
        WHERE MONTH(a.data) = %s AND YEAR(a.data) = %s
    """, (month, year))
    agendamentos = cursor.fetchall()

    # Obter os nomes das salas
    cursor.execute('SELECT id, nome FROM tab_salas')
    salas = cursor.fetchall()
    sala_dict = {sala[0]: sala[1] for sala in salas}

    # Organizar as reuniões por dia e substituir IDs por nomes
    agendamentos_por_dia = {}
    for agendamento in agendamentos:
        dia = agendamento[2].day
        if dia not in agendamentos_por_dia:
            agendamentos_por_dia[dia] = []
        # Incluir o nome do usuário na exibição
        nome_sala = sala_dict.get(agendamento[1], 'Desconhecida')
        usuario = agendamento[7]  # Nome do usuário
        agendamentos_por_dia[dia].append((nome_sala, *agendamento[2:7], usuario))

    cursor.close()
    conn.close()

    return render_template('home.html', month_days=month_days, today=today, agendamentos_por_dia=agendamentos_por_dia, month=month, year=year, month_name=meses[month])

@app.route('/agendar')
@login_required
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome FROM tab_salas')
    salas = cursor.fetchall()
    conn.close()
    return render_template('agendar.html', salas=salas)

@app.route('/agendar', methods=['POST'])
@login_required
def agendar():
    sala_id = request.form['sala']
    data = request.form['data']
    inicio = request.form['inicio']
    fim = request.form['fim']
    quantidade_pessoas = int(request.form['quantidade_pessoas'])
    motivo = request.form['motivo']
    usuario_id = current_user.id  # Aqui você usa o current_user

    conn = get_db_connection()
    cursor = conn.cursor()

    # Validação de conflito de horários
    cursor.execute(
        "SELECT * FROM tab_agendamentos WHERE sala_id = %s AND data = %s AND (horario_inicio < %s AND horario_fim > %s)",
        (sala_id, data, fim, inicio)
    )
    conflito = cursor.fetchone()

    if conflito:
        return 'Conflito de horário! Tente outro horário ou sala.'

    # Validação de capacidade de sala
    cursor.execute('SELECT capacidade FROM tab_salas WHERE id = %s', (sala_id,))
    sala = cursor.fetchone()

    if quantidade_pessoas > sala[0]:
        return 'Sala não tem capacidade para essa quantidade de pessoas! Tente outra sala!'

    # Inserir o agendamento
    cursor.execute(
        "INSERT INTO tab_agendamentos (sala_id, data, horario_inicio, horario_fim, quantidade_pessoas, motivo, usuario_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (sala_id, data, inicio, fim, quantidade_pessoas, motivo, usuario_id)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
