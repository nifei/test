<?php
require_once('mysqlconf.php');
require_once('devicesql.php');

$db=new Device($db_host, $db_user, $db_pwd, $db_name, $db_charSet, $db_conn);

$createTableSql="CREATE TABLE IF NOT EXISTS DeviceInfo(ID int(10) unsigned NOT NULL AUTO_INCREMENT, STATUS char(30) NOT NULL, IP char(30) NOT NULL, MAC char(30) NOT NULL, NATTYPE char(30) NOT NULL, PRIMARY KEY(ID))";
$db->Query($createTableSql);

$createTableSql="CREATE TABLE IF NOT EXISTS DeviceAction(ID int(10) unsigned NOT NULL AUTO_INCREMENT, MAC char(30) NOT NULL, ACTION char(30) NOT NULL DEFAULT 'WAIT', FILE char(30) NOT NULL DEFAULT '', STATUS char(30) NOT NULL, PRIMARY KEY(ID))";
$db->Query($createTableSql);

$querySql="SELECT * FROM DeviceInfo WHERE MAC='$_POST[MAC]'";
$res=$db->Query($querySql);
$numRows=$db->GetRowsNum($res);
echo "login.php numRows=" . $numRows . "\n";

if($numRows==0)
{
    echo "$_POST[MAC] Login Firstly.\n";
    $insertSql="INSERT INTO DeviceInfo values('', '$_POST[STATUS]', '$_POST[IP]', '$_POST[MAC]', '$_POST[NATTYPE]')";
    $db->Query($insertSql);
    $affectedRows=mysql_affected_rows();
    echo  $affectedRows . " Records Insterted\n";

#    $insertSql="INSERT INTO DeviceAction(ID, MAC) values('', '$_POST[MAC]')";
#    $db->Query($insertSql);
#    $affectedRows=mysql_affected_rows();
#    echo $affectedRows . " Records Insterted\n";
}
else if($numRows==1)
{
    echo "$_POST[MAC] has Logged in already\n";
    $updateSql="UPDATE DeviceInfo SET STATUS='$_POST[STATUS]', IP='$_POST[IP]', NATTYPE='$_POST[NATTYPE]' WHERE MAC='$_POST[MAC]'";
    $db->Query($updateSql);
    $affectedRows=mysql_affected_rows();
    echo $affectedRows . " Records Updated\n";

#    Remove lines to update DeviceAction on Action = "Wait"
#    "Wait" Action will be returned in "action.php" while there's no matching records for queried device
#    $updateSql="UPDATE DeviceAction SET ACTION='WAIT', FILE='' WHERE MAC='$_POST[MAC]'";
#    $updateSql="Insert into DeviceAction (ACTION, FILE, STATUS, MAC) values('WAIT', '', 'PENDING', '$_POST[MAC]')";
#    $db->Query($updateSql);
#    $affectedRows=mysql_affected_rows();
#    echo $affectedRows . " Records Updated\n";
}
else
{
    exit("More than two Records. Error, MAC='$_POST[MAC]'\n");
}

?>
