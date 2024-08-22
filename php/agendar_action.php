<?php
include 'db.php';

$sala = $_POST['sala'];
$data = $_POST['data'];
$inicio = $_POST['inicio'];
$fim = $_POST['fim'];
$quantidade_pessoas = $_POST['quantidade_pessoas'];
$motivo = $_POST['motivo'];

$conn = get_db_connection();

$stmt = $conn->prepare("INSERT INTO tab_agendamentos (sala_id, data, horario_inicio, horario_fim, quantidade_pessoas, motivo) 
                        VALUES (?, ?, ?, ?, ?, ?)");
$stmt->bind_param('isssis', $sala, $data, $inicio, $fim, $quantidade_pessoas, $motivo);

if ($stmt->execute()) {
    header("Location: index.php");
} else {
    echo "Erro ao agendar: " . $stmt->error;
}

$conn->close();
?>
