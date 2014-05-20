Connected successfully
CREATE DATABASE IF NOT EXISTS P2PDevice successfully
Select database P2PDevice successfully
UPDATE DeviceAction SET STATUS='Idle' WHERE ID='0' successfully
UPDATE DeviceInfo SET IP='10.45.30.158', NATTYPE='liantong' WHERE MAC='00:0c:29:37:84:7e' successfully
SELECT ID, ACTION, FILE FROM DeviceAction WHERE MAC='00:0c:29:37:84:7e' and STATUS='PENDING' ORDER BY ID LIMIT 1 successfully
ACTION_ID: 0
ACTION: WAIT
FILE: 
EXTRA: no rec
