Connected successfully
CREATE DATABASE IF NOT EXISTS P2PDevice successfully
Select database P2PDevice successfully
UPDATE DeviceInfo SET STATUS='Disposition_OK', IP='192.168.91.123', NATTYPE='liantong' WHERE MAC='00:0c:29:f2:2e:77' successfully
SELECT ACTION, FILE FROM DeviceAction WHERE MAC='00:0c:29:f2:2e:77' successfully
UPDATE DeviceAction SET ACTION='WAIT' WHERE MAC='00:0c:29:f2:2e:77' successfully
ACTION: WAIT
FILE: download/ltest.sh
