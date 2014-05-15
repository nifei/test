<?php
require_once('mysqlconf.php');
require_once('devicesql.php');

$db=new Device($db_host, $db_user, $db_pwd, $db_name, $db_charSet, $db_conn);

$updateSql="UPDATE DeviceInfo SET STATUS='$_POST[STATUS]', IP='$_POST[IP]', NATTYPE='$_POST[NATTYPE]' WHERE MAC='$_POST[MAC]'";
$db->Query($updateSql);

$querySql="SELECT ACTION, FILE FROM DeviceAction WHERE MAC='$_POST[MAC]'";
$res=$db->Query($querySql);
$row=mysql_fetch_array($res);
$action=$row['ACTION'];
$fileName=$row['FILE'];

switch($_POST['STATUS'])
{
case "Disposition_OK":
case "Disposition_Err":
    if($action!="EXECUTE")
    {
        $updateSql="UPDATE DeviceAction SET ACTION='WAIT' WHERE MAC='$_POST[MAC]'";
        $db->Query($updateSql);
        $action="WAIT";
    }
    break;

case "Execution_OK":
case "Execution_Err":
    if($action!="REPLOG")
    {
        $updateSql="UPDATE DeviceAction SET ACTION='WAIT' WHERE MAC='$_POST[MAC]'";
        $db->Query($updateSql);
	$action="WAIT";
    }
    break;

case "Test_Done":
    $updateSql="UPDATE DeviceAction SET ACTION='WAIT', FILE='' WHERE MAC='$_POST[MAC]'";
    $db->Query($updateSql);

    $updateSql="UPDATE DeviceInfo SET STATUS='Idle' WHERE MAC='$_POST[MAC]'";
    $db->Query($updateSql);

    $action="WAIT";
    $fileName='';
    break;

default:
    break;
}

echo "ACTION: " . $action . "\n";
echo "FILE: " . $fileName . "\n";

?>
