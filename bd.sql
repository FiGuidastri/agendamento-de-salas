CREATE DATABASE IF NOT EXISTS agendamento_salas;

CREATE TABLE tab_salas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    capacidade INT NOT NULL
);

CREATE TABLE tab_agendamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sala_id INT,
    data DATE,
    horario_inicio TIME,
    horario_fim TIME,
    quantidade_pessoas INT,
    motivo TEXT,
    FOREIGN KEY (sala_id) REFERENCES tab_salas(id)
);
