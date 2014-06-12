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
<h3 align="center"> Dispose File </h3>
<div id="devicelist">
<?php
require_once('../mysqlconf.php');
require_once('../devicesql.php');

$querySql="SELECT * from DeviceInfo ORDER BY FREEMEM";
$db=new Device($db_host, $db_user, $db_pwd, $db_name, $db_charSet, $db_conn);
$res=$db->Query($querySql);
$resNum=$db->GetRowsNum($res);

echo "<form enctype='multipart/form-data' action='/manual/remanualdispose.php' method='post'>";
echo "<table width='400' border='1'>
<caption> Check Devices to dispose files firstly </caption>
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
	<th>IsChecked</th>
</tr>";

$i=0;
while($row=mysql_fetch_array($res))
{
	echo "<tr>";
	echo "<td align='center'>" . ++$i . "</td>";
	
	switch($row[ACTIONSTATUS])
	{
	case "Idle":
		echo "<td bgcolor=#FF9933 align='center'>" . $row[ACTIONSTATUS] . "</td>";
	break;
	case "Disposition_OK":
	case "Execution_OK":
		echo "<td bgcolor=#00FF00 align='center'>" . $row[ACTIONSTATUS] . "</td>";
	break;
	case "Disposition_Err":
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
	echo "<td align='right'> <input type='checkbox' name='DevicesChecked[]' value='$row[MAC]'>" . "</td>";
	echo "</tr>";
}
echo "</table>";
?>
<br/>
<label class="tips"> Upload File </label>
<input name="file" type="file" class="tips"/>
<br/>
<label class="tips"> Continue to deploy file </label>
<br/>
<br/>
<input type="radio" name="IsReDispose" value="yes" checked> ReDispose <br/>
<input type="radio" name="IsReDispose" value="no"> NoDispose <br/>
<br/>
<input type="submit" value="Submit" />
<input type="reset" value="Reset" />
<br/>
<br/>
</div>
</form>
</body>
</html>
