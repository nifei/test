<?php

function GetNumAvailableDevicesWithNatType($db, $fields)
{
	$querySql="select * from DeviceInfo where NATTYPE='$fields' and STATUS in ('Online', 'Idle')";
	$res=$db->Query($querySql);
	return $db->GetRowsNum($res);
}

function DisposeFileToDevices($db, $fields, $fileName, $NumDevicesRequired)
{
	$querySql="select * from DeviceInfo where NATTYPE='$fields' and STATUS in ('Online', 'Idle')";
	$res=$db->Query($querySql);
	
#	while($NumDevicesRequired>0 && $row=mysql_fetch_array($res))
	{
                $row=mysql_fetch_array($res);
		$updateSql="UPDATE DeviceAction SET ACTION='GET', FILE='$fileName', STATUS='PENDING' WHERE MAC='$row[MAC]'";
		$db->Query($updateSql);
		$NumDevicesRequired--;
	}
}

function CheckDisposeDoneWithNatType($db, $fields, $NumDevicesRequired)
{
	$querySql="select * from DeviceInfo,DeviceAction where DeviceInfo.MAC=DeviceAction.MAC and DeviceInfo.NATTYPE='$fields' and DeviceAction.STATUS in ('Disposition_OK', 'Disposition_Err')";
	$res=$db->Query($querySql);
	$numRes=$db->GetRowsNum($res);
	
	if($NumDevicesRequired>$numRes)
	{
		return false;
	}
	else
	{
		return true;
	}
}

function EchoDisposeResultsWithNatType($db, $fields, $NumDevicesRequired, $fileName)
{
	echo "Dispose File to " . $fields . " Devices: " . $NumDevicesRequired . "<br/>";
	echo "<table width='400' border='6'>
	<caption>" . $fields . " Device Dispose Results</caption>
	<tr>
		<td align='center'>Status</td>
		<td align='center'>IP</td>
		<td align='center'>MAC</td>
		<td align='center'>NatType</td>
		<td align='center'>FileName</td>
	</tr>";

	$querySql="select DeviceAction.STATUS, DeviceInfo.IP, DeviceInfo.MAC, DeviceInfo.NATTYPE , DeviceAction.FILE from DeviceInfo, DeviceAction where DeviceAction.FILE='$fileName' and DeviceAction.STATUS in ('Disposition_OK', 'Disposition_Err') and DeviceAction.MAC=DeviceInfo.MAC";
	$res=$db->Query($querySql);
	$numRes=$db->GetRowsNum($res);
	
	while($NumDevicesRequired>0 && $row=mysql_fetch_array($res))
	{
		$NumDevicesRequired--;
		echo "<tr>";
		echo "<td bgcolor='red' align='center'>" . $row[STATUS] . "</td>";
		echo "<td align='center'>" . $row[IP] . "</td>";
		echo "<td align='center'>" . $row[MAC] . "</td>";
		echo "<td align='center'>" . $row[NATTYPE] . "</td>";
		echo "<td align='center'>" . $row[FILE] . "</td>";
		echo "</tr>";
	}

	echo "</table>";	
}

function CtrlDevicesExecuteFile($db, $fileName)
{
	$querySql="select DeviceInfo.MAC as mac, DeviceAction.STATUS, DeviceAction.FILE from DeviceInfo, DeviceAction where DeviceAction.STATUS='Disposition_OK' and DeviceAction.FILE='$fileName' and DeviceInfo.MAC=DeviceAction.MAC";
	$res=$db->Query($querySql);
	$numRes=$db->GetRowsNum($res);
	echo "numRes: " . $numRes . "<br/>";
	
	while($row=mysql_fetch_array($res))
	{
		$updateSql="UPDATE DeviceAction SET ACTION='EXECUTE', STATUS='PENDING' WHERE MAC='$row[mac]'";
		$db->Query($updateSql);
	}
        return $numRes;

}

function WaitExecuteDone($db, $fileName, $numRes)
{
	$querySql="select DeviceAction.STATUS, DeviceInfo.IP, DeviceInfo.MAC, DeviceInfo.NATTYPE , DeviceAction.FILE from DeviceInfo, DeviceAction where DeviceAction.FILE='$fileName' and DeviceAction.STATUS='Disposition_OK' and DeviceAction.MAC=DeviceInfo.MAC";
	$res=$db->Query($querySql);
#	$numResRequire=$db->GetRowsNum($res);
	$numResRequire=$numRes;
	
	$querySql="select DeviceAction.STATUS, DeviceInfo.IP, DeviceInfo.MAC, DeviceInfo.NATTYPE , DeviceAction.FILE from DeviceInfo, DeviceAction where DeviceAction.FILE='$fileName' and DeviceAction.STATUS in ('Execution_OK', 'Execution_Err') and DeviceAction.MAC=DeviceInfo.MAC";
	
	while(true)
	{
		
		$res=$db->Query($querySql);
		$numRes=$db->GetRowsNum($res);
	
		if($numResRequire>$numRes)
		{
			echo "Executing " . $fileName . " On Devices......" . "<br/>";
			sleep(15);
		}
		else if($numResRequire==$numRes)
		{
			echo "<table width='400' border='6'>
			<caption>" . $numRes . " Device Execute done, Results As Follows</caption>
			<tr>
				<td align='center'>Status</td>
				<td align='center'>IP</td>
				<td align='center'>MAC</td>
				<td align='center'>NatType</td>
				<td align='center'>FileName</td>
			</tr>";
			
			while($row=mysql_fetch_array($res))
			{
				echo "<tr>";
				echo "<td bgcolor='red' align='center'>" . $row[STATUS] . "</td>";
				echo "<td align='center'>" . $row[IP] . "</td>";
				echo "<td align='center'>" . $row[MAC] . "</td>";
				echo "<td align='center'>" . $row[NATTYPE] . "</td>";
				echo "<td align='center'>" . $row[FILE] . "</td>";
				echo "</tr>";
			}
			
			echo "</table>";	
			break;
		}
		else
		{
			echo "Error" . "<br/>";
			break;
		}
		
	}
}

?>
