<?php
header('Access-Control-Allow-Origin: *');
$data = json_decode(file_get_contents('php://input'), true);
$userData = $_GET['data'];
$queryId = $_GET['query_id'];

$tokens = [
    "test" => "telegram-token-1",
    "prod" => "telegram-token-2"
];

$botToken = $tokens[$_GET['env']];

if (empty($botToken)) {
    echo "Unknown env " . $_GET['env'];
    exit(0);
}

$telegramApiUrl = "https://api.telegram.org/bot$botToken/answerWebAppQuery";

$lang = [
    'en' => 'Submitting data... ',
    'ru' => 'Отправляем... ',
    'es' => 'Enviando datos... ',
    'fr' => 'Soumission des données... ',
    'de' => 'Daten werden übermittelt... ',
];


$userData = str_replace('__timestamp__', time(), $userData);

$postFields = [
    'web_app_query_id' => $queryId,
    'result' => json_encode([
        'type' => 'article',
        'id' => uniqid(),
        'title' => 'Data Transfer',
        'input_message_content' => [
            'message_text' => $lang[$_GET['lang_code']] . '<tg-spoiler>' . $userData . '</tg-spoiler>',
            "parse_mode" => "HTML"
        ]
    ]),
];

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $telegramApiUrl);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_POSTFIELDS, $postFields);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($ch);
$httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

echo json_encode(['env' => $_GET['env'], 'status' => $httpcode, 'response' => $response, 'query_id' => $queryId, 'data' => $userData]);

