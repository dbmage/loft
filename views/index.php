<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<?php
$MYROOTDIR = '/var/www';
include ("$MYROOTDIR/config.php");
include ("$MYROOTDIR/preference.php");
include ("$MYROOTDIR/result.php" );

$command = "sudo /scripts/./depth.py";
$width="200";
$test = exec($command,$output);
$left = $output[0];
$right = $output[1];
$lock = shell_exec('cat /sys/class/gpio/gpio2/value');
$lights = shell_exec('cat /sys/class/gpio/gpio3/value');
$valve = shell_exec('cat /sys/class/gpio/gpio4/value');
$pumps = shell_exec('cat /sys/class/gpio/gpio17/value');

$time=shell_exec('date +%T');
//Unit section:  inialize variable depending if the unit is cm or in
if ($preferunit=="cm") {
   $niveaudo=(($deep-$left)).' '.$preferunit.' ';
   $niveaudo2=(($deep-$right)).' '.$preferunit.' ';
   $litres=((29 * 29 * 3.1415926535897932384626433832795 * $niveaudo / 1000));
   $litres=number_format($litres, 2, '.', '');
   $litres2=((29 * 29 * 3.1415926535897932384626433832795 * $niveaudo2 / 1000));
   $litres2=number_format($litres2, 2, '.', '');
   $totallitres=(( $litres + $litres2 ));
   $freespace= $left.' '.$preferunit.' free ';
   $freespace2= $right.' '.$preferunit.' free ';
   $sizeofreeblock=$left*5;  //this will change the size of the table
   $sizeofreeblock2=$right*5;
   $sizeofusedblock=($deep-$left)*5; //this will change the size of the table
   $sizeofusedblock2=($deep-$right)*5;
} else if ($preferunit=="in") {
   $niveaudo=(($deep-$mesurepouce)).' '.$preferunit.' ';
   $freespace= $mesurepouce.' '.$preferunit.' free ';
   $sizeofreeblock=$mesurepouce*13;  //size is in pixel for previewing only, this will change the size of the table
   $sizeofusedblock=($deep-$mesurepouce)*13; //size is in pixel for previewing only, this will change the size of the table
}
// End of Unit section

//Color led section: change the image path depending of the color of the led
if ($niveaudo>$highred)	{
   $toppicture="topred.gif";
} else if ($niveaudo>$highamber) {
   $toppicture="topamber.gif";
} else if ($niveaudo<$lowamber) {
   $toppicture="topamber.gif";
} else if ($niveaudo<$lowred) {
   $toppicture="topred.gif";
} else {
   $toppicture="topgreen.gif";
}

$lightpic = ($lights == 0) ? "greenlight.png" : "redlight.png"; // if $lights == "0" then greenlight else (:) redlight
$lockpic = ( $lock == 1 ) ? "greenlight.png" : "redlight.png";
$valvepic = ( $valve == 0 ) ? "greenlight.png" : "redlight.png";
$pumpspic = ( $pumps == 1 ) ? "greenlight.png" : "redlight.png";
$linkip = (empty($_SERVER['HTTP_X_FORWARDED_FOR'])) ? "http://192.168.0.2/mon" : "http://dbmage.co.uk/mon";
?>
<head>
   <meta name="viewport" content="width=750, initial-scale=0.8">
   <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
   <title>Water Bucket Levels</title>
   <link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>
<h4 class="navh">Menu</h4>
<form class="button1" method="get" action="<?php echo $linkip; ?>"><button type="submit">Server</button></form>
<form class="button2" method="get" action="<?php echo $linkip; ?>/satan.php"><button type="submit">Switch</button></form>
<form class="button3" method="get" action="<?php echo $linkip; ?>/water.php"><button type="submit">Water</button></form>
<h4 class="conh">Control</h4>
<form class="pump" method="post" action="control.php"><button type="submit" name="pump">Pump override</button></form>
<form class="lock" method="post" action="control.php"><button type="submit" name="door">Door override</button></form>
<form class="valve" method="post" action="control.php"><button type="submit" name="valve">Valve on/off</button></form>


<table border="0" border cellspacing="0" cellpadding="10">
   <tr>
      <td colspan="2">Lock Power: <img src="<?php echo $lockpic; ?>" width="30px" alt="Lock status LED"></td>
      <td colspan="2">Lights Power: <img src="<?php echo $lightpic; ?>" width="30px" alt="Light status LED"></td>
   </tr>
   <tr>
      <td colspan="2">Valve Power: <img src="<?php echo $valvepic; ?>" width="30px" alt="Valve status LED"></td>
      <td colspan="2">Pumps Power: <img src="<?php echo $pumpspic; ?>" width="30px" alt="Pump status LED"></td>
   </tr>
   <tr>
      <th>Tank 1</th>
      <th></th>
      <th>Tank 2</th>
   </tr>
   <tr>
      <td width="<?php echo $width; ?>" height="75"  style="background: url('<?php echo $toppicture ;?>') top left no-repeat;"></td>
      <td></td>
      <td width="<?php echo $width; ?>" height="75"  style="background: url('<?php echo $toppicture ;?>') top left no-repeat;"></td>
   </tr>
   <tr>
      <td class="free" width="<?php echo $width; ?>" height="<?php echo $sizeofreeblock ;?>" align="right" ><?php echo $freespace ?></td>
      <td></td>
      <td class="free" width="<?php echo $width; ?>" height="<?php echo $sizeofreeblock2 ;?>" align="right" ><?php echo $freespace2 ?></td>
   </tr>
   <tr>
      <td class="water" width="<?php echo $width; ?>" height="<?php echo $sizeofusedblock ;?>" align="right" ><?php echo $niveaudo; echo ""; echo "<br>$litres litres";?> </td>
      <td></td>
      <td class="water" width="<?php echo $width; ?>" height="<?php echo $sizeofusedblock2 ;?>" align="right"><?php echo $niveaudo2; echo "<br>$litres2 litres"; ?> </td>
   </tr>
   <tr>
      <td width="<?php echo $width; ?>" height="4" align="center" > Last update: <?php echo $time."\n";  echo $heurescan; ?></td>
      <td></td>
      <td width="<?php echo $width; ?>" height="4" align="center" > Last update: <?php echo $time."\n";  echo $heurescan2; ?></td>
   </tr>
   <tr>
      <td colspan="3" align="center">Total: <?php echo $totallitres; ?> litres</td>
   </tr>
</table>
<table>
<p style="position: fixed; bottom: 10px; right: 110px">
<a href="http://validator.w3.org/check?uri=referer">
<img src="/img/vhtml" alt="Valid HTML 4.01 Transitional">
</a>
</p>
<p style="position: fixed; bottom: 10px; right: 10px;">
<a href="http://jigsaw.w3.org/css-validator/check/referer">
<img src="/img/vcss" alt="Valid CSS!"></a>
</body>
</html>
