<?php

$hostname = "localhost";
$username = "root";
$password = "";
$database = "robotsensorsmeasurment_db";

$conn = mysqli_connect($hostname, $username, $password, $database);

if (!$conn){
	die("Connection failed!".mysqli_connect_error());
}

echo "Database connection is OK<br>";


if(isset($_POST["xValue"]) && isset($_POST["yValue"]) && isset($_POST["Obstacle_distance"])&& isset($_POST["Control_direction"]) && isset($_POST["collision"])) {

	$xValue = $_POST["xValue"];
	$yValue = $_POST["yValue"];
	$Obstacle_distance = $_POST["Obstacle_distance"];
	$Control_direction = $_POST["Control_direction"];
	$collision = $_POST["collision"];

	$sql = "INSERT INTO sensor_data (`XValue`, `YValue`, `Obstacle Distance`, `Control direction`, `Robot Collision`)
	VALUES ($xValue, $yValue, $Obstacle_distance, '$Control_direction', $collision)";

	if (mysqli_query($conn, $sql)) { 
		echo "\nNew record created successfully"; 
	} else { 
		echo "Error: " . $sql . "<br>" . mysqli_error($conn); 
	}
}
?>