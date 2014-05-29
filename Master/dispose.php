<?php
require_once('mysqlconf.php');
require_once('devicesql.php');
require_once('function.php');

$prefix="/usr/share/nginx/www/download/";
#$prefix="/usr/local/nginx/html/download/";
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
		echo $_FILES["file"]["name"] . " already exists, Cover " . $_FILES["file"]["name"] . "<br/>";
		unlink ($fileName);
	}
	
	move_uploaded_file($_FILES["file"]["tmp_name"], $prefix . $_FILES["file"]["name"]);
	echo "Stored in: " . $prefix. $_FILES["file"]["name"];
}

$fileName="download/" . $_FILES["file"]["name"];

$db=new Device($db_host, $db_user, $db_pwd, $db_name, $db_charSet, $db_conn);

$DianXinNumDevices=GetNumAvailableDevicesWithNatType($db, "dianxin");
$LianTongNumDevices=GetNumAvailableDevicesWithNatType($db, "liantong");
$YiDongNumDevices=GetNumAvailableDevicesWithNatType($db, "yidong");

if($_POST['dianxin']>$DianXinNumDevices)
{
	echo "There is just " . $DianXinNumDevices . " Devices, less than your requirement " . $_POST['dianxin'] . "<br/>";
	return;
}
else
{
	DisposeFileToDevices($db, "dianxin", $fileName, $_POST['dianxin']);
}

if($_POST['liantong']>$LianTongNumDevices)
{
	echo "There is just " . $LianTongNumDevices . " Devices, less than your requirement " . $_POST['liantong'] . "<br/>";
	return;
}
else
{
	DisposeFileToDevices($db, "liantong", $fileName, $_POST['liantong']);
}

if($_POST['yidong']>$YiDongNumDevices)
{
	echo "There is just " . $YiDongNumDevices . " Devices, less than your requirement " . $_POST['yidong'] . "<br/>";
	return;
}
else
{
	DisposeFileToDevices($db, "yidong", $fileName, $_POST['yidong']);
}

$done=false;
$DianXinDone=false;
$LianTongDone=false;
$YiDongDone=false;

while(!$done)
{
	if(!$DianXinDone)
	{
		$DianXinDone=CheckDisposeDoneWithNatType($db, "dianxin", $_POST['dianxin']);
	}
	
	if(!$LianTongDone)
	{
		$LianTongDone=CheckDisposeDoneWithNatType($db, "liantong", $_POST['liantong']);
	}
	
	if(!$YiDongDone)
	{
		$YiDongDone=CheckDisposeDoneWithNatType($db, "yidong", $_POST['yidong']);
	}
	
	if($DianXinDone && $LianTongDone && $YiDongDone)
	{
		$done=true;	
	}
	else
	{
		echo "Disposing file: " . $fileName . " to Devices...... " . "<br/>";
		sleep(5);	
	}
}

if($_POST['dianxin'] > 0)
{
	EchoDisposeResultsWithNatType($db, "dianxin", $_POST['dianxin'], $fileName);
}

if($_POST['liantong'] > 0)
{
	EchoDisposeResultsWithNatType($db, "liantong", $_POST['liantong'], $fileName);
}

if($_POST['yidong'] > 0)
{
	EchoDisposeResultsWithNatType($db, "yidong", $_POST['yidong'], $fileName);
}

?>

<HTML>
<HEAD>
<TITLE>Device Net Information</TITLE>
</HEAD>
<BODY>

<div>
<form name="frmImage" enctype="multipart/form-data" action="http://127.0.0.1/execute.php" method="post">
	
	<label>File to Execute:	</label>
	<input type="text" name="fileName" value=""/>
	<br />
	
	<input type="radio" name="IS_Execute" value="1" checked> EXECUTE
	<input type="radio" name="IS_Execute" value="0" > UNEXECUTE
	<br/>
	
	<input type="submit" value="Submit" />
	<input type="reset" value="Reset" />
	<br/>
	
</form>
</div>
</BODY>
</HTML>
