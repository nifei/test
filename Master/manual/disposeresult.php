<html>
<head>
<style>
body
{
background:#d0e4fe url('../img/devicelist.jpg') top;
margin-right:200px;
}
.tips
{
color:red;
align:center;
}
#devicelist
{
position:absolute;
left:500px;
top:90px;
}
</style>
</head>
<body>
<h2 align="center"> Manual Test </h2>
<h3 align="center"> Display the result of dispose file </h3>
<div id="devicelist">
<?php
require_once('../mysqlconf.php');
require_once('../devicesql.php');

$db=new Device($db_host, $db_user, $db_pwd, $db_name, $db_charSet, $db_conn);
if($_POST['IsEchoDisposeRes'] == "yes")
{
	$querySql="select * from DeviceDispose";
	$res=$db->Query($querySql);
	$totalNum=$db->GetRowsNum($res);
	
	$querySql="select DeviceInfo.ACTIONSTATUS, DeviceInfo.NETTYPE, DeviceInfo.IP, DeviceInfo.MAC, DeviceInfo.PEERID, DeviceInfo.FREEMEM, DeviceInfo.FREEDISK, DeviceInfo.OSTYPE, DeviceDispose.FILE from DeviceDispose, DeviceInfo where DeviceDispose.MAC=DeviceInfo.MAC and DeviceInfo.ACTIONSTATUS in ('Disposition_OK', 'Disposition_Err')";
	$res=$db->Query($querySql);
	$actualNum=$db->GetRowsNum($res);
	echo "totalNum=" . $totalNum;
	echo "actualNum=" . $actualNum;
	if($totalNum!=$actualNum)
	{
		sleep(3);
		echo "<p> Master is disposing files to devices, wait for a moment again... </p>";
		echo "<form enctype='multipart/form-data' action='/manual/disposeresult.php' method='post'>";
		echo "<label class='tips'> Display the result of dispose file </label>";
		echo "<br/>";
		echo "<input type='radio' name='IsEchoDisposeRes' value='yes' checked> Display " . "<br/>";
		echo "<input type='radio' name='IsEchoDisposeRes' value='no'> NoDisplay" . "<br/>" . "<br/>";
		echo "<input type='submit' value='Submit' />";
		echo "<input type='reset' value='Reset' />" . "<br/>";
		echo "</form>";
		echo "</div>";
		echo "</form>";
		echo "</body>";
		echo "</html>";
		return;		
	}

	echo "<form enctype='multipart/form-data' action='/manual/manualexecute.php' method='post'>";
	echo "<table width='400' border='1'>
	<caption> The result of dispose files </caption>
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
		<th>File</th>
	</tr>";
	$i=0;
	while($row=mysql_fetch_array($res))
	{
		echo "<tr>";
		echo "<td align='center'>" . ++$i . "</td>";
		switch($row[ACTIONSTATUS])
		{
		case "Disposition_OK":
			echo "<td bgcolor=#00FF00 align='center'>" . $row[ACTIONSTATUS] . "</td>";
		break;
		case "Disposition_Err":
			echo "<td bgcolor=#FF0000 align='center'>" . $row[ACTIONSTATUS] . "</td>";
		break;
		default:
			echo "<td bgcolor=#C0C0C0 align='center'>" . $row[ACTIONSTATUS] . "</td>";
		break;
		}

		echo "<td align='center'>" . $row[NETTYPE] . "</td>";
		echo "<td align='center'>" . $row[IP] . "</td>";
		echo "<td align='center'>" . $row[MAC] . "</td>";
		echo "<td align='center'>" . $row[PEERID] . "</td>";
		echo "<td align='center'>" . $row[FREEMEM] . "</td>";
		echo "<td align='center'>" . $row[FREEDISK] . "</td>";
		echo "<td align='center'>" . $row[OSTYPE] . "</td>";
		echo "<td align='center'>" . $row[FILE] . "</td>";
		echo "</tr>";
	}
	echo "</table>";
	echo "<br/>";
	echo "<label class='tips'> Execute files disposed on devices </label>";
	echo "<br/>";
	echo "<input type='radio' name='IsExecute' value='yes' checked> Execute" . "<br/>";
	echo "<input type='radio' name='IsExecute' value='no'> NoExecute" . "<br/>" . "<br/>";
	echo "<input type='submit' value='Submit' />";
	echo "<input type='reset' value='Reset' />" . "<br/>";
	echo "</form>";
}
else
{
	echo "<p> Not sure dispose file successfully or not. </p>";
	echo "<form enctype='multipart/form-data' action='/manual/manualexecute.php' method='post'>";
	echo "<br/>";
	echo "<label class='tips'> Execute files disposed on devices </label>";
	echo "<br/>";
	echo "<input type='radio' name='IsExecute' value='yes' checked> Execute" . "<br/>";
	echo "<input type='radio' name='IsExecute' value='no'> NoExecute" . "<br/>" . "<br/>";
	echo "<input type='submit' value='Submit' />";
	echo "<input type='reset' value='Reset' />" . "<br/>";
	echo "</form>";
}
?>
</div>
</form>
</body>
</html>
