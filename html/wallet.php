<?php
$jsonString = file_get_contents('pool.json');
$data = json_decode($jsonString, true);
if(isset($_GET["address"]))
{
	$address = strtolower($_GET["address"]);
	$manager = new MongoDB\Driver\Manager("mongodb://localhost:27017");
	$filter = ['address' => $address];
	$query = new MongoDB\Driver\Query($filter, [
		'projection' => [
			'address' => 1,
			'status' => 1,
			'valueSum' => [
				'$sum' => '$value'
			]
		]
	]);
	$namespace = 'eleneum.poolpayments';
	$results = $manager->executeQuery($namespace, $query)->toArray();
	$unpaid = 0;
	$paid = 0;
	foreach ($results as $result) {
		if($result->status == -1) $unpaid += $result->valueSum;
		if($result->status == 1) $paid += $result->valueSum;
	}
	$timestamp = time() - 600;
	$query = new MongoDB\Driver\Query(['address' => $address]);
	$r = $manager->executeQuery("eleneum.poolworkers", $query)->toArray();
	$wids = array();
	foreach($r as $document)
	{
		$wids[$document->extranonce] = $document->workerid;
	}
	$query = new MongoDB\Driver\Query(['address' => $address, 'ts' => ['$gt' => $timestamp]]);
	$r = $manager->executeQuery("eleneum.pool", $query)->toArray();
	$sd = 0;
	$workers = array();
	foreach ($r as $document) {
		$sd += $document->target;
		if(!isset($workers[$wids[substr($document->nonce, 0, 4)]]))
			$workers[$wids[substr($document->nonce, 0, 4)]] = $document->target;
		else
			$workers[$wids[substr($document->nonce, 0, 4)]] += $document->target;
	}
	$query = new MongoDB\Driver\Query(['address' => $address]);
	$solomined = $manager->executeQuery("eleneum.poolsoloblocks", $query)->toArray();
}
?>
<!DOCTYPE html>
<html lang="en">

<head>
    <!-- Meta tags -->
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
    <meta content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0' name='viewport' />
    <meta name="viewport" content="width=device-width" />
    <!-- Chrome, Firefox OS and Opera mobile address bar theming -->
    <meta name="theme-color" content="#000000">
    <!-- Windows Phone mobile address bar theming -->
    <meta name="msapplication-navbutton-color" content="#000000">
    <!-- iOS Safari mobile address bar theming -->
    <meta name="apple-mobile-web-app-status-bar-style" content="#000000">
    <!-- SEO -->
    <meta name="description" content="Eleneum Mining Pool">
    <meta name="author" content="Eleneum">
    <meta name="keywords" content="eleneum, mining, pool, bitcoin, ethereum, metamask, evm, smart contracts, moner, randomx, xmrig">
	<!-- Open graph -->
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://<?php echo $data['url']; ?>/">
    <meta property="og:title" content="Eleneum Mining Pool">
    <meta property="og:description" content="Eleneum Mining Pool">
    <meta property="og:image" content="https://<?php echo $data['url']; ?>/img/logo.png">
    <!-- Fav and Title -->
    <link rel="icon" href="/img/logo.png">
    <title>Eleneum Mining Pool</title>
    <!-- Halfmoon CSS -->
    <link href="https://cdn.jsdelivr.net/npm/halfmoon@1.1.1/css/halfmoon.min.css" rel="stylesheet" />
    <!-- Font awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css" integrity="sha256-eZrrJcwDc/3uDhsdt61sL2oOBY362qM3lon1gyExkL0=" crossorigin="anonymous" />
    <!-- Roboto font (Used when Apple system fonts are not available) -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <!-- Landing styles -->
    <link href="/static/site/css/landing-styles-3.css" rel="stylesheet">
