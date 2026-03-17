-- MySQL dump 10.13  Distrib 8.0.45, for Linux (x86_64)
--
-- Host: localhost    Database: RideShare
-- ------------------------------------------------------
-- Server version	8.0.45-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ActiveRides`
--

DROP TABLE IF EXISTS `ActiveRides`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ActiveRides` (
  `RideID` varchar(50) NOT NULL,
  `AdminID` int NOT NULL,
  `AvailableSeats` int NOT NULL,
  `PassengerCount` int NOT NULL,
  `Source` varchar(100) NOT NULL,
  `Destination` varchar(100) NOT NULL,
  `VehicleType` varchar(30) NOT NULL,
  `StartTime` datetime NOT NULL,
  `EstimatedTime` int NOT NULL,
  `FemaleOnly` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`RideID`),
  KEY `fk_activeride_admin` (`AdminID`),
  CONSTRAINT `fk_activeride_admin` FOREIGN KEY (`AdminID`) REFERENCES `Members` (`MemberID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ActiveRides_chk_1` CHECK ((`AvailableSeats` >= 0)),
  CONSTRAINT `ActiveRides_chk_2` CHECK ((`PassengerCount` >= 1))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `BookingRequests`
--

DROP TABLE IF EXISTS `BookingRequests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `BookingRequests` (
  `RequestID` int NOT NULL AUTO_INCREMENT,
  `RideID` varchar(50) NOT NULL,
  `PassengerID` int NOT NULL,
  `RequestStatus` varchar(20) NOT NULL DEFAULT 'PENDING',
  `RequestedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`RequestID`),
  KEY `fk_booking_ride` (`RideID`),
  KEY `fk_booking_passenger` (`PassengerID`),
  CONSTRAINT `fk_booking_passenger` FOREIGN KEY (`PassengerID`) REFERENCES `Members` (`MemberID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_booking_ride` FOREIGN KEY (`RideID`) REFERENCES `ActiveRides` (`RideID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Cancellation`
--

DROP TABLE IF EXISTS `Cancellation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Cancellation` (
  `RideID` varchar(50) NOT NULL,
  `MemberID` int NOT NULL,
  `CancellationReason` varchar(255) NOT NULL,
  KEY `fk_cancellation_ride` (`RideID`),
  KEY `fk_cancellation_member` (`MemberID`),
  CONSTRAINT `fk_cancellation_member` FOREIGN KEY (`MemberID`) REFERENCES `Members` (`MemberID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cancellation_ride` FOREIGN KEY (`RideID`) REFERENCES `ActiveRides` (`RideID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `MemberRatings`
--

DROP TABLE IF EXISTS `MemberRatings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MemberRatings` (
  `RideID` varchar(50) NOT NULL,
  `SenderMemberID` int NOT NULL,
  `ReceiverMemberID` int NOT NULL,
  `Rating` decimal(2,1) NOT NULL,
  `RatingComment` varchar(500) DEFAULT NULL,
  `RatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`RideID`,`SenderMemberID`,`ReceiverMemberID`),
  KEY `fk_memberrating_sender` (`SenderMemberID`),
  KEY `fk_memberrating_receiver` (`ReceiverMemberID`),
  CONSTRAINT `fk_memberrating_receiver` FOREIGN KEY (`ReceiverMemberID`) REFERENCES `Members` (`MemberID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_memberrating_sender` FOREIGN KEY (`SenderMemberID`) REFERENCES `Members` (`MemberID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `MemberRatings_chk_1` CHECK (((`Rating` >= 1.0) and (`Rating` <= 5.0)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `MemberStats`
--

DROP TABLE IF EXISTS `MemberStats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MemberStats` (
  `MemberID` int NOT NULL,
  `AverageRating` decimal(3,2) NOT NULL DEFAULT '0.00',
  `TotalRidesTaken` int NOT NULL DEFAULT '0',
  `TotalRidesHosted` int NOT NULL DEFAULT '0',
  `NumberOfRatings` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`MemberID`),
  CONSTRAINT `fk_stats_member` FOREIGN KEY (`MemberID`) REFERENCES `Members` (`MemberID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Members`
--

DROP TABLE IF EXISTS `Members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Members` (
  `MemberID` int NOT NULL AUTO_INCREMENT,
  `FullName` varchar(100) NOT NULL,
  `ProfileImageURL` varchar(255) DEFAULT 'default_avatar.png',
  `Programme` varchar(50) NOT NULL,
  `Branch` varchar(50) DEFAULT NULL,
  `BatchYear` year NOT NULL,
  `Email` varchar(100) NOT NULL,
  `ContactNumber` varchar(15) NOT NULL,
  `Age` int DEFAULT NULL,
  `Gender` char(1) DEFAULT NULL,
  PRIMARY KEY (`MemberID`),
  UNIQUE KEY `Email` (`Email`),
  UNIQUE KEY `ContactNumber` (`ContactNumber`)
) ENGINE=InnoDB AUTO_INCREMENT=28498468 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `MessageHistory`
--

DROP TABLE IF EXISTS `MessageHistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MessageHistory` (
  `MessageID` int NOT NULL AUTO_INCREMENT,
  `RideID` varchar(50) NOT NULL,
  `SenderID` int NOT NULL,
  `MessageText` text NOT NULL,
  `Timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `IsRead` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`MessageID`),
  KEY `fk_message_ride` (`RideID`),
  KEY `fk_message_sender` (`SenderID`),
  CONSTRAINT `fk_message_ride` FOREIGN KEY (`RideID`) REFERENCES `ActiveRides` (`RideID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_message_sender` FOREIGN KEY (`SenderID`) REFERENCES `Members` (`MemberID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `Rahul`
--

DROP TABLE IF EXISTS `Rahul`;
/*!50001 DROP VIEW IF EXISTS `Rahul`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `Rahul` AS SELECT 
 1 AS `VehicleID`,
 1 AS `VehicleType`,
 1 AS `MaxCapacity`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `RideFeedback`
--

DROP TABLE IF EXISTS `RideFeedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `RideFeedback` (
  `RideID` varchar(50) NOT NULL,
  `MemberID` int NOT NULL,
  `FeedbackText` text NOT NULL,
  `FeedbackCategory` varchar(50) DEFAULT NULL,
  `SubmittedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`RideID`),
  KEY `fk_feedback_member` (`MemberID`),
  CONSTRAINT `fk_feedback_member` FOREIGN KEY (`MemberID`) REFERENCES `Members` (`MemberID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `RideHistory`
--

DROP TABLE IF EXISTS `RideHistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `RideHistory` (
  `RideID` varchar(50) NOT NULL,
  `AdminID` int NOT NULL,
  `RideDate` date NOT NULL,
  `StartTime` time NOT NULL,
  `Source` varchar(100) NOT NULL,
  `Destination` varchar(100) NOT NULL,
  `Platform` varchar(30) NOT NULL,
  `Price` int NOT NULL,
  `FemaleOnly` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`RideID`),
  KEY `fk_ridehistory_admin` (`AdminID`),
  CONSTRAINT `fk_ridehistory_admin` FOREIGN KEY (`AdminID`) REFERENCES `Members` (`MemberID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `RidePassengerMap`
--

DROP TABLE IF EXISTS `RidePassengerMap`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `RidePassengerMap` (
  `RideID` varchar(50) NOT NULL,
  `PassengerID` int NOT NULL,
  `IsConfirmed` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`RideID`,`PassengerID`),
  KEY `fk_ridemap_passenger` (`PassengerID`),
  CONSTRAINT `fk_ridemap_passenger` FOREIGN KEY (`PassengerID`) REFERENCES `Members` (`MemberID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_ridemap_ride` FOREIGN KEY (`RideID`) REFERENCES `ActiveRides` (`RideID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Vehicles`
--

DROP TABLE IF EXISTS `Vehicles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Vehicles` (
  `VehicleID` int NOT NULL AUTO_INCREMENT,
  `VehicleType` varchar(30) NOT NULL,
  `MaxCapacity` int NOT NULL,
  PRIMARY KEY (`VehicleID`),
  CONSTRAINT `Vehicles_chk_1` CHECK ((`MaxCapacity` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Final view structure for view `Rahul`
--

/*!50001 DROP VIEW IF EXISTS `Rahul`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `Rahul` AS select `Vehicles`.`VehicleID` AS `VehicleID`,`Vehicles`.`VehicleType` AS `VehicleType`,`Vehicles`.`MaxCapacity` AS `MaxCapacity` from `Vehicles` where (`Vehicles`.`MaxCapacity` >= 3) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-16  6:30:53
