CREATE TABLE IF NOT EXISTS DeviceInfo(
        ID int(10) unsigned NOT NULL AUTO_INCREMENT, 
	STATUS char(30) NOT NULL, 
	IP char(30) NOT NULL, 
	MAC char(30) NOT NULL, 
	NATTYPE char(30) NOT NULL, 
	NAT char(30) NOT NULL, 
	TUNNEL int(10), 
	PEERID char(30),
	SHARED_COUNT int(10),
	PRIMARY KEY(ID));

CREATE TABLE IF NOT EXISTS DeviceAction(
        ID int(10) unsigned NOT NULL AUTO_INCREMENT, 
	MAC char(30) NOT NULL, 
	ACTION char(30) NOT NULL DEFAULT 'WAIT', 
	FILE char(30) NOT NULL DEFAULT '', 
	STATUS char(30) NOT NULL, 
	TASK_ID int(10) unsigned DEFAULT 0, 
	PRIMARY KEY(ID));

CREATE TABLE IF NOT EXISTS Tasks (
        ID int(10) unsigned NOT NULL AUTO_INCREMENT, 
	TEST_CASE char(30) NOT NULL, 
	TASK_NAME char(30) NOT NULL, 
	STATUS char(30) NOT NULL, 
	CURRENT_STEP int(10) unsigned, 
	STOP_FLAG BOOL DEFAULT FALSE,
	PAUSE_FLAG BOOL DEFAULT FALSE,
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
insert into DeviceInfo values ('', 'Online', '1.1.1.1', 'MAC-1', 'yidong', 'None', 1, 'PID1', 0);
insert into DeviceInfo values ('', 'Online', '2.1.1.1', 'MAC-2', 'yidong', 'Addr', 2, 'PID2', 0);
insert into DeviceInfo values ('', 'Online', '3.1.1.1', 'MAC-3', 'yidong', 'Cone', 3, 'PID3', 0);
insert into DeviceInfo values ('', 'Online', '4.1.1.1', 'MAC-4', 'yidong', 'Addr', 4, 'PID4', 0);
insert into DeviceInfo values ('', 'Online', '5.1.1.1', 'MAC-5', 'liantong', 'Symm', 5, 'PID5', 0);
insert into DeviceInfo values ('', 'Online', '6.1.1.1', 'MAC-6', 'liantong', 'Addr', 6, 'PID6', 0);
insert into DeviceInfo values ('', 'Online', '7.1.1.1', 'MAC-7', 'liantong', 'None', 7, 'PID7', 0);
insert into DeviceInfo values ('', 'Online', '8.1.1.1', 'MAC-8', 'dianxin', 'Cone', 8, 'PID8', 0);
insert into DeviceInfo values ('', 'Online', '9.1.1.1', 'MAC-9', 'dianxin', 'Cone', 9, 'PID9', 0);
insert into DeviceInfo values ('', 'Online', '0.1.1.1', 'MAC-0', 'dianxin', 'Addr', 0, 'PID0', 0);
insert into DeviceInfo values ('', 'Online', '1.2.1.1', 'MAC-11', 'dianxin', 'Cone', 11, 'PID0', 0);
