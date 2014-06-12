<?php
require_once('../mysqlconf.php');
require_once('../devicesql.php');

$db=new Device($db_host, $db_user, $db_pwd, $db_name, $db_charSet, $db_conn);
$querySql="select * from DeviceDispose";
$res=$db->Query($querySql);
while($row=mysql_fetch_array($res))
{
	$updateTableSql="update DeviceInfo set ACTIONSTATUS='FINISHED' where MAC='$row[MAC]'";
	$res=$db->Query($updateTableSql);
}
$delTableSql="drop table DeviceDispose";
$res=$db->Query($delTableSql);
$delTableSql="drop table DeviceExecute";
$res=$db->Query($delTableSql);
$delTableSql="drop table DeviceReportLog";
$res=$db->Query($delTableSql);

echo "<p>System Exit </p>";
?>
