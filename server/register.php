<?php
	$url = 'http://localhost:5000/register';
	$data = array('username' => $_GET['username'], 'password' => $_GET['password'], 'name' => $_GET['name'], 'account' => $_GET['account']);

// use key 'http' even if you send the request to https://...
$options = array(
    'http' => array(
        'header'  => "Content-type: application/x-www-form-urlencoded\r\n",
        'method'  => 'POST',
        'content' => http_build_query($data),
    ),
);
$context  = stream_context_create($options);
$result = file_get_contents($url, false, $context);
$callback = $_GET['mycallback'];
echo $callback . '(' . json_encode($result) . ')';
?>