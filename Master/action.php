<?php
require_once('mysqlconf.php');
require_once('devicesql.php');

$downloadDir="download/";
$db=new Device($db_host, $db_user, $db_pwd, $db_name, $db_charSet, $db_conn);
$client_ip=$_SERVER["REMOTE_ADDR"];

$updateSqlAction="UPDATE DeviceAction SET STATUS='$_POST[STATUS]' WHERE ID='$_POST[ACTION_ID]'"; 
$updateSqlInfo="UPDATE DeviceInfo SET ACTIONSTATUS='$_POST[ACTIONSTATUS]', NETTYPE='$_POST[NETTYPE]', IP='$client_ip', PEERID='$_POST[PEERID]', NAT='$_POST[NAT]', TUNNEL='$_POST[TUNNEL]', FREEMEM='$_POST[FREEMEM]', FREEDISK='$_POST[FREEDISK]', OSTYPE='$_POST[OSTYPE]' WHERE MAC='$_POST[MAC]'";
$db->Query($updateSqlAction);
$db->Query($updateSqlInfo);
$querySql="SELECT ID, ACTION, FILE FROM DeviceAction WHERE MAC='$_POST[MAC]' and STATUS='PENDING' ORDER BY ID LIMIT 1";
$res=$db->Query($querySql);
$row=mysql_fetch_array($res);
if($row==False)
{
    $next_action_id=0;
    $next_action="WAIT";
    $next_fileName=""; 
    $extra_info="no rec";
}
else
{
	$next_action_id=$row['ID'];
	$next_action=$row['ACTION'];
	$next_fileName=$row['FILE'];
	if (strpos($row['FILE'], 'TestCaseFiles') === 0){
		$next_fileName=$row['FILE'];
	}
	else if ($next_action==='EXECUTE')
	{
		$next_fileName=$row['FILE'];
	}
	else
	{
		$next_fileName=$downloadDir . $row['FILE'];
	}
    $updateSqlAction="UPDATE DeviceAction SET STATUS='RUNNING' WHERE ID='$next_action_id'"; 
    $db->Query($updateSqlAction);
    $extra_info="found";
}
$last_action_id=$_POST[ACTION_ID];
echo "ACTION_ID: " . $next_action_id . "\n";
echo "ACTION: " . $next_action . "\n";
echo "FILE: " . $next_fileName . "\n";
echo "EXTRA: " . $extra_info . "\n";
echo "ADDR:" . $_SERVER["REMOTE_ADDR"] . "\n";
?>
