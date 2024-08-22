import calendar
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for
from db import get_db_connection

app = Flask(__name__)

@app.route('/')
def home():
    today = datetime.today()
    year = today.year
    month = today.month

    # Gerar um calendário para o mês atual
    cal = calendar.Calendar()
    month_days = cal.itermonthdays(year, month)

    # Conectar ao banco de dados
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obter as reuniões agendadas para o mês atual
    cursor.execute("""
        SELECT id, sala_id, data, horario_inicio, horario_fim, quantidade_pessoas, motivo 
        FROM tab_agendamentos 
        WHERE MONTH(data) = %s AND YEAR(data) = %s
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
        # Substituir o ID da sala pelo nome
        nome_sala = sala_dict.get(agendamento[1], 'Desconhecida')
        agendamentos_por_dia[dia].append((nome_sala, *agendamento[2:]))

    cursor.close()
    conn.close()

    return render_template('home.html', month_days=month_days, today=today, agendamentos_por_dia=agendamentos_por_dia, month=month, year=year, month_name=calendar.month_name[month])

@app.route('/agendar')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome FROM tab_salas')
    salas = cursor.fetchall()
    conn.close()
    return render_template('agendar.html', salas=salas)

@app.route('/agendar', methods=['POST'])
def agendar():
    sala_id = request.form['sala']
    data = request.form['data']
    inicio = request.form['inicio']
    fim = request.form['fim']
    quantidade_pessoas = int(request.form['quantidade_pessoas'])
    motivo = request.form['motivo']

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
        "INSERT INTO tab_agendamentos (sala_id, data, horario_inicio, horario_fim, quantidade_pessoas, motivo) VALUES (%s, %s, %s, %s, %s, %s)",
        (sala_id, data, inicio, fim, quantidade_pessoas, motivo)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
