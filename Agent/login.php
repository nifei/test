Connected successfully
CREATE DATABASE IF NOT EXISTS P2PDevice successfully
Select database P2PDevice successfully
CREATE TABLE IF NOT EXISTS DeviceInfo(ID int(10) unsigned NOT NULL AUTO_INCREMENT, STATUS char(30) NOT NULL, IP char(30) NOT NULL, MAC char(30) NOT NULL, NATTYPE char(30) NOT NULL, PRIMARY KEY(ID)) successfully
CREATE TABLE IF NOT EXISTS DeviceAction(ID int(10) unsigned NOT NULL AUTO_INCREMENT, MAC char(30) NOT NULL, ACTION char(30) NOT NULL DEFAULT 'WAIT', FILE char(30) NOT NULL DEFAULT '', PRIMARY KEY(ID)) successfully
SELECT * FROM DeviceInfo WHERE MAC='00:0c:29:f2:2e:77' successfully
login.php numRows=1
00:0c:29:f2:2e:77 has Logged in already
UPDATE DeviceInfo SET STATUS='Online', IP='192.168.91.123', NATTYPE='liantong' WHERE MAC='00:0c:29:f2:2e:77' successfully
1 Records Updated
UPDATE DeviceAction SET ACTION='WAIT', FILE='' WHERE MAC='00:0c:29:f2:2e:77' successfully
1 Records Updated
