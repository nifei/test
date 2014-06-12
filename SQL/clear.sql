drop table DeviceInfo;
drop table DeviceAction;
drop table Tasks;
drop table TaskDeviceRelation;

CREATE TABLE IF NOT EXISTS DeviceInfo(
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
	PRIMARY KEY(ID));

CREATE TABLE IF NOT EXISTS DeviceAction(
        ID int(10) unsigned NOT NULL AUTO_INCREMENT,  
	ACTION char(30) NOT NULL DEFAULT 'WAIT', 
	MAC char(100) NOT NULL,
	FILE char(100) NOT NULL DEFAULT '', 
	STATUS char(30) NOT NULL DEFAULt 'PENDING', 
	TASK_ID int(10) unsigned DEFAULT 0, 
	PRIMARY KEY(ID));

CREATE TABLE IF NOT EXISTS Tasks (
        ID int(10) unsigned NOT NULL AUTO_INCREMENT, 
	TEST_CASE char(30) NOT NULL, 
	TASK_NAME char(30) NOT NULL, 
	STATUS char(30) NOT NULL, 
	CURRENT_STEP int(10), 
	STOP_FLAG BOOL,
	PAUSE_FLAG BOOL,
	PRIMARY KEY(ID));

CREATE TABLE IF NOT EXISTS TaskDeviceRelation (
        ID int(10) unsigned NOT NULL AUTO_INCREMENT, 
	TASK_ID int(10) NOT NULL, 
	DEVICE_ID int(10) NOT NULL, 
	ROLE char(30) NOT NULL, 
	PRIMARY KEY(ID));
delete from DeviceAction; 
delete from TaskDeviceRelation;
delete from Tasks;
delete from DeviceInfo;

