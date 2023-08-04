<?php

if (($body_stream = file_get_contents("php://input")) === FALSE) {
    echo "Bad Request";
}
error_log('Received data: ' . file_get_contents("php://input"));
// Send the data to the local server
$url = 'http://127.0.0.1:5000/save';
$ch = curl_init($url);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_POSTFIELDS, $body_stream);
curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($ch);

if ($response === FALSE) {
    echo "Failed to send data to the server";
}

curl_close($ch);

echo "{\"error\":0}";

?>

