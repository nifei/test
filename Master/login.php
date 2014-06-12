<?php
require_once('mysqlconf.php');
require_once('devicesql.php');

$db=new Device($db_host, $db_user, $db_pwd, $db_name, $db_charSet, $db_conn);

$createTableSql="CREATE TABLE IF NOT EXISTS DeviceInfo(
	ID int(10) unsigned NOT NULL AUTO_INCREMENT,
	ACTIONSTATUS char(30) NOT NULL,
	STATUS char(30) NOT NULL,
	NETTYPE char(30) NOT NULL,
	IP char(30) NOT NULL,
	MAC char(100) NOT NULL,
	PEERID char(30) DEFAULT '',
	NAT char(30) NOT NULL DEFAULT '',
	TUNNEL int(10) DEFAULT 0,
	FREEMEM int(16) unsigned DEFAULT 0,
	FREEDISK int(16) unsigned DEFAULT 0,
	OSTYPE char(10) NOT NULL DEFAULT '',
	SHARED_COUNT int(10) DEFAULT 0,
	PRIMARY KEY(ID))";
$db->Query($createTableSql);

$createTableSql="CREATE TABLE IF NOT EXISTS DeviceAction(
        ID int(10) unsigned NOT NULL AUTO_INCREMENT,  
	ACTION char(30) NOT NULL DEFAULT 'WAIT', 
	MAC char(100) NOT NULL,
	FILE char(100) NOT NULL DEFAULT '', 
	STATUS char(30) NOT NULL DEFAULt 'PENDING', 
	TASK_ID int(10) unsigned DEFAULT 0, 
	PRIMARY KEY(ID))";
$db->Query($createTableSql);

$createTableSql="CREATE TABLE IF NOT EXISTS Tasks (
        ID int(10) unsigned NOT NULL AUTO_INCREMENT, 
	TEST_CASE char(30) NOT NULL, 
	TASK_NAME char(30) NOT NULL, 
	STATUS char(30) NOT NULL, 
	CURRENT_STEP int(10), 
	STOP_FLAG BOOL,
	PAUSE_FLAG BOOL,
	PRIMARY KEY(ID))";
$db->Query($createTableSql);

$createTableSql="CREATE TABLE IF NOT EXISTS TaskDeviceRelation (
        ID int(10) unsigned NOT NULL AUTO_INCREMENT, 
	TASK_ID int(10) NOT NULL, 
	DEVICE_ID int(10) NOT NULL, 
	ROLE char(30) NOT NULL, 
	PRIMARY KEY(ID))";
$db->Query($createTableSql);

$tempTableSql="CREATE TABLE IF NOT EXISTS DeviceReportLog(ID int(10) unsigned NOT NULL AUTO_INCREMENT, MAC char(30) NOT NULL, PEERID char(30) NOT NULL, FILE char(30) NOT NULL, PRIMARY KEY(ID))";
$res=$db->Query($tempTableSql);

$tempTableSql="CREATE TABLE IF NOT EXISTS DeviceDispose(ID int(10) unsigned NOT NULL AUTO_INCREMENT, MAC char(30) NOT NULL, PEERID char(30) NOT NULL, FILE char(30) NOT NULL, PRIMARY KEY(ID))";
$res=$db->Query($tempTableSql);

$tempTableSql="CREATE TABLE IF NOT EXISTS DeviceExecute(ID int(10) unsigned NOT NULL AUTO_INCREMENT, MAC char(30) NOT NULL, PEERID char(30) NOT NULL, FILE char(30) NOT NULL, PRIMARY KEY(ID))";
$res=$db->Query($tempTableSql);

$querySql="SELECT * FROM DeviceInfo WHERE MAC='$_POST[MAC]'";
$res=$db->Query($querySql);
$numRows=$db->GetRowsNum($res);
echo "login.php numRows=" . $numRows . "\n";
$client_ip=$_SERVER["REMOTE_ADDR"];

if($numRows==0)
{
    echo "$_POST[MAC] Login Firstly.\n";
    $insertSql="INSERT INTO DeviceInfo values('', '$_POST[ACTIONSTATUS]', '$_POST[STATUS]', '$_POST[NETTYPE]', '$client_ip', '$_POST[MAC]', '$_POST[PEERID]', '$_POST[NAT]', '$_POST[TUNNEL]', '$_POST[FREEMEM]', '$_POST[FREEDISK]', '$_POST[OSTYPE]', 0)";
    $db->Query($insertSql);
    $affectedRows=mysql_affected_rows();
    echo  $affectedRows . " Records Insterted\n";

}
else if($numRows==1)
{
    echo "$_POST[MAC] has Logged in already\n";
    $updateSql="UPDATE DeviceInfo SET ACTIONSTATUS='$_POST[ACTIONSTATUS]',
        STATUS='$_POST[STATUS]',  
	NETTYPE='$_POST[NETTYPE]', 
	IP='$client_ip',
	PEERID='$_POST[PEERID]',
	NAT='$_POST[NAT]', 
	TUNNEL='$_POST[TUNNEL]',
	FREEMEM='$_POST[FREEMEM]',
	FREEDISK='$_POST[FREEDISK]',
	OSTYPE='$_POST[OSTYPE]'
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
