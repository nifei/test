Connected successfully
CREATE DATABASE IF NOT EXISTS P2PDevice successfully
Select database P2PDevice successfully
CREATE TABLE IF NOT EXISTS DeviceInfo(ID int(10) unsigned NOT NULL AUTO_INCREMENT, STATUS char(30) NOT NULL, IP char(30) NOT NULL, MAC char(30) NOT NULL, NATTYPE char(30) NOT NULL, PRIMARY KEY(ID)) successfully
CREATE TABLE IF NOT EXISTS DeviceAction(ID int(10) unsigned NOT NULL AUTO_INCREMENT, MAC char(30) NOT NULL, ACTION char(30) NOT NULL DEFAULT 'WAIT', FILE char(30) NOT NULL DEFAULT '', STATUS char(30) NOT NULL, PRIMARY KEY(ID)) successfully
SELECT * FROM DeviceInfo WHERE MAC='00:0c:29:37:84:7e' successfully
login.php numRows=0
00:0c:29:37:84:7e Login Firstly.
INSERT INTO DeviceInfo values('', 'Online', '10.45.30.158', '00:0c:29:37:84:7e', 'liantong') successfully
1 Records Insterted
INSERT INTO DeviceAction(ID, MAC) values('', '00:0c:29:37:84:7e') successfully
1 Records Insterted
