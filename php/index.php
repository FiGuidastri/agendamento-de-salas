<?php
include 'db.php';

$today = new DateTime();
$year = $today->format('Y');
$month = $today->format('m');

// Mapeamento dos nomes dos meses em português
$meses = [
    1 => 'Janeiro',
    2 => 'Fevereiro',
    3 => 'Março',
    4 => 'Abril',
    5 => 'Maio',
    6 => 'Junho',
    7 => 'Julho',
    8 => 'Agosto',
    9 => 'Setembro',
    10 => 'Outubro',
    11 => 'Novembro',
    12 => 'Dezembro',
];

// Gerar um calendário para o mês atual
$cal = new DateTime();
$cal->setDate($year, $month, 1);

// Obter o dia da semana do primeiro dia do mês (1 para segunda-feira, 7 para domingo)
$first_day_of_week = $cal->format('N');

// Preencher dias vazios antes do início do mês
$month_days = array_fill(0, $first_day_of_week - 1, 0);

while ($cal->format('m') == $month) {
    $month_days[] = $cal->format('j');
    $cal->modify('+1 day');
}

// Conectar ao banco de dados
$conn = get_db_connection();

// Obter as reuniões agendadas para o mês atual
$stmt = $conn->prepare("SELECT id, sala_id, data, horario_inicio, horario_fim, quantidade_pessoas, motivo 
                        FROM tab_agendamentos 
                        WHERE MONTH(data) = ? AND YEAR(data) = ?");
$stmt->bind_param('ii', $month, $year);
$stmt->execute();
$result = $stmt->get_result();
$agendamentos = $result->fetch_all(MYSQLI_ASSOC);

// Obter os nomes das salas
$sala_stmt = $conn->query("SELECT id, nome FROM tab_salas");
$salas = $sala_stmt->fetch_all(MYSQLI_ASSOC);
$sala_dict = [];
foreach ($salas as $sala) {
    $sala_dict[$sala['id']] = $sala['nome'];
}

// Organizar as reuniões por dia e substituir IDs por nomes
$agendamentos_por_dia = [];
foreach ($agendamentos as $agendamento) {
    $dia = (new DateTime($agendamento['data']))->format('j');
    if (!isset($agendamentos_por_dia[$dia])) {
        $agendamentos_por_dia[$dia] = [];
    }
    $nome_sala = $sala_dict[$agendamento['sala_id']] ?? 'Desconhecida';
    $agendamentos_por_dia[$dia][] = [
        'sala' => $nome_sala,
        'inicio' => $agendamento['horario_inicio'],
        'fim' => $agendamento['horario_fim'],
        'pessoas' => $agendamento['quantidade_pessoas'],
        'motivo' => $agendamento['motivo']
    ];
}

$conn->close();
$month_name = $meses[(int)$month];
?>

<!doctype html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Agendamento de Salas</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .calendar-table { width: 100%; table-layout: fixed; }
        .calendar-table td { vertical-align: top; padding: 10px; border: 1px solid #ddd; min-height: 100px; position: relative; background-color: #f8f9fa; }
        .calendar-table th { text-align: center; vertical-align: middle; padding: 10px; border: 1px solid #ddd; }
        .event-list { margin: 0; padding: 0; list-style: none; }
        .event-list li { padding: 5px 0; border-bottom: 1px solid #ddd; font-size: 0.9rem; }
        .day { position: relative; }
        .day .events { margin-top: 10px; }
        .day strong { display: block; margin-bottom: 5px; }
        .day.empty { background-color: #e9ecef; }
    </style>
</head>
<body>
    <div class="container mt-4">
        <h1 class="mb-4">Calendário de <?php echo $month_name . " " . $year; ?></h1>
        <table class="calendar-table table table-bordered">
            <thead>
                <tr>
                    <th>Seg</th>
                    <th>Ter</th>
                    <th>Qua</th>
                    <th>Qui</th>
                    <th>Sex</th>
                    <th>Sab</th>
                    <th>Dom</th>
                </tr>
            </thead>
            <tbody>
                <?php 
                foreach (array_chunk($month_days, 7) as $week) {
                    echo "<tr>";
                    foreach ($week as $day) {
                        echo "<td class='". ($day == 0 ? 'empty' : '') ."'>";
                        if ($day != 0) {
                            echo "<div class='day'><strong>$day</strong>";
                            if (isset($agendamentos_por_dia[$day])) {
                                echo "<div class='events'><ul class='event-list'>";
                                foreach ($agendamentos_por_dia[$day] as $agendamento) {
                                    echo "<li><strong>Sala {$agendamento['sala']}</strong> Horário: {$agendamento['inicio']} - {$agendamento['fim']}<br>{$agendamento['pessoas']} pessoas - {$agendamento['motivo']}</li>";
                                }
                                echo "</ul></div>";
                            }
                            echo "</div>";
                        }
                        echo "</td>";
                    }
                    echo "</tr>";
                }
                ?>
            </tbody>
        </table>
        <a href="agendar.php" class="btn btn-primary mt-3">Agendar Reunião</a>
    </div>
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.2/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
