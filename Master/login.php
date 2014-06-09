<?php
require_once('mysqlconf.php');
require_once('devicesql.php');

$db=new Device($db_host, $db_user, $db_pwd, $db_name, $db_charSet, $db_conn);

$createTableSql="CREATE TABLE IF NOT EXISTS DeviceInfo(
        ID int(10) unsigned NOT NULL AUTO_INCREMENT, 
	STATUS char(30) NOT NULL, 
	IP char(30) NOT NULL, 
	MAC char(30) NOT NULL, 
	NATTYPE char(30) NOT NULL, 
	NAT char(30) NOT NULL, 
	TUNNEL int(10), 
	PEERID char(30),
	SHARED_COUNT int(10),
	PRIMARY KEY(ID))";
$db->Query($createTableSql);

$createTableSql="CREATE TABLE IF NOT EXISTS DeviceAction(
        ID int(10) unsigned NOT NULL AUTO_INCREMENT, 
	MAC char(30) NOT NULL, 
	ACTION char(30) NOT NULL DEFAULT 'WAIT', 
	FILE char(30) NOT NULL DEFAULT '', 
	STATUS char(30) NOT NULL, 
	TASK_ID int(10) unsigned DEFAULT 0, 
	PRIMARY KEY(ID))";
$db->Query($createTableSql);

$createTableSql="CREATE TABLE IF NOT EXISTS Tasks (
        ID int(10) unsigned NOT NULL AUTO_INCREMENT, 
	TEST_CASE char(30) NOT NULL, 
	TASK_NAME char(30) NOT NULL, 
	STATUS char(30) NOT NULL, 
	CURRENT_STEP int(10), 
	PRIMARY KEY(ID))";
$db->Query($createTableSql);

$createTableSql="CREATE TABLE IF NOT EXISTS TaskDeviceRelation (
        ID int(10) unsigned NOT NULL AUTO_INCREMENT, 
	TASK_ID int(10) NOT NULL, 
	DEVICE_ID int(10) NOT NULL, 
	ROLE char(30) NOT NULL, 
	PRIMARY KEY(ID))";
$db->Query($createTableSql);

$querySql="SELECT * FROM DeviceInfo WHERE MAC='$_POST[MAC]'";
$res=$db->Query($querySql);
$numRows=$db->GetRowsNum($res);
echo "login.php numRows=" . $numRows . "\n";

if($numRows==0)
{
    echo "$_POST[MAC] Login Firstly.\n";
    $insertSql="INSERT INTO DeviceInfo values(
          '', 
          '$_POST[STATUS]', 
	  '$_POST[IP]', 
	  '$_POST[MAC]', 
	  '$_POST[NATTYPE]', 
	  '$_POST[NAT]', 
	  '$_POST[TUNNEL]', 
	  '$_POST[PEERID]',
	  0)";
    $db->Query($insertSql);
    $affectedRows=mysql_affected_rows();
    echo  $affectedRows . " Records Insterted\n";

}
else if($numRows==1)
{
    echo "$_POST[MAC] has Logged in already\n";
    $updateSql="UPDATE DeviceInfo SET 
        STATUS='$_POST[STATUS]', 
	IP='$_POST[IP]', 
	NATTYPE='$_POST[NATTYPE]', 
	NAT='$_POST[NAT]', 
	TUNNEL='$_POST[TUNNEL]',
	PEERID='$_POST[PEERID]'
        WHERE MAC='$_POST[MAC]'";
    $db->Query($updateSql);
    $affectedRows=mysql_affected_rows();
    echo $affectedRows . " Records Updated\n";
}
else
{
    exit("More than two Records. Error, MAC='$_POST[MAC]'\n");
}

?>
