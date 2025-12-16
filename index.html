<?php
// tg.php — Telegram Login handler

$BOT_TOKEN = "ВСТАВЬ_ТОКЕН_ТВОЕГО_БОТА";

// читаем JSON
$data = json_decode(file_get_contents("php://input"), true);
if (!$data) {
  http_response_code(400);
  exit("No data");
}

// --- Проверка подписи Telegram ---
$check_hash = $data["hash"];
unset($data["hash"]);

ksort($data);
$check_string = "";
foreach ($data as $k => $v) {
  $check_string .= "$k=$v\n";
}
$check_string = rtrim($check_string, "\n");

$secret_key = hash("sha256", $BOT_TOKEN, true);
$hash = hash_hmac("sha256", $check_string, $secret_key);

if (!hash_equals($hash, $check_hash)) {
  http_response_code(403);
  exit("Invalid Telegram auth");
}

// --- База SQLite ---
$db = new PDO("sqlite:users.db");
$db->exec("
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  username TEXT,
  first_name TEXT,
  photo_url TEXT
)
");

// --- Сохраняем пользователя ---
$stmt = $db->prepare("
INSERT OR IGNORE INTO users (id, username, first_name, photo_url)
VALUES (:id, :username, :first_name, :photo_url)
");

$stmt->execute([
  ":id" => $data["id"],
  ":username" => $data["username"] ?? null,
  ":first_name" => $data["first_name"] ?? null,
  ":photo_url" => $data["photo_url"] ?? null
]);

echo json_encode(["ok" => true]);
