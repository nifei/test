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
<h3 align="center"> ReExecute File </h3>
<div id="devicelist">
<?php
require_once('../mysqlconf.php');
require_once('../devicesql.php');

$db=new Device($db_host, $db_user, $db_pwd, $db_name, $db_charSet, $db_conn);
//$tempTableSql="CREATE TABLE IF NOT EXISTS DeviceExecute(ID int(10) unsigned NOT NULL AUTO_INCREMENT, MAC char(30) NOT NULL, PEERID char(30) NOT NULL, FILE char(30) NOT NULL, PRIMARY KEY(ID))";
//$res=$db->Query($tempTableSql);

foreach($_POST['DevicesChecked'] as $var)
{
	$querySql="select DeviceInfo.MAC, DeviceInfo.PEERID, DeviceDispose.FILE from DeviceInfo, DeviceDispose where DeviceDispose.ID='$var' and DeviceInfo.MAC=DeviceDispose.MAC";
	$res=$db->Query($querySql);
	/*
	while($row=mysql_fetch_array($res))
	{
		$insertSql="INSERT INTO  DeviceAction(ID, ACTION, MAC, FILE) VALUES('', 'EXECUTE', '$row[MAC]', '$row[FILE]')";
		$res=$db->Query($insertSql);
		$insertSql="INSERT INTO DeviceExecute VALUES('', '$row[MAC]', '$row[PEERID]', '$row[FILE]')";
		$res=$db->Query($insertSql);
	}
	*/
	$row=mysql_fetch_array($res);
	$insertSql="INSERT INTO  DeviceAction(ID, ACTION, MAC, FILE) VALUES('', 'EXECUTE', '$row[MAC]', '$row[FILE]')";
	$res=$db->Query($insertSql);
	$insertSql="INSERT INTO DeviceExecute VALUES('', '$row[MAC]', '$row[PEERID]', '$row[FILE]')";
	$res=$db->Query($insertSql);
}

if($_POST['IsReExecute'] == "yes")
{
	//foreach($_POST['DevicesChecked'] as $var)
	//	echo $var . "<br/>";
	echo "<form enctype='multipart/form-data' action='/manual/remanualexecute.php' method='post'>";
	$querySql="select DeviceDispose.ID, DeviceInfo.ACTIONSTATUS, DeviceInfo.NETTYPE, DeviceInfo.IP, DeviceInfo.MAC, DeviceInfo.PEERID, DeviceInfo.FREEMEM, DeviceInfo.FREEDISK, DeviceInfo.OSTYPE, DeviceDispose.FILE from DeviceInfo, DeviceDispose where DeviceInfo.MAC=DeviceDispose.MAC";
	$res=$db->Query($querySql);
	echo "<table width='400' border='1'>
	<caption> Ctrl device to execute file continue </caption>
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
		<th>Checked</th>
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
		echo "<td align='right'> <input type='checkbox' name='DevicesChecked[]' value='$row[ID]'>" . "</td>";
		echo "</tr>";
	}

	echo "</table>";
	echo "<br/>";
	echo "<label class='tips'> Continue to execute file </label>";
	echo "<br/>";
	echo "<input type='radio' name='IsExecute' value='yes' checked> ReExecute" . "<br/>";
	echo "<input type='radio' name='IsExecute' value='no'> NoExecute" . "<br/>" . "<br/>";
	echo "<input type='submit' value='Submit' />";
	echo "<input type='reset' value='Reset' />" . "<br/>";
	echo "</form>";
}
else
{
	$querySql="select * from DeviceExecute";
	$res=$db->Query($querySql);
	$totalNum=$db->GetRowsNum($res);

	$querySql="select DeviceInfo.ACTIONSTATUS, DeviceInfo.NETTYPE, DeviceInfo.IP, DeviceInfo.MAC, DeviceInfo.PEERID, DeviceInfo.FREEMEM, DeviceInfo.FREEDISK, DeviceInfo.OSTYPE, DeviceExecute.FILE from DeviceExecute, DeviceInfo where DeviceExecute.MAC=DeviceInfo.MAC and DeviceInfo.ACTIONSTATUS in ('Execution_OK', 'Execution_Err')";
	$res=$db->Query($querySql);
	$actualNum=$db->GetRowsNum($res);
	/*
	while($totalNum != $actualNum)
	{
		sleep(5);
		$res=$db->Query($querySql);
		$actualNum=$db->GetRowsNum($res);
	}
	*/
	if($totalNum != $actualNum)
	{
		sleep(3);
		echo "<p> devices are executing file disposed, wait for a moment... </p>";
		echo "<form enctype='multipart/form-data' action='/manual/executeresult.php' method='post'>";
		echo "<label class='tips'> Display the result of execute file </label>";
		echo "<br/>";
		echo "<input type='radio' name='IsEchoExecuteRes' value='yes' checked> Display " . "<br/>";
		echo "<input type='radio' name='IsEchoExecuteRes' value='no'> NoDisplay" . "<br/>" . "<br/>";
		echo "<input type='submit' value='Submit' />";
		echo "<input type='reset' value='Reset' />" . "<br/>";
		echo "</form>";
		echo "</div>";
		echo "</form>";
		echo "</body>";
		echo "</html>";
		return;		
	}

	echo "<form enctype='multipart/form-data' action='/manual/collectlog.php' method='post'>";
	echo "<table width='400' border='1'>
	<caption> The result of execute files on devices </caption>
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
		case "Execution_OK":
			echo "<td bgcolor=#00FF00 align='center'>" . $row[ACTIONSTATUS] . "</td>";
		break;
		case "Execution_Err":
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
	echo "<label class='tips'> Master collect log from devices </label>";
	echo "<br/>";
	echo "<input type='radio' name='IsCollectLog' value='yes' checked> CollectLog" . "<br/>";
	echo "<input type='radio' name='IsCollectLog' value='no'> NoCollectLog" . "<br/>" . "<br/>";
	echo "<input type='submit' value='Submit' />";
	echo "<input type='reset' value='Reset' />" . "<br/>";
	echo "</form>";
}
?>
</div>
</form>
</body>
</html>
