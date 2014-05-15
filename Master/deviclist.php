<?php
require_once('mysqlconf.php');
require_once('devicesql.php');

$querySql="select * from DeviceInfo";
$db=new Device($db_host, $db_user, $db_pwd, $db_name, $db_charSet, $db_conn);
$res=$db->Query($querySql);
$resNum=$db->GetRowsNum($res);

echo "Total Devices: " . $resNum . "<br/>";
echo "<table width='400' border='6'>
<caption>All Device Net Information</caption>
<tr>
	<td align='center'>ID</td>
	<td align='center'>Status</td>
	<td align='center'>IP</td>
	<td align='center'>MAC</td>
	<td align='center'>NatType</td>
</tr>";

while($row=mysql_fetch_array($res))
{
	echo "<tr>";
	echo "<td align='center'>" . $row[ID] . "</td>";
	echo "<td bgcolor='red' align='center'>" . $row[STATUS] . "</td>";
	echo "<td align='center'>" . $row[IP] . "</td>";
	echo "<td align='center'>" . $row[MAC] . "</td>";
	echo "<td align='center'>" . $row[NATTYPE] . "</td>";
	echo "</tr>";
}

echo "</table>";
?>

<HTML>
<HEAD>
<TITLE>Device Net Information</TITLE>
</HEAD>
<BODY>
<div>
<form name="frmImage" enctype="multipart/form-data" action="http://127.0.0.1/dispose.php" method="post" class="frmImageUpload">

<label>Peers: </label>
<input type="text" name="peers" value=""/>
<br />

<label>DianXin peers:	</label>
<input type="text" name="dianxin" value=""/>
<br />

<label>LianTong peers:	</label>
<input type="text" name="liantong" value=""/>
<br />

<label>YiDong peers:	</label>
<input type="text" name="yidong" value=""/>
<br />

<label>Upload File:	</label>
<input name="file" type="file" id="file" />
<br />
<br />
<input type="submit" value="Submit" />
<input type="reset" value="Reset" />
<br/>

</form>
</div>
</BODY>
</HTML>
