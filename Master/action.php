<?php
require_once('mysqlconf.php');
require_once('devicesql.php');

$db=new Device($db_host, $db_user, $db_pwd, $db_name, $db_charSet, $db_conn);

$updateSqlAction="UPDATE DeviceAction SET STATUS='$_POST[STATUS]' WHERE ID='$_POST[ACTION_ID]'"; 
$updateSqlInfo="UPDATE DeviceInfo SET IP='$_POST[IP]', NATTYPE='$_POST[NATTYPE]' WHERE MAC='$_POST[MAC]'";
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
        $updateSqlAction="UPDATE DeviceAction SET STATUS='RUNNING' WHERE ID='$next_action_id'"; 
        $db->Query($updateSqlAction);
        $extra_info="found";

}
$last_action_id=$_POST[ACTION_ID];

#switch($_POST['STATUS'])
#{
#case "Disposition_OK":
#case "Disposition_Err":
#    if($action!="EXECUTE")
#    {
#        $updateSql="UPDATE DeviceAction SET ACTION='WAIT' WHERE MAC='$_POST[MAC]'";
#        $db->Query($updateSql);
#        $action="WAIT";
#    }
#    break;
#
#case "Execution_OK":
#case "Execution_Err":
#    if($action!="REPLOG")
#    {
#        $updateSql="UPDATE DeviceAction SET ACTION='WAIT' WHERE MAC='$_POST[MAC]'";
#        $db->Query($updateSql);
#	$action="WAIT";
#    }
#    break;
#
#case "Test_Done":
#    $updateSql="UPDATE DeviceAction SET ACTION='WAIT', FILE='' WHERE MAC='$_POST[MAC]'";
#    $db->Query($updateSql);
#
#    $updateSql="UPDATE DeviceInfo SET STATUS='Idle' WHERE MAC='$_POST[MAC]'";
#    $db->Query($updateSql);
#
#    $action="WAIT";
#    $fileName='';
#    break;
#
#default:
#    break;
#}
#test

echo "ACTION_ID: " . $next_action_id . "\n";
echo "ACTION: " . $next_action . "\n";
echo "FILE: " . $next_fileName . "\n";
echo "EXTRA: " . $extra_info . "\n";
?>
