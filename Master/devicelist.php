<!DOCTYPE html>
<html>
<head>
<style>
body
{
background:#d0e4fe url('img/devicelist.jpg') top;
margin-right:200px;
}
#devicelist
{
position:absolute;
left:500px;
top:50px;
}
</style>
</head>

<body>
<h1 align="center"> Device List </h1>
<div id="devicelist">
<?php
require_once('mysqlconf.php');
require_once('devicesql.php');

$querySql="select * from DeviceInfo";
$db=new Device($db_host, $db_user, $db_pwd, $db_name, $db_charSet, $db_conn);
$res=$db->Query($querySql);
$resNum=$db->GetRowsNum($res);

echo "The Number of Devices: " . $resNum . "<br/>";
echo "<table width='400' border='1'>
<caption> Devices Net Information as follows: </caption>
<tr>
	<th>ID</th>
	<th>Status</th>
	<th>NetType</th>
	<th>IP</th>
	<th>MAC</th>
	<th>PeerID</th>
	<th>FreeMem</th>
	<th>FreeDisk</th>
	<th>OSType</th>
</tr>";

while($row=mysql_fetch_array($res))
{
	echo "<tr>";
	echo "<td align='center'>" . $row[ID] . "</td>";
	
	switch($row[STATUS])
	{
	case "Idle":
		echo "<td bgcolor=#FF9933 align='center'>" . $row[STATUS] . "</td>";
	break;
	case "Disposition_OK":
	case "Execution_OK":
		echo "<td bgcolor=#00FF00 align='center'>" . $row[STATUS] . "</td>";
	break;
	case "Disposition_Err":
	case "Execution_Err":
		echo "<td bgcolor=#FF0000 align='center'>" . $row[STATUS] . "</td>";
	break;
	default:
		echo "<td bgcolor=#C0C0C0 align='center'>" . $row[STATUS] . "</td>";
	break;
	}

	echo "<td align='center'>" . $row[NETTYPE] . "</td>";
	echo "<td align='center'>" . $row[IP] . "</td>";
	echo "<td align='center'>" . $row[MAC] . "</td>";
	echo "<td align='center'>" . $row[PEERID] . "</td>";
	echo "<td align='center'>" . $row[FREEMEM] . "</td>";
	echo "<td align='center'>" . $row[FREEDISK] . "</td>";
	echo "<td align='center'>" . $row[OSTYPE] . "</td>";
	echo "</tr>";
}

echo "</table>";
