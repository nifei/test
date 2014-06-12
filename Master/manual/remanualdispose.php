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
<h3 align="center"> Dispose File Continue</h3>
<div id="devicelist">
<?php
require_once('../mysqlconf.php');
require_once('../devicesql.php');

$db=new Device($db_host, $db_user, $db_pwd, $db_name, $db_charSet, $db_conn);
$prefix="/usr/share/nginx/www/download/";
if ($_FILES["file"]["error"] > 0)
{
	echo "Error: " . $_FILES["file"]["error"] . "<br />";
	return;
}
else
{
	echo "Upload: " . $_FILES["file"]["name"] . "<br />";
	echo "Type: " . $_FILES["file"]["type"] . "<br />";
	echo "Size: " . ($_FILES["file"]["size"] / 1024) . " Kb<br />";
	echo "Upload tmp_name: " . $_FILES["file"]["tmp_name"] . "<br />";
	
	if (file_exists($prefix . $_FILES["file"]["name"]))
	{
		$fileName=$prefix . $_FILES["file"]["name"];
		echo $_FILES["file"]["name"] . " already exists, Update " . $_FILES["file"]["name"] . "<br/>";
		unlink ($fileName);
	}	
	move_uploaded_file($_FILES["file"]["tmp_name"], $prefix . $_FILES["file"]["name"]);
	echo "Stored in: " . $prefix. $_FILES["file"]["name"] . "<br/>";
}

$fileName=$_FILES["file"]["name"];
//$tempTableSql="CREATE TABLE IF NOT EXISTS DeviceDispose(ID int(10) unsigned NOT NULL AUTO_INCREMENT, MAC char(30) NOT NULL, PEERID char(30) NOT NULL, FILE char(30) NOT NULL, PRIMARY KEY(ID))";
//$res=$db->Query($tempTableSql);

foreach($_POST['DevicesChecked'] as $var)
{
	echo "VAR".$var;
	$querySql="select * from DeviceInfo where MAC='$var'";
	$res=$db->Query($querySql);
	$row=mysql_fetch_array($res);
	echo " ID:";
	echo $row[ID];
	echo " MAC:";
	echo $row[MAC];
	echo "\n";
	echo "INSERT INTO DeviceAction(ID, ACTION, MAC, FILE) VALUES('', 'GET', '$row[MAC]', '$fileName')";
	//$updateSql="UPDATE DeviceAction SET ACTION='GET', FILE='$fileName' WHERE MAC='$row[MAC]' AND PEERID='$row[PEERID]'";
	$insertSql="INSERT INTO DeviceAction(ID, ACTION, MAC, FILE) VALUES('', 'GET', '$row[MAC]', '$fileName')";
	$res=$db->Query($insertSql);
	$insertSql="INSERT INTO DeviceDispose VALUES('', '$row[MAC]', '$row[PEERID]', '$fileName')";
	$res=$db->Query($insertSql);
}

if($_POST['IsReDispose'] == "yes")
{
	//foreach($_POST['DevicesChecked'] as $var)
	//	echo $var . "<br/>";
	echo "<form enctype='multipart/form-data' action='/manual/remanualdispose.php' method='post'>";
	//$querySql="select DeviceInfo.ACTIONSTATUS, DeviceInfo.NETTYPE, DeviceInfo.IP, DeviceInfo.MAC, DeviceInfo.PEERID, DeviceInfo.FREEMEM, DeviceInfo.FREEDISK, DeviceInfo.OSTYPE, DeviceAction.FILE from DeviceInfo, DeviceAction where DeviceInfo.MAC=DeviceAction.MAC and DeviceAction.FILE!='' ORDER BY DeviceInfo.ID";
	//$querySql="SELECT DeviceInfo.ACTIONSTATUS, DeviceInfo.NETTYPE, DeviceInfo.IP, DeviceInfo.MAC, DeviceInfo.PEERID, DeviceInfo.FREEMEM, DeviceInfo.FREEDISK, DeviceInfo.OSTYPE from DeviceInfo ORDER BY DeviceInfo.FREEMEM";
	$querySql="SELECT * FROM DeviceInfo";
	$res=$db->Query($querySql);
	echo "<table width='400' border='1'>
	<caption> Dispose file to devices continue </caption>
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
		$flag=false;
		//echo "<tr>";
		//echo "<td align='center'>" . ++$i . "</td>";
		$tmpQuerySql="SELECT FILE FROM DeviceDispose WHERE MAC='$row[MAC]'";
		$tmpres=$db->Query($tmpQuerySql);
		while($tmprow=mysql_fetch_array($tmpres))
		{
			$flag=true;
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
			echo "<td align='center'>" . $tmprow[FILE] . "</td>";
			echo "<td align='right'> <input type='checkbox' name='DevicesChecked[]' value='$row[MAC]'>" . "</td>";
			echo "</tr>";
		}
	
		if($flag)
		{
			continue;
		}

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
		echo "<td align='center'>" . "" . "</td>";
		echo "<td align='right'> <input type='checkbox' name='DevicesChecked[]' value='$row[MAC]'>" . "</td>";
		echo "</tr>";
	}

	echo "</table>";
	echo "<br/>";
	echo "<label class='tips'> Upload File </label>";
	echo "<input name='file' type='file'/>";
	echo "<br/>";
	echo "<label class='tips'> Continue to deploy file </label>";
	echo "<br/>";
	echo "<input type='radio' name='IsReDispose' value='yes' checked> ReDispose" . "<br/>";
	echo "<input type='radio' name='IsReDispose' value='no'> NoDispose" . "<br/>" . "<br/>";
	echo "<input type='submit' value='Submit' />";
	echo "<input type='reset' value='Reset' />" . "<br/>";
	echo "</form>";
}
else
{
	$querySql="select * from DeviceDispose";
	$res=$db->Query($querySql);
	$totalNum=$db->GetRowsNum($res);

	$querySql="select DeviceInfo.ACTIONSTATUS, DeviceInfo.NETTYPE, DeviceInfo.IP, DeviceInfo.MAC, DeviceInfo.PEERID, DeviceInfo.FREEMEM, DeviceInfo.FREEDISK, DeviceInfo.OSTYPE, DeviceDispose.FILE from DeviceDispose, DeviceInfo where DeviceDispose.MAC=DeviceInfo.MAC and DeviceInfo.ACTIONSTATUS in ('Disposition_OK', 'Disposition_Err')";
	$res=$db->Query($querySql);
	$actualNum=$db->GetRowsNum($res);
	echo "totalNum=" . $totalNum;
	echo "actualNum=" . $actualNum;
	/*
	while($totalNum != $actualNum)
	{
		sleep(3);
		$res=$db->Query($querySql);
		$actualNum=$db->GetRowsNum($res);
	}
	*/

	if($totalNum!=$actualNum)
	{
		sleep(3);
		echo "<p> Master is disposing files to devices, wait for a moment... </p>";
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
?>
</div>
</form>
</body>
</html>
