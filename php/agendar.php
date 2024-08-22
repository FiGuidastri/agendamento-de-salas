<?php
include 'db.php';

$conn = get_db_connection();
$result = $conn->query("SELECT id, nome FROM tab_salas");
$salas = $result->fetch_all(MYSQLI_ASSOC);
$conn->close();
?>

<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agendamento de Salas</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center mb-4">Agendar Sala</h1>
        <div class="row justify-content-center">
            <div class="col-md-6">
                <form action="agendar_action.php" method="post" class="shadow p-4 rounded bg-light">
                    <div class="mb-3">
                        <label for="sala" class="form-label">Sala:</label>
                        <select name="sala" id="sala" class="form-select">
                            <?php foreach ($salas as $sala): ?>
                                <option value="<?php echo $sala['id']; ?>"><?php echo $sala['nome']; ?></option>
                            <?php endforeach; ?>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="data" class="form-label">Data:</label>
                        <input type="date" name="data" id="data" class="form-control">
                    </div>
                    <div class="mb-3">
                        <label for="inicio" class="form-label">Horário de Início:</label>
                        <input type="time" name="inicio" id="inicio" class="form-control">
                    </div>
                    <div class="mb-3">
                        <label for="fim" class="form-label">Horário de Fim:</label>
                        <input type="time" name="fim" id="fim" class="form-control">
                    </div>
                    <div class="mb-3">
                        <label for="quantidade_pessoas" class="form-label">Quantidade de Pessoas:</label>
                        <input type="number" name="quantidade_pessoas" id="quantidade_pessoas" class="form-control">
                    </div>
                    <div class="mb-3">
                        <label for="motivo" class="form-label">Motivo da Reunião:</label>
                        <textarea name="motivo" id="motivo" class="form-control" rows="3"></textarea>
                    </div>
                    <div class="text-center">
                        <button type="submit" class="btn btn-primary">Agendar</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
