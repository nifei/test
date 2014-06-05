<?php
$result = null;
$prefix="/home/test/TestCaseFiles/";

$tmp_file=$_FILES["fileUpLoad"]["tmp_name"];
$target_file=$prefix.$_FILES["fileUpLoad"]["name"];
move_uploaded_file($tmp_file, $target_file);
echo "<script>parent.notice('文件上传到 $target_file');</script>";
?>
