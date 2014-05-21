<?php

require_once('mysqlconf.php');
require_once('devicesql.php');
require_once('function.php');


$fileName=$_POST['fileName'];

if($_POST['IS_Execute']==0)
{
	echo "Checked UnExecute, value: " . $_POST['IS_Execute'] . "<br/>";
	return;
}

echo "fileName: " . $fileName . "<br/>";
echo "Checked " . $_POST['IS_Execute'] . "<br/>";
$db=new Device($db_host, $db_user, $db_pwd, $db_name, $db_charSet, $db_conn);

$numRes = CtrlDevicesExecuteFile($db, $fileName);
WaitExecuteDone($db, $fileName, $numRes);

?>

<HTML>
<HEAD>
<TITLE>Device Net Information</TITLE>
</HEAD>
<BODY>

<div>
<form name="frmImage" enctype="multipart/form-data" action="http://127.0.0.1/reportlog.php" method="post">
	
	<p> reportlog.php Unfinished </p>
	<br/>
	<input type="radio" name="IS_ReportLog" value="1" > ReportLog
	<input type="radio" name="IS_ReportLog" value="0" checked> UnReportLog
	<br/>
	
	<input type="submit" value="Submit" />
	<input type="reset" value="Reset" />
	<br/>
	
</form>
</div>
</BODY>
</HTML>
