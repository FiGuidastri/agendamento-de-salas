<?php
function get_db_connection() {
    $conn = new mysqli('localhost', 'root', 'root', 'agendamento_salas');

    if ($conn->connect_error) {
        die("Conexão falhou: " . $conn->connect_error);
    }

    return $conn;
}
?>
