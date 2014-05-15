<?php

class Device
{
    private $db_host;
    private $db_user;
    private $db_pwd;
    private $db_name;
    private $db_charSet;
    private $conn;
    private $sql;
    private $res;
    private $resarray;

    public function __construct($db_host, $db_user, $db_pwd, $db_name, $db_charSet, $conn)
    {
        $this->db_host=$db_host;
        $this->db_user=$db_user;
        $this->db_pwd=$db_pwd;
        $this->db_name=$db_name;
        $this->db_charSet=$db_charSet;
        $this->conn=$conn;
        $this->resarray=array();
        $this->Connect();
    }

    public function Connect()
    {
        if($this->conn=="pconn")
        {
            $this->conn=mysql_pconnect($this->db_host, $this->db_user, $this->db_pwd);
            if(!$this->conn)
            {
                die("Could not pconnect: " . mysql_error() . "\n");
            }
            else
            {
                echo "Connected successfully\n";
            }
        }
        else
        {
            $this->conn=mysql_connect($this->db_host, $this->db_user, $this->db_pwd);
            if(!$this->conn)
            {
                die("Could not connect: " . mysql_error() . "\n");
            }
            else
            {
                echo "Connected successfully\n";
            }
        }

        $this->SelectDataBase($this->db_name);
        mysql_query("SET NAMES $this->db_charSet");
        mysql_query("SET CHARACTER_SET_CLIENT='$this->db_charSet'");  
        mysql_query("SET CHARACTER_SET_RESULTS='$this->db_charSet'"); 
    }
    
    public function SelectDataBase($db_name)
    {
        $this->CreateDatabase($db_name);
        $selected=mysql_select_db($db_name, $this->conn);
        if(!$selected)
        {
           die("Can not use database: " . $db_name . " ,error info: " . mysql_error() . "\n"); 
        }
        else
        {
            echo "Select database " . $db_name . " successfully\n"; 
        }
    }
    
    public function CreateDatabase($db_name)
    {
        $sql="CREATE DATABASE IF NOT EXISTS " . $db_name;
        $this->Query($sql);
    }

    public function Query($sql)
    {
        if($sql=="")
        {
            die("sql syntax error, sql should not be null\n");
        }

        $this->sql=$sql;
        $res=mysql_query($this->sql, $this->conn);
        if(!$res)
        {
            die("Invalid query:" . $sql . ". error info: " . mysql_error() . "\n");
        }
        else
        {
            $this->res=$res;
            echo $sql . " successfully\n";
        }

        return $this->res;
    }

    public function GetFieldsNum($res)
    {
        return mysql_num_fields($res);
    }

    public function GetRowsNum($res)
    {
        if(mysql_errno()==0)
        {
            return mysql_num_rows($res);
        }
        else
        {
            die("Invalid sql: " . $this->sql . ". error info: " . mysql_error() . "\n");
        }
    }

    public function GetResult($res)
    {
        if($this->GetRowsNum()>0)
        {
            while($rows=mysql_fetch_array($res))
            {
                $this->resarray[]=$rows;
            }

            return $this->resarray;
        }
    }

    public function __destruct()
    {
        mysql_close($this->conn);
    }
}

?>
