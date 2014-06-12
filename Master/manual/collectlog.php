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
<h3 align="center"> Collect Log </h3>
<div id="devicelist">
<?php
require_once('../mysqlconf.php');
require_once('../devicesql.php');

$querySql="select DeviceExecute.ID, DeviceInfo.ACTIONSTATUS, DeviceInfo.NETTYPE, DeviceInfo.IP, DeviceInfo.MAC, DeviceInfo.PEERID, DeviceInfo.FREEMEM, DeviceInfo.FREEDISK, DeviceInfo.OSTYPE, DeviceExecute.FILE from DeviceInfo, DeviceExecute where DeviceExecute.MAC=DeviceInfo.MAC";
$db=new Device($db_host, $db_user, $db_pwd, $db_name, $db_charSet, $db_conn);
$res=$db->Query($querySql);
$resNum=$db->GetRowsNum($res);

if($_POST['IsCollectLog'] == 'yes')
{
	echo "<form enctype='multipart/form-data' action='/manual/recollectlog.php' method='post'>";
	echo "<table width='400' border='1'>
	<caption> Check Devices to report log to master </caption>
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
		<th>FILE</th>
		<th>IsChecked</th>
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
		echo "<td align='right'> <input type='checkbox' name='DevicesChecked[]' value='$row[ID]'>" . "</td>";
		echo "</tr>";
	}

	echo "</table>";
	echo "<br/>";
	echo "<label class='tips'> Master collects log from devices continue</label>";
	echo "<br/>";
	echo "<input type='radio' name='IsReCollectLog' value='yes' checked> ReCollectLog <br/>";
	echo "<input type='radio' name='IsReCollectLog' value='no'> NoCollectLog <br/>";
	echo "<br/>";
	echo "<input type='submit' value='Submit' />";
	echo "<input type='reset' value='Reset' />";
	echo "<br/>";
	echo "</form>";
}
else
{
	echo "<form enctype='multipart/form-data' action='/manual/systemexit.php' method='post'>";
	echo "<br/>";
	echo "<label class='tips'> Exit System </label>";
	echo "<br/>";
	echo "<input type='radio' name='IsExitSystem' value='yes' checked> ExitSystem" . "<br/>";
	echo "<input type='radio' name='IsExitSystem' value='no'> NoExitSystem" . "<br/>" . "<br/>";
	echo "<input type='submit' value='Submit' />";
	echo "<input type='reset' value='Reset' />" . "<br/>";
	echo "</form>";

}
?>
</div>
</body>
</html>
