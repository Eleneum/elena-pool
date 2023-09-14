<?php
$jsonString = file_get_contents('pool.json');
$data = json_decode($jsonString, true);
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
                <li class="nav-item active">
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
				<li class="nav-item">
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
						<div style="text-align:center;" class="content">
							<a style="margin:4px;" target="_blank" class="btn btn-primary" href="https://eleneum.org">Website</a>
							<a style="margin:4px;" target="_blank" class="btn btn-primary" href="https://explorer.eleneum.org">ELENAScan</a>
							<a style="margin:4px;" target="_blank" class="btn btn-primary" href="https://metamask.io">Metamask wallet</a>
							<a style="margin:4px;" target="_blank" class="btn btn-primary" href="https://discord.gg/x7yDFThdAN">Discord</a>
						</div>
                            <!-- Notice link start --
                            <!-- Header, content, and CTAs start -->
                            <div class="container-fluid">
							  <div class="row">
								<div class="col-sm">
								<div class="card" style="text-align:center;">
								  <h4 class="card-title">
									Height
								  </h4>
								  <p>
									<a href="#" class="btn"><span id="nheight"></span></a>
								  </p>
								</div>
								</div>	
								
								<div class="col-sm">
									<div class="card" style="text-align:center;">
								  <h4 class="card-title">
									Difficulty
								  </h4>
								  <p>
									<a href="#" class="btn"><span id="ndiff"></span></a>
								  </p>
								</div>	
								</div>
								<div class="col-sm">
									<div class="card" style="text-align:center;">
								  <h4 class="card-title">
									Net Hashrate
								  </h4>
								  <p>
									<a href="#" class="btn"><span id="nhr"></span></a>
								  </p>
								</div>
								</div>
									<div class="col-sm">
										<div class="card" style="text-align:center;">
								  <h4 class="card-title">
									Last block
								  </h4>
								  <p>
									<a href="#" class="btn"><span id="nlastblock"></span> sec ago</a>
								  </p>
								</div>
									</div>
							  </div>
								<div class="row">
								<div class="col-sm">
								<div class="card" style="text-align:center;">
								  <h2 class="card-title">
									Miners
								  </h2>
								  <p>
									<a href="#" class="btn"><span id="pminers"></span> miners</a><br><br><a href="#" class="btn"><span id="pworkers"></span> workers</a>
									<br><br><a href="#" class="btn"><span id="psolo"></span> solo</a>
								  </p>
								</div>
								</div>	
								
								<div class="col-sm">
									<div class="card" style="text-align:center;">
								  <h2 class="card-title">
									Pool Hashrate
								  </h2>
								  <p>
									<a href="#" class="btn">POOL: <span id="phr"></span></a><br><br>
									<a href="#" class="btn">SOLO: <span id="psolohr"></span></a>
								  </p>
								</div>	
								</div>
								<div class="col-sm">
									<div class="card" style="text-align:center;">
								  <h2 class="card-title">
									Blocks Found
								  </h2>
								  <p>
									<a href="#" class="btn">POOL: <span id="pnumblocks"></span></a><br><br>
									<a href="#" class="btn">SOLO: <span id="pnumsoloblocks"></span></a>
								  </p>
								</div>
								</div>
									<div class="col-sm">
										<div class="card" style="text-align:center;">
								  <h2 class="card-title">
									Pool Fee
								  </h2>
								  <p>
									<a href="#" class="btn"><span id="pfee"></span></a>
								  </p>
								</div>
									</div>
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
    <!-- Particle JS -->
    	<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
	<script>
	function convertHashRate(hashRate) {
	  if (hashRate < 1000) {
		return hashRate + " H/s";
	  } else if (hashRate >= 1000 && hashRate <= 999999) {
		return (hashRate / 1000).toFixed(2) + " KH/s";
	  } else {
		return (hashRate / 1000000).toFixed(2) + " MH/s";
	  }
	}
    function updatePoolStats() {
      $.ajax({
        url: '/api/stats/',
        dataType: 'json',
        success: function(data) {
          $("#nheight").text(data['network']['height']);
		  $("#ndiff").text(data['network']['difficulty']);
		  $("#nhr").text(convertHashRate(data['network']['difficulty']/20));
		  $("#nlastblock").text(Math.floor(Date.now() / 1000)-data['network']['lastblock']['timestamp']);
		  $("#pminers").text(data['pool']['stats']['miners']);
		  $("#pworkers").text(data['pool']['stats']['workers']);
		  $("#psolo").text(data['pool']['stats']['workersSolo']);
		  $("#phr").text(convertHashRate(data['pool']['stats']['hashrate']));
		  $("#psolohr").text(convertHashRate(data['pool']['stats']['hashrateSolo']));
		  $("#pnumblocks").text(data['pool']['stats']['totalBlocks']);
		  $("#pnumsoloblocks").text(data['pool']['stats']['totalBlocksSolo']);
		  $("#pfee").text(data['config']['fee'] + "%");
        }
      });
    }
    $(document).ready(function() {
      updatePoolStats();
      setInterval(updatePoolStats, 20000);
    });
  </script>
</body>
</html>
