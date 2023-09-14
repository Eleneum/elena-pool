<?php
$jsonString = file_get_contents('../../pool.json');
$data = json_decode($jsonString, true);
$manager = new MongoDB\Driver\Manager("mongodb://localhost:27017");
$query = new MongoDB\Driver\Query([], [
	'sort' => ['ts' => -1],
	'limit' => 15
]);
$r = $manager->executeQuery("eleneum.poolblocks", $query)->toArray();
$query = new MongoDB\Driver\Query([], [
	'sort' => ['ts' => -1],
	'limit' => 15
]);
$sr = $manager->executeQuery("eleneum.poolsoloblocks", $query)->toArray();
foreach ($r as &$item) {
    $item->solo = 0;
}
foreach ($sr as &$item) {
    $item->solo = 1;
}
$blocks = array_merge($r, $sr);
function compareByTsDesc($a, $b) {
    return $b->ts - $a->ts;
}
usort($blocks, 'compareByTsDesc');
$sentpayments = array();
$query = new MongoDB\Driver\Query([], [
	'sort' => ['height' => -1],
	'limit' => 1
]);
$r = $manager->executeQuery("eleneum.blocks", $query)->toArray();
$h = $r[0]->height;
$hh = $r[0]->hash;
$d = $r[0]->difficulty;
$t = $r[0]->timestamp;
$timestamp = time() - 300;
$query = new MongoDB\Driver\Query(['ts' => ['$gt' => $timestamp]]);
$r = $manager->executeQuery("eleneum.pool", $query)->toArray();
$sd = 0;
$solosd = 0;
$miners = array();
$workers = array();
$solo = array();
foreach ($r as $document) {
	if(intval($document->solo) != 1)
	{
		$sd += $document->target;
		array_push($miners, $document->address);
		array_push($workers, $document->extranonce);
	}
	else
	{
		$solosd += $document->target;
		array_push($miners, $document->address);
		array_push($solo, $document->extranonce);
	}
}
$miners = array_unique($miners);
$workers = array_unique($workers);
$solo = array_unique($solo);
$filter = [];
$options = [
    'projection' => ['_id' => 1],
    'sort' => [],
];
$query = new MongoDB\Driver\Query($filter, $options);
$cursor = $manager->executeQuery("eleneum.poolblocks", $query);
$numblocks = iterator_count($cursor);
$filter = [];
$options = [
    'projection' => ['_id' => 1],
    'sort' => [],
];
$query = new MongoDB\Driver\Query($filter, $options);
$cursor = $manager->executeQuery("eleneum.poolsoloblocks", $query);
$solonumblocks = iterator_count($cursor);
header('Content-Type: application/json');
$lastblock = 0;
$ret = array();
$ret["config"] = array();
$ret["health"] = array();
$ret["pool"] = array();
$ret["charts"] = array();
$ret["network"] = array();

	$ret["config"]["poolHost"] = $data['url'];
	$ret["config"]["ports"] = array("port" => $data['port'], "difficulty" => $data['startdiff'], "desc" => "");
	$ret["config"]["cnAlgorithm"] = "randomx";
	$ret["config"]["cnVariant"] = 0;
	$ret["config"]["cnBlobType"] = 0;
	$ret["config"]["hashrateWindow"] = 300;
	$ret["config"]["fee"] = $data['fee'];
	$ret["config"]["soloFee"] = $data['fee'];
	$ret["config"]["networkFee"] = 0;
	$ret["config"]["coin"] = "ELENA";
	$ret["config"]["coinUnits"] = 1000000000000000000;
	$ret["config"]["coinDecimalPlaces"] = 18;
	$ret["config"]["coinDifficultyTarget"] = 20;
	$ret["config"]["symbol"] = "ELENA";
	$ret["config"]["depth"] = 60;
	$ret["config"]["version"] = "v0.0.2";
	$ret["config"]["paymentsInterval"] = 300;
	$ret["config"]["minPaymentThreshold"] = 100000000000000000;
	$ret["config"]["maxPaymentThreshold"] = 10000000000000000000000;
	$ret["config"]["transferFee"] = 0;
	$ret["config"]["denominationUnit"] = 1000000000000000000;
	$ret["config"]["blocksChartEnabled"] = false;
	
	$ret["health"] = array("ELENA" => array("daemon" => "OK", "wallet" => "OK"));
	$ret["pool"]["stats"] = array(); 
	$ret["pool"]["stats"]["blocks"] = array();
	foreach ($blocks as $document)
	{
		if($lastblock == 0) $lastblock = intval($document->ts);
		array_push($ret["pool"]["stats"]["blocks"], array("prop:".$document->hash.":".intval($document->ts).":".$document->reward.":0:0:0", strval($document->height)));
	}
	$ret["pool"]["stats"]["totalBlocks"] = $numblocks;
	$ret["pool"]["stats"]["totalBlocksSolo"] = $solonumblocks;
	$ret["pool"]["stats"]["totalDiff"] = 0;
	$ret["pool"]["stats"]["totalDiffSolo"] = 0;
	$ret["pool"]["stats"]["totalShares"] = 0;
	$ret["pool"]["stats"]["totalSharesSolo"] = 0;
	$ret["pool"]["stats"]["miners"] = count($miners);
	$ret["pool"]["stats"]["minersSolo"] = 0;
	$ret["pool"]["stats"]["workers"] = round(count($workers), 0);
	$ret["pool"]["stats"]["workersSolo"] = round(count($solo),0);
	$ret["pool"]["stats"]["hashrate"] = round($sd/300,0);
	$ret["pool"]["stats"]["hashrateSolo"] = round($solosd/300,0);
	$ret["pool"]["stats"]["roundScore"] = 0;
	$ret["pool"]["stats"]["roundHashes"] = 0;
	$ret["pool"]["stats"]["lastBlockFoundsolo"] = "0";
	$ret["pool"]["stats"]["lastBlockFoundprop"] = strval($lastblock);
	$ret["pool"]["stats"]["lastBlockFound"] = strval($lastblock);
	$ret["pool"]["stats"]["charts"] = array();
	$ret["network"] = array(); 
	$ret["network"]["difficulty"] = $d;
	$ret["network"]["height"] = $h;
	$ret["network"]["lastblock"] = array();
	$ret["network"]["lastblock"]["difficulty"] = $d;
	$ret["network"]["lastblock"]["height"] = $h;
	$ret["network"]["lastblock"]["timestamp"] = $t;
	$ret["network"]["lastblock"]["reward"] = 0;
	$ret["network"]["lastblock"]["hash"] = $hh;
	$ret["network"]["miner"] = array();

	echo json_encode($ret);
?>