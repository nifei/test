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
<h3 align="center"> Execute File </h3>
<div id="devicelist">
<?php
require_once('../mysqlconf.php');
require_once('../devicesql.php');

$querySql="select DeviceDispose.ID, DeviceInfo.ACTIONSTATUS, DeviceInfo.NETTYPE, DeviceInfo.IP, DeviceInfo.MAC, DeviceInfo.PEERID, DeviceInfo.FREEMEM, DeviceInfo.FREEDISK, DeviceInfo.OSTYPE, DeviceDispose.FILE from DeviceInfo, DeviceDispose where DeviceDispose.MAC=DeviceInfo.MAC";
$db=new Device($db_host, $db_user, $db_pwd, $db_name, $db_charSet, $db_conn);
$res=$db->Query($querySql);
$resNum=$db->GetRowsNum($res);

echo "<form enctype='multipart/form-data' action='/manual/remanualexecute.php' method='post'>";
echo "<table width='400' border='1'>
<caption> Check Devices to execute file </caption>
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
	//echo "<td align='right'> <input type='checkbox' name='DevicesChecked[]' value='$row[MAC]'>" . "</td>";
	echo "<td align='right'> <input type='checkbox' name='DevicesChecked[]' value='$row[ID]'>" . "</td>";
	echo "</tr>";
}

echo "</table>";
?>
<br/>
<label class='tips'> Execute files disposed on devices continue</label>
<br/>
<input type="radio" name="IsReExecute" value="yes" checked> ReExecute <br/>
<input type="radio" name="IsReExecute" value="no"> NoExecute <br/>
<br/>
<input type="submit" value="Submit" />
<input type="reset" value="Reset" />
<br/>
</form>
</div>
</body>
</html>