</head>
<body class="dark-mode with-custom-webkit-scrollbars with-custom-css-scrollbars">
    <!-- Page wrapper start -->
	<div class="page-wrapper with-navbar with-navbar-fixed-bottom" id="particles-js">

		<!-- Navbar start -->
        <nav class="navbar">
            <a href="/" class="navbar-brand">
				<img src="/img/logo.png">
                ELENAPool 
                <span style="margin-left:8px;" class="badge font-size-12 text-monospace px-5 px-sm-10">
                    v0.0.3
                </span>
            </a>
            <ul class="navbar-nav hidden-sm-and-down">
                <li class="nav-item">
                    <a href="/" class="nav-link">Home</a>
                </li>
                <li class="nav-item">
                    <a href="/gettingstarted.php" class="nav-link">Getting started</a>
                </li>
                <li class="nav-item">
                    <a href="/blocks.php" class="nav-link">Blocks</a>
                </li>
				<li class="nav-item">
                    <a href="/payments.php" class="nav-link">Payments</a>
                </li>
				<li class="nav-item active">
                    <a href="/mywallet.php" class="nav-link">My wallet</a>
                </li>
				<li class="nav-item">
                    <a href="/miners.php" class="nav-link">Miners</a>
                </li>
            </ul>
            <div class="navbar-content ml-auto">
                <div class="dropdown with-arrow hidden-md-and-up">
                    <button class="btn navbar-menu-btn" data-toggle="dropdown" type="button" id="navbar-dropdown-toggle-btn" aria-haspopup="true" aria-expanded="false">
                        <span class="text">Menu</span>
                        <i class="fa fa-angle-down" aria-hidden="true"></i>
                    </button>
                    <div class="dropdown-menu dropdown-menu-right" aria-labelledby="navbar-dropdown-toggle-btn">
                        <a href="/" class="dropdown-item">Home</a>
                        <a href="/gettingstarted.php" class="dropdown-item">Getting Started</a>
                        <a href="/blocks.php" class="dropdown-item">Blocks</a>
						<a href="/payments.php" class="dropdown-item">Payments</a>
						<a href="/mywallet.php" class="dropdown-item">My Wallet</a>
						<a href="/miners.php" class="dropdown-item">Miners</a>
                        <div class="dropdown-divider"></div>
                    </div>
                </div>
            </div>
        </nav>
        <!-- Navbar end -->
        <!-- Content wrapper start -->
		<div class="content-wrapper">
			<div class="container-lg">
				<div class="row">

                    <!-- Hero start -->
					<div class="col-lg-12">
                        <div class="content">
                            <!-- Notice link start --
                            <!-- Header, content, and CTAs start -->
                            <div class="container-fluid">
							  <div class="row">
							  <!-- Small input -->
							  <form method="get" style="width:100%;">
							<input type="text" name="address" class="form-control form-control-sm" placeholder="Insert your metamask address and press enter">
							</form>
							<!-- No outer padding -->
							<h5><?php echo $address; ?></h5>
							<table class="table table-no-outer-padding">
							  <thead>
								<tr>
								  <th>Unpaid</th>
								  <th>Paid</th>
								  <th>Total</th>
								  <th>SOLO Blocks</th>
								</tr>
							  </thead>
							  <tbody>
								<tr>
								  <td><?php echo $unpaid/1000000000000000000; ?> ELENA</td>
								  <td><?php echo $paid/1000000000000000000; ?> ELENA</td>
								  <td><?php echo ($unpaid+$paid)/1000000000000000000; ?> ELENA</td>
								  <td><?php echo count($solomined); ?></td>
								</tr>
							  </tbody>
							</table>
							  </div>
								<div class="row">
							<h5>Mining info</h5>
							<table class="table table-no-outer-padding">
							  <thead>
								<tr>
								  <th>Worker</th>
								  <th>Hashrate</th>
								</tr>
							  </thead>
							  <tbody>
							<?php foreach($workers as $key => $value): ?>
								<tr>
								  <td><?php echo $key; ?></td>
								  <td><?php echo intval($value/600); ?> H/s</td>
								</tr>
							<?php endforeach; ?>
								<tr>
								  <td><b>Total hashrate</b></td>
								  <td><b><?php echo intval($sd/600); ?> H/s</b></td>
								</tr>
							  </tbody>
							</table>
							  </div>
							</div>
                            <!-- Header, content, and CTAs end -->
                        </div>
                    </div>
                    <!-- Hero end -->
				</div>
			</div>
		</div>
        <!-- Content wrapper end -->
        <!-- Navbar fixed bottom start -->
        <nav class="navbar navbar-fixed-bottom">
            <ul class="navbar-nav ml-auto">
                <li class="nav-item">
                    <a href="https://github.com/Eleneum/elena-pool" target="_blank" rel="noopener" class="nav-link pr-5">
                        <span class="d-none d-sm-inline">
                            Made with <i class="fa fa-heart" aria-hidden="true"></i> by Alberto
                        </span>
                        <span class="d-sm-none">
                            Made with <i class="fa fa-heart" aria-hidden="true"></i> by Alberto
                        </span>
                    </a>
                </li>
            </ul>
        </nav>
        <!-- Navbar fixed bottom end -->
	</div>
    <!-- Page wrapper end -->
    <!-- Halfmoon JS -->
    <script src="https://cdn.jsdelivr.net/npm/halfmoon@1.1.1/js/halfmoon.min.js"></script>
</body>
</html>