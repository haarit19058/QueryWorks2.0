-- Table structure for table `ActiveRides`
--
DROP TABLE IF EXISTS `ActiveRides`;

/*!40101 SET @saved_cs_client     = @@character_set_client */;

/*!50503 SET character_set_client = utf8mb4 */;

CREATE TABLE
  `ActiveRides` (
    `RideID` varchar(50) NOT NULL,
    `AdminID` int NOT NULL,
    `AvailableSeats` int NOT NULL,
    `PassengerCount` int NOT NULL DEFAULT '1',
    `Source` varchar(100) NOT NULL,
    `Destination` varchar(100) NOT NULL,
    `VehicleType` varchar(30) NOT NULL,
    `StartTime` datetime NOT NULL,
    `EstimatedTime` int NOT NULL,
    `FemaleOnly` tinyint (1) DEFAULT '0',
    `Status` varchar(20) NOT NULL DEFAULT 'ACTIVE',
    PRIMARY KEY (`RideID`),
    KEY `fk_activeride_admin` (`AdminID`),
    CONSTRAINT `fk_activeride_admin` FOREIGN KEY (`AdminID`) REFERENCES `Members` (`MemberID`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `ActiveRides_chk_1` CHECK ((`AvailableSeats` >= 0)),
    CONSTRAINT `ActiveRides_chk_2` CHECK ((`PassengerCount` >= 1))
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ActiveRides`
--
LOCK TABLES `ActiveRides` WRITE;

/*!40000 ALTER TABLE `ActiveRides` DISABLE KEYS */;

INSERT INTO
  `ActiveRides`
VALUES
  (
    '19487c13-c598-46ec-aa3c-407a1bf05669',
    28498490,
    4,
    1,
    'IIT Gandhinagar, Acad Block Path, - 382019, GJ, India',
    'Sector 10, Gurgaon - 120001, HR, India',
    'Car',
    '2026-04-02 02:29:00',
    50,
    1,
    'ACTIVE'
  ),
  (
    '4d54af73-b35e-4410-b352-f3eb42ebf559',
    28498438,
    0,
    6,
    'Ahmedabad Railway Station',
    'Gift City',
    'SUV Cab',
    '2026-02-16 04:03:11',
    56,
    0,
    'ACTIVE'
  ),
  (
    '553aced0-6547-41e5-9aaa-26ddf8e769ed',
    28498442,
    1,
    6,
    'IIT Gandhinagar (Palaj)',
    'Gift City',
    'Premium SUV',
    '2026-02-15 06:03:11',
    71,
    1,
    'ACTIVE'
  ),
  (
    '6e0180e5-20d9-4e12-872f-f6b45ef5cd82',
    28498446,
    0,
    1,
    'IIT Gandhinagar (Palaj)',
    'PVR Motera',
    'Bike',
    '2026-02-16 15:03:11',
    81,
    0,
    'ACTIVE'
  ),
  (
    '6f179c80-7958-4a77-b0fb-00d61de45087',
    28498445,
    0,
    1,
    'Gift City',
    'IIT Gandhinagar (Palaj)',
    'Bike',
    '2026-02-16 19:03:11',
    88,
    1,
    'ACTIVE'
  ),
  (
    '7262c937-95e9-4526-9efc-1d2d65db305c',
    28498445,
    1,
    2,
    'SVPI Airport',
    'PVR Motera',
    'Auto Rickshaw',
    '2026-02-16 18:03:11',
    55,
    0,
    'ACTIVE'
  ),
  (
    '7dad019c-c58d-42db-be4f-9d7d794b57ed',
    28498464,
    0,
    3,
    'Gift City',
    'IIT Gandhinagar (Palaj)',
    'Auto Rickshaw',
    '2026-02-16 13:03:11',
    56,
    0,
    'ACTIVE'
  ),
  (
    '9735ef94-75bf-49ed-bb07-953d50455b23',
    28498438,
    1,
    3,
    'IIT Gandhinagar (Palaj)',
    'Ahmedabad Railway Station',
    'Mini Cab',
    '2026-02-16 06:03:11',
    68,
    0,
    'ACTIVE'
  ),
  (
    'a1287b4e-2a85-444b-9813-c5a4759cce8c',
    28498439,
    0,
    3,
    'IIT Gandhinagar (Palaj)',
    'Kudasan',
    'Auto Rickshaw',
    '2026-02-16 21:03:11',
    62,
    1,
    'ACTIVE'
  ),
  (
    'b673fea0-b774-41f3-9e76-2846183a7467',
    28498465,
    1,
    3,
    'IIT Gandhinagar (Palaj)',
    'PVR Motera',
    'Sedan Cab',
    '2026-02-15 19:03:11',
    82,
    0,
    'ACTIVE'
  ),
  (
    'b6facd13-306b-4a00-9ef0-da8c342217a1',
    28498449,
    0,
    6,
    'SVPI Airport',
    'PVR Motera',
    'SUV Cab',
    '2026-02-16 17:03:11',
    33,
    0,
    'ACTIVE'
  ),
  (
    'b83d9c8b-0278-4a57-9ba7-4b9673550776',
    28498459,
    3,
    3,
    'IIT Gandhinagar (Palaj)',
    'PVR Motera',
    'SUV Cab',
    '2026-02-15 09:03:11',
    39,
    1,
    'ACTIVE'
  ),
  (
    'bc1f49d4-f927-4adf-97a8-86c33187bf44',
    28498459,
    2,
    1,
    'IIT Gandhinagar (Palaj)',
    'SG Highway',
    'Auto Rickshaw',
    '2026-02-16 05:03:11',
    55,
    0,
    'ACTIVE'
  ),
  (
    'c409227a-e96e-4444-8749-15c2bd03d2ae',
    28498455,
    0,
    6,
    'Infocity',
    'Gift City',
    'SUV Cab',
    '2026-02-15 19:03:11',
    38,
    0,
    'ACTIVE'
  ),
  (
    'dd1ee643-2f02-4546-977c-bc55fd4b55ea',
    28498463,
    1,
    3,
    'SVPI Airport',
    'IIT Gandhinagar (Palaj)',
    'Mini Cab',
    '2026-02-17 01:03:11',
    74,
    1,
    'ACTIVE'
  ),
  (
    'e8e48b51-43b9-4a88-8254-5fa6859ba6bb',
    28498472,
    1,
    2,
    'Dhandhuka, GJ, India',
    'Vasai-Virar, MH, India',
    'Car',
    '2026-03-22 09:00:00',
    230,
    0,
    'COMPLETING'
  ),
  (
    'f29f6565-5bc4-495a-9878-4b91b3b876c3',
    28498452,
    3,
    1,
    'IIT Gandhinagar (Palaj)',
    'PVR Motera',
    'Sedan Cab',
    '2026-02-16 21:03:11',
    78,
    0,
    'ACTIVE'
  );

/*!40000 ALTER TABLE `ActiveRides` ENABLE KEYS */;

UNLOCK TABLES;

--
-- Table structure for table `BookingRequests`
--
DROP TABLE IF EXISTS `BookingRequests`;

/*!40101 SET @saved_cs_client     = @@character_set_client */;

/*!50503 SET character_set_client = utf8mb4 */;

CREATE TABLE
  `BookingRequests` (
    `RequestID` int NOT NULL AUTO_INCREMENT,
    `RideID` varchar(50) NOT NULL,
    `PassengerID` int NOT NULL,
    `RequestStatus` varchar(20) NOT NULL DEFAULT 'PENDING',
    `RequestedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`RequestID`),
    KEY `fk_booking_ride` (`RideID`),
    KEY `fk_booking_passenger` (`PassengerID`),
    KEY `idx_status` (`RequestStatus`),
    CONSTRAINT `fk_booking_passenger` FOREIGN KEY (`PassengerID`) REFERENCES `Members` (`MemberID`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_booking_ride` FOREIGN KEY (`RideID`) REFERENCES `ActiveRides` (`RideID`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = InnoDB AUTO_INCREMENT = 52 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `BookingRequests`
--
LOCK TABLES `BookingRequests` WRITE;

/*!40000 ALTER TABLE `BookingRequests` DISABLE KEYS */;

INSERT INTO
  `BookingRequests`
VALUES
  (
    1,
    'dd1ee643-2f02-4546-977c-bc55fd4b55ea',
    28498463,
    'PENDING',
    '2026-02-09 08:00:00'
  ),
  (
    2,
    '6e0180e5-20d9-4e12-872f-f6b45ef5cd82',
    28498446,
    'ACCEPTED',
    '2026-02-09 08:10:00'
  ),
  (
    4,
    'c409227a-e96e-4444-8749-15c2bd03d2ae',
    28498455,
    'ACCEPTED',
    '2026-02-09 08:30:00'
  ),
  (
    5,
    '6f179c80-7958-4a77-b0fb-00d61de45087',
    28498445,
    'PENDING',
    '2026-02-09 08:40:00'
  ),
  (
    6,
    'bc1f49d4-f927-4adf-97a8-86c33187bf44',
    28498459,
    'ACCEPTED',
    '2026-02-09 08:50:00'
  ),
  (
    7,
    '9735ef94-75bf-49ed-bb07-953d50455b23',
    28498438,
    'REJECTED',
    '2026-02-09 09:00:00'
  ),
  (
    8,
    '4d54af73-b35e-4410-b352-f3eb42ebf559',
    28498438,
    'PENDING',
    '2026-02-09 09:10:00'
  ),
  (
    10,
    'a1287b4e-2a85-444b-9813-c5a4759cce8c',
    28498439,
    'PENDING',
    '2026-02-09 09:30:00'
  ),
  (
    11,
    'f29f6565-5bc4-495a-9878-4b91b3b876c3',
    28498452,
    'REJECTED',
    '2026-02-09 09:40:00'
  ),
  (
    13,
    'b83d9c8b-0278-4a57-9ba7-4b9673550776',
    28498459,
    'PENDING',
    '2026-02-09 10:00:00'
  ),
  (
    14,
    '553aced0-6547-41e5-9aaa-26ddf8e769ed',
    28498442,
    'ACCEPTED',
    '2026-02-09 10:10:00'
  ),
  (
    15,
    '7dad019c-c58d-42db-be4f-9d7d794b57ed',
    28498464,
    'REJECTED',
    '2026-02-09 10:20:00'
  ),
  (
    16,
    '7262c937-95e9-4526-9efc-1d2d65db305c',
    28498445,
    'PENDING',
    '2026-02-12 08:00:00'
  ),
  (
    17,
    'b6facd13-306b-4a00-9ef0-da8c342217a1',
    28498449,
    'ACCEPTED',
    '2026-02-12 08:10:00'
  ),
  (
    20,
    'b673fea0-b774-41f3-9e76-2846183a7467',
    28498465,
    'ACCEPTED',
    '2026-02-12 08:40:00'
  ),
  (
    24,
    '7262c937-95e9-4526-9efc-1d2d65db305c',
    28498468,
    'PENDING',
    '2026-03-21 13:55:28'
  ),
  (
    49,
    '553aced0-6547-41e5-9aaa-26ddf8e769ed',
    28498489,
    'PENDING',
    '2026-03-28 16:36:12'
  );

/*!40000 ALTER TABLE `BookingRequests` ENABLE KEYS */;

UNLOCK TABLES;

--
-- Table structure for table `Cancellation`
--
DROP TABLE IF EXISTS `Cancellation`;

/*!40101 SET @saved_cs_client     = @@character_set_client */;

/*!50503 SET character_set_client = utf8mb4 */;

CREATE TABLE
  `Cancellation` (
    `CancellationID` int NOT NULL AUTO_INCREMENT,
    `RideID` varchar(50) NOT NULL,
    `MemberID` int NOT NULL,
    `CancellationReason` varchar(255) NOT NULL,
    PRIMARY KEY (`CancellationID`),
    KEY `fk_cancellation_ride` (`RideID`),
    KEY `fk_cancellation_member` (`MemberID`),
    CONSTRAINT `fk_cancellation_member` FOREIGN KEY (`MemberID`) REFERENCES `Members` (`MemberID`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = InnoDB AUTO_INCREMENT = 9 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Cancellation`
--
LOCK TABLES `Cancellation` WRITE;

/*!40000 ALTER TABLE `Cancellation` DISABLE KEYS */;

INSERT INTO
  `Cancellation`
VALUES
  (
    1,
    'a1287b4e-2a85-444b-9813-c5a4759cce8c',
    28498454,
    'Bad co passengers'
  ),
  (
    2,
    '351d6041-9b8f-4b93-b3c8-613788d14dbe',
    28498444,
    'Other private reasons'
  ),
  (
    4,
    '7dad019c-c58d-42db-be4f-9d7d794b57ed',
    28498443,
    'Plan Changed'
  );

/*!40000 ALTER TABLE `Cancellation` ENABLE KEYS */;

UNLOCK TABLES;

--
-- Table structure for table `MemberRatings`
--
DROP TABLE IF EXISTS `MemberRatings`;

/*!40101 SET @saved_cs_client     = @@character_set_client */;

/*!50503 SET character_set_client = utf8mb4 */;

CREATE TABLE
  `MemberRatings` (
    `RideID` varchar(50) NOT NULL,
    `SenderMemberID` int NOT NULL,
    `ReceiverMemberID` int NOT NULL,
    `Rating` decimal(2, 1) NOT NULL,
    `RatingComment` varchar(500) DEFAULT NULL,
    `RatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`RideID`, `SenderMemberID`, `ReceiverMemberID`),
    KEY `fk_memberrating_sender` (`SenderMemberID`),
    KEY `fk_memberrating_receiver` (`ReceiverMemberID`),
    CONSTRAINT `fk_memberrating_receiver` FOREIGN KEY (`ReceiverMemberID`) REFERENCES `Members` (`MemberID`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_memberrating_sender` FOREIGN KEY (`SenderMemberID`) REFERENCES `Members` (`MemberID`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `MemberRatings_chk_1` CHECK (
      (
        (`Rating` >= 1.0)
        and (`Rating` <= 5.0)
      )
    )
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MemberRatings`
--
LOCK TABLES `MemberRatings` WRITE;

/*!40000 ALTER TABLE `MemberRatings` DISABLE KEYS */;

INSERT INTO
  `MemberRatings`
VALUES
  (
    '0e255964-65fb-4e26-955c-beb69785393b',
    28498442,
    28498451,
    3.8,
    'Great ride, very smooth!',
    '2026-02-15 01:24:17'
  ),
  (
    '0e255964-65fb-4e26-955c-beb69785393b',
    28498457,
    28498449,
    3.0,
    'Ride was fine, nothing to complain about.',
    '2026-02-15 01:24:17'
  ),
  (
    '0e255964-65fb-4e26-955c-beb69785393b',
    28498457,
    28498459,
    4.8,
    'Good communication and coordination.',
    '2026-02-15 01:24:17'
  ),
  (
    '152056fd-7799-4aab-8156-c216eb76f0c3',
    28498450,
    28498462,
    3.8,
    'Pleasant trip, no issues.',
    '2026-02-15 01:24:17'
  ),
  (
    '152056fd-7799-4aab-8156-c216eb76f0c3',
    28498458,
    28498459,
    3.3,
    'Driver was punctual and polite.',
    '2026-02-15 01:24:17'
  ),
  (
    '152056fd-7799-4aab-8156-c216eb76f0c3',
    28498462,
    28498451,
    3.3,
    'Good communication and coordination.',
    '2026-02-15 01:24:17'
  ),
  (
    '17bcba21-075c-49c6-8574-47214519b2e1',
    28498445,
    28498464,
    3.6,
    'Clean car and comfortable journey.',
    '2026-02-15 01:24:17'
  ),
  (
    '17bcba21-075c-49c6-8574-47214519b2e1',
    28498460,
    28498454,
    4.9,
    'Great ride, very smooth!',
    '2026-02-15 01:24:17'
  ),
  (
    '17bcba21-075c-49c6-8574-47214519b2e1',
    28498466,
    28498467,
    4.8,
    'Clean car and comfortable journey.',
    '2026-02-15 01:24:17'
  ),
  (
    '1bea2983-7e49-4705-a8a9-36f467fd0873',
    28498447,
    28498465,
    3.8,
    'Nice experience overall.',
    '2026-02-15 01:24:17'
  ),
  (
    '1bea2983-7e49-4705-a8a9-36f467fd0873',
    28498462,
    28498459,
    4.8,
    'Pleasant trip, no issues.',
    '2026-02-15 01:24:17'
  ),
  (
    '1bea2983-7e49-4705-a8a9-36f467fd0873',
    28498465,
    28498457,
    4.1,
    'Pleasant trip, no issues.',
    '2026-02-15 01:24:17'
  ),
  (
    '1fd3e50d-c543-4110-ba47-7144a7321122',
    28498445,
    28498446,
    3.0,
    'Friendly and cooperative member.',
    '2026-02-15 01:24:17'
  ),
  (
    '1fd3e50d-c543-4110-ba47-7144a7321122',
    28498456,
    28498459,
    4.1,
    'Pleasant trip, no issues.',
    '2026-02-15 01:24:17'
  ),
  (
    '1fd3e50d-c543-4110-ba47-7144a7321122',
    28498463,
    28498439,
    4.6,
    'Clean car and comfortable journey.',
    '2026-02-15 01:24:17'
  ),
  (
    '3357e8ea-a4a9-4f99-9a0a-3643a89d1a51',
    28498445,
    28498446,
    4.5,
    'Great ride, very smooth!',
    '2026-02-15 01:24:17'
  ),
  (
    '3357e8ea-a4a9-4f99-9a0a-3643a89d1a51',
    28498456,
    28498462,
    3.6,
    'Great ride, very smooth!',
    '2026-02-15 01:24:17'
  ),
  (
    '3357e8ea-a4a9-4f99-9a0a-3643a89d1a51',
    28498461,
    28498445,
    4.0,
    'Comfortable ride, would recommend.',
    '2026-02-15 01:24:17'
  ),
  (
    '3a5cad27-a2e5-4f20-a70e-ddea0e82a852',
    28498438,
    28498446,
    3.8,
    'Friendly and cooperative member.',
    '2026-02-15 01:24:17'
  ),
  (
    '3a5cad27-a2e5-4f20-a70e-ddea0e82a852',
    28498449,
    28498448,
    4.4,
    'Good communication and coordination.',
    '2026-02-15 01:24:17'
  ),
  (
    '3a5cad27-a2e5-4f20-a70e-ddea0e82a852',
    28498459,
    28498442,
    3.6,
    'Good communication and coordination.',
    '2026-02-15 01:24:17'
  ),
  (
    '3cc9024d-a7ef-46db-87e7-480fadcfa16d',
    28498439,
    28498441,
    3.2,
    'Pleasant trip, no issues.',
    '2026-02-15 01:24:17'
  ),
  (
    '3cc9024d-a7ef-46db-87e7-480fadcfa16d',
    28498443,
    28498465,
    4.3,
    'Comfortable ride, would recommend.',
    '2026-02-15 01:24:17'
  ),
  (
    '3cc9024d-a7ef-46db-87e7-480fadcfa16d',
    28498456,
    28498448,
    3.0,
    'Good communication and coordination.',
    '2026-02-15 01:24:17'
  ),
  (
    '4515709e-df3f-4f01-829c-9bfa6aac3af7',
    28498448,
    28498462,
    3.6,
    'Nice experience overall.',
    '2026-02-15 01:24:17'
  ),
  (
    '4515709e-df3f-4f01-829c-9bfa6aac3af7',
    28498456,
    28498438,
    4.5,
    'Great ride, very smooth!',
    '2026-02-15 01:24:17'
  ),
  (
    '4515709e-df3f-4f01-829c-9bfa6aac3af7',
    28498460,
    28498456,
    4.6,
    'Friendly and cooperative member.',
    '2026-02-15 01:24:17'
  ),
  (
    '458849ce-94ef-4371-bd9b-1c55b9bec9b6',
    28498449,
    28498462,
    4.0,
    'Comfortable ride, would recommend.',
    '2026-02-15 01:24:17'
  ),
  (
    '458849ce-94ef-4371-bd9b-1c55b9bec9b6',
    28498465,
    28498445,
    4.3,
    'Pleasant trip, no issues.',
    '2026-02-15 01:24:17'
  ),
  (
    '458849ce-94ef-4371-bd9b-1c55b9bec9b6',
    28498465,
    28498449,
    3.9,
    'Comfortable ride, would recommend.',
    '2026-02-15 01:24:17'
  ),
  (
    '4675faeb-4be3-40b5-8350-031e9bdfb2da',
    28498468,
    28498474,
    4.0,
    'Good experience',
    '2026-03-22 17:14:05'
  ),
  (
    '480d513c-d0f3-44ae-802c-da1b7b64a87f',
    28498460,
    28498465,
    3.9,
    'Enjoyed the ride, thank you!',
    '2026-02-15 01:24:17'
  ),
  (
    '480d513c-d0f3-44ae-802c-da1b7b64a87f',
    28498462,
    28498448,
    4.3,
    'Ride was fine, nothing to complain about.',
    '2026-02-15 01:24:17'
  ),
  (
    '480d513c-d0f3-44ae-802c-da1b7b64a87f',
    28498464,
    28498447,
    3.7,
    'Nice experience overall.',
    '2026-02-15 01:24:17'
  ),
  (
    '525867bd-3a18-403b-a0bb-601eee3ce3ee',
    28498441,
    28498457,
    4.4,
    'Great ride, very smooth!',
    '2026-02-15 01:24:17'
  ),
  (
    '525867bd-3a18-403b-a0bb-601eee3ce3ee',
    28498443,
    28498440,
    3.5,
    'Nice experience overall.',
    '2026-02-15 01:24:17'
  ),
  (
    '525867bd-3a18-403b-a0bb-601eee3ce3ee',
    28498449,
    28498451,
    4.6,
    'Great ride, very smooth!',
    '2026-02-15 01:24:17'
  ),
  (
    '5f2acb79-ebf8-49ef-8588-dd63706e769a',
    28498438,
    28498444,
    4.7,
    'Friendly and cooperative member.',
    '2026-02-15 01:24:17'
  ),
  (
    '5f2acb79-ebf8-49ef-8588-dd63706e769a',
    28498440,
    28498439,
    3.1,
    'Enjoyed the ride, thank you!',
    '2026-02-15 01:24:17'
  ),
  (
    '5f2acb79-ebf8-49ef-8588-dd63706e769a',
    28498442,
    28498460,
    3.2,
    'Ride was fine, nothing to complain about.',
    '2026-02-15 01:24:17'
  ),
  (
    '62e067d5-5155-4b71-b65f-f7fdc2e1bbf9',
    28498438,
    28498439,
    4.6,
    'Driver was punctual and polite.',
    '2026-02-15 01:24:17'
  ),
  (
    '62e067d5-5155-4b71-b65f-f7fdc2e1bbf9',
    28498458,
    28498442,
    3.6,
    'Good communication and coordination.',
    '2026-02-15 01:24:17'
  ),
  (
    '62e067d5-5155-4b71-b65f-f7fdc2e1bbf9',
    28498459,
    28498462,
    3.5,
    'Comfortable ride, would recommend.',
    '2026-02-15 01:24:17'
  ),
  (
    '66e87cba-96f7-4da4-bc09-eccea50bc882',
    28498468,
    28498489,
    2.0,
    '',
    '2026-04-02 02:51:49'
  ),
  (
    '66e87cba-96f7-4da4-bc09-eccea50bc882',
    28498489,
    28498468,
    5.0,
    '',
    '2026-03-28 16:41:21'
  ),
  (
    '754e06d2-a43b-4b62-8f4e-df9e15593eed',
    28498439,
    28498465,
    4.6,
    'Enjoyed the ride, thank you!',
    '2026-02-15 01:24:17'
  ),
  (
    '754e06d2-a43b-4b62-8f4e-df9e15593eed',
    28498447,
    28498464,
    3.4,
    'Great ride, very smooth!',
    '2026-02-15 01:24:17'
  ),
  (
    '754e06d2-a43b-4b62-8f4e-df9e15593eed',
    28498449,
    28498466,
    4.5,
    'Driver was punctual and polite.',
    '2026-02-15 01:24:17'
  ),
  (
    '766d2473-dc58-413f-a814-8c54c928e701',
    28498439,
    28498440,
    4.5,
    'Pleasant trip, no issues.',
    '2026-02-15 01:24:17'
  ),
  (
    '766d2473-dc58-413f-a814-8c54c928e701',
    28498445,
    28498444,
    3.1,
    'Ride was fine, nothing to complain about.',
    '2026-02-15 01:24:17'
  ),
  (
    '766d2473-dc58-413f-a814-8c54c928e701',
    28498445,
    28498447,
    3.5,
    'Pleasant trip, no issues.',
    '2026-02-15 01:24:17'
  ),
  (
    '78d88260-537c-4439-b175-ff06c4eb0fcd',
    28498438,
    28498463,
    3.4,
    'Ride was fine, nothing to complain about.',
    '2026-02-15 01:24:17'
  ),
  (
    '78d88260-537c-4439-b175-ff06c4eb0fcd',
    28498447,
    28498445,
    3.9,
    'Driver was punctual and polite.',
    '2026-02-15 01:24:17'
  ),
  (
    '78d88260-537c-4439-b175-ff06c4eb0fcd',
    28498467,
    28498452,
    5.0,
    'Driver was punctual and polite.',
    '2026-02-15 01:24:17'
  ),
  (
    '7bafd39b-6e2c-44fb-8b65-373ab4607608',
    28498439,
    28498448,
    3.8,
    'Friendly and cooperative member.',
    '2026-02-15 01:24:17'
  ),
  (
    '7bafd39b-6e2c-44fb-8b65-373ab4607608',
    28498452,
    28498461,
    3.8,
    'Enjoyed the ride, thank you!',
    '2026-02-15 01:24:17'
  ),
  (
    '7bafd39b-6e2c-44fb-8b65-373ab4607608',
    28498452,
    28498464,
    4.1,
    'Great ride, very smooth!',
    '2026-02-15 01:24:17'
  ),
  (
    '8469215d-ac85-4a64-ae88-51ec8a89bc09',
    28498440,
    28498467,
    3.7,
    'Comfortable ride, would recommend.',
    '2026-02-15 01:24:17'
  ),
  (
    '8469215d-ac85-4a64-ae88-51ec8a89bc09',
    28498447,
    28498450,
    4.5,
    'Nice experience overall.',
    '2026-02-15 01:24:17'
  ),
  (
    '8469215d-ac85-4a64-ae88-51ec8a89bc09',
    28498448,
    28498440,
    3.5,
    'Comfortable ride, would recommend.',
    '2026-02-15 01:24:17'
  ),
  (
    '8a668859-41ad-4a2e-baa8-8e9afd0f1061',
    28498447,
    28498440,
    4.9,
    'Comfortable ride, would recommend.',
    '2026-02-15 01:24:17'
  ),
  (
    '8a668859-41ad-4a2e-baa8-8e9afd0f1061',
    28498460,
    28498455,
    3.1,
    'Ride was fine, nothing to complain about.',
    '2026-02-15 01:24:17'
  ),
  (
    '8a668859-41ad-4a2e-baa8-8e9afd0f1061',
    28498467,
    28498464,
    4.7,
    'Comfortable ride, would recommend.',
    '2026-02-15 01:24:17'
  ),
  (
    '8f5dedd8-21b3-4a5d-a1cf-8bd93db74b8c',
    28498447,
    28498444,
    4.2,
    'Good communication and coordination.',
    '2026-02-15 01:24:17'
  ),
  (
    '8f5dedd8-21b3-4a5d-a1cf-8bd93db74b8c',
    28498447,
    28498461,
    4.2,
    'Friendly and cooperative member.',
    '2026-02-15 01:24:17'
  ),
  (
    '8f5dedd8-21b3-4a5d-a1cf-8bd93db74b8c',
    28498465,
    28498438,
    4.5,
    'Enjoyed the ride, thank you!',
    '2026-02-15 01:24:17'
  ),
  (
    '8f7877f9-d082-4046-a9d0-daa413c1bcf8',
    28498438,
    28498453,
    4.0,
    'Driver was punctual and polite.',
    '2026-02-15 01:24:17'
  ),
  (
    '8f7877f9-d082-4046-a9d0-daa413c1bcf8',
    28498445,
    28498439,
    3.2,
    'Good communication and coordination.',
    '2026-02-15 01:24:17'
  ),
  (
    '8f7877f9-d082-4046-a9d0-daa413c1bcf8',
    28498457,
    28498464,
    4.9,
    'Great ride, very smooth!',
    '2026-02-15 01:24:17'
  ),
  (
    '939a2d5e-4b8b-4614-b5a3-c3ac9fd6242f',
    28498450,
    28498465,
    3.0,
    'Enjoyed the ride, thank you!',
    '2026-02-15 01:24:17'
  ),
  (
    '939a2d5e-4b8b-4614-b5a3-c3ac9fd6242f',
    28498453,
    28498454,
    4.4,
    'Ride was fine, nothing to complain about.',
    '2026-02-15 01:24:17'
  ),
  (
    '939a2d5e-4b8b-4614-b5a3-c3ac9fd6242f',
    28498458,
    28498466,
    4.9,
    'Friendly and cooperative member.',
    '2026-02-15 01:24:17'
  ),
  (
    '974ff030-0e5b-4c22-a242-dee141ffe44b',
    28498445,
    28498459,
    4.9,
    'Ride was fine, nothing to complain about.',
    '2026-02-15 01:24:17'
  ),
  (
    '974ff030-0e5b-4c22-a242-dee141ffe44b',
    28498457,
    28498438,
    4.1,
    'Pleasant trip, no issues.',
    '2026-02-15 01:24:17'
  ),
  (
    '974ff030-0e5b-4c22-a242-dee141ffe44b',
    28498463,
    28498467,
    3.9,
    'Nice experience overall.',
    '2026-02-15 01:24:17'
  ),
  (
    '9bd17bb6-2bf9-4245-bae6-5ac56f517ce4',
    28498445,
    28498463,
    4.7,
    'Great ride, very smooth!',
    '2026-02-15 01:24:17'
  ),
  (
    '9bd17bb6-2bf9-4245-bae6-5ac56f517ce4',
    28498451,
    28498445,
    3.9,
    'Ride was fine, nothing to complain about.',
    '2026-02-15 01:24:17'
  ),
  (
    '9bd17bb6-2bf9-4245-bae6-5ac56f517ce4',
    28498454,
    28498460,
    3.1,
    'Enjoyed the ride, thank you!',
    '2026-02-15 01:24:17'
  ),
  (
    '9cdc933e-0676-41ba-ae65-7637db70d3ab',
    28498439,
    28498440,
    4.4,
    'Ride was fine, nothing to complain about.',
    '2026-02-15 01:24:17'
  ),
  (
    '9cdc933e-0676-41ba-ae65-7637db70d3ab',
    28498454,
    28498463,
    4.0,
    'Clean car and comfortable journey.',
    '2026-02-15 01:24:17'
  ),
  (
    '9cdc933e-0676-41ba-ae65-7637db70d3ab',
    28498462,
    28498441,
    3.9,
    'Driver was punctual and polite.',
    '2026-02-15 01:24:17'
  ),
  (
    '9e1bc7fd-a916-4453-a378-017a0e304316',
    28498454,
    28498441,
    4.3,
    'Ride was fine, nothing to complain about.',
    '2026-02-15 01:24:17'
  ),
  (
    '9e1bc7fd-a916-4453-a378-017a0e304316',
    28498458,
    28498459,
    4.0,
    'Driver was punctual and polite.',
    '2026-02-15 01:24:17'
  ),
  (
    '9e1bc7fd-a916-4453-a378-017a0e304316',
    28498460,
    28498467,
    3.1,
    'Clean car and comfortable journey.',
    '2026-02-15 01:24:17'
  ),
  (
    'a8749424-ac53-4119-9b95-6d621d37d052',
    28498440,
    28498463,
    4.7,
    'Ride was fine, nothing to complain about.',
    '2026-02-15 01:24:17'
  ),
  (
    'a8749424-ac53-4119-9b95-6d621d37d052',
    28498447,
    28498448,
    4.4,
    'Enjoyed the ride, thank you!',
    '2026-02-15 01:24:17'
  ),
  (
    'a8749424-ac53-4119-9b95-6d621d37d052',
    28498463,
    28498460,
    3.1,
    'Good communication and coordination.',
    '2026-02-15 01:24:17'
  ),
  (
    'b3b7e197-41bd-442c-b30e-94d2ed874009',
    28498439,
    28498459,
    4.2,
    'Enjoyed the ride, thank you!',
    '2026-02-15 01:24:17'
  ),
  (
    'b3b7e197-41bd-442c-b30e-94d2ed874009',
    28498442,
    28498461,
    4.6,
    'Enjoyed the ride, thank you!',
    '2026-02-15 01:24:17'
  ),
  (
    'b3b7e197-41bd-442c-b30e-94d2ed874009',
    28498456,
    28498444,
    3.3,
    'Friendly and cooperative member.',
    '2026-02-15 01:24:17'
  ),
  (
    'b539a100-4699-41d7-bc48-892b1d89bad2',
    28498444,
    28498463,
    4.0,
    'Nice experience overall.',
    '2026-02-15 01:24:17'
  ),
  (
    'b539a100-4699-41d7-bc48-892b1d89bad2',
    28498454,
    28498438,
    4.8,
    'Clean car and comfortable journey.',
    '2026-02-15 01:24:17'
  ),
  (
    'b539a100-4699-41d7-bc48-892b1d89bad2',
    28498454,
    28498447,
    3.5,
    'Nice experience overall.',
    '2026-02-15 01:24:17'
  ),
  (
    'bda24468-ca06-4713-988e-2f9e2cdaa500',
    28498450,
    28498448,
    4.4,
    'Friendly and cooperative member.',
    '2026-02-15 01:24:17'
  ),
  (
    'bda24468-ca06-4713-988e-2f9e2cdaa500',
    28498458,
    28498457,
    3.2,
    'Great ride, very smooth!',
    '2026-02-15 01:24:17'
  ),
  (
    'bda24468-ca06-4713-988e-2f9e2cdaa500',
    28498466,
    28498464,
    4.8,
    'Great ride, very smooth!',
    '2026-02-15 01:24:17'
  ),
  (
    'cf56023f-de0e-4c63-9db6-bbbd554d452b',
    28498447,
    28498448,
    3.4,
    'Comfortable ride, would recommend.',
    '2026-02-15 01:24:17'
  ),
  (
    'cf56023f-de0e-4c63-9db6-bbbd554d452b',
    28498450,
    28498447,
    4.9,
    'Pleasant trip, no issues.',
    '2026-02-15 01:24:17'
  ),
  (
    'cf56023f-de0e-4c63-9db6-bbbd554d452b',
    28498467,
    28498464,
    3.2,
    'Nice experience overall.',
    '2026-02-15 01:24:17'
  ),
  (
    'cf97d981-4613-4bac-971e-e6865052db20',
    28498445,
    28498449,
    4.8,
    'Clean car and comfortable journey.',
    '2026-02-15 01:24:17'
  ),
  (
    'cf97d981-4613-4bac-971e-e6865052db20',
    28498448,
    28498440,
    3.0,
    'Ride was fine, nothing to complain about.',
    '2026-02-15 01:24:17'
  ),
  (
    'cf97d981-4613-4bac-971e-e6865052db20',
    28498466,
    28498461,
    5.0,
    'Good communication and coordination.',
    '2026-02-15 01:24:17'
  ),
  (
    'd0f95a70-14c5-4c70-914b-b12771c1098a',
    28498457,
    28498441,
    3.5,
    'Nice experience overall.',
    '2026-02-15 01:24:17'
  ),
  (
    'd0f95a70-14c5-4c70-914b-b12771c1098a',
    28498458,
    28498465,
    4.5,
    'Clean car and comfortable journey.',
    '2026-02-15 01:24:17'
  ),
  (
    'd0f95a70-14c5-4c70-914b-b12771c1098a',
    28498467,
    28498464,
    4.9,
    'Driver was punctual and polite.',
    '2026-02-15 01:24:17'
  ),
  (
    'ded92a7a-cb50-4381-8926-2be10b4c45ca',
    28498451,
    28498465,
    3.6,
    'Good communication and coordination.',
    '2026-02-15 01:24:17'
  ),
  (
    'ded92a7a-cb50-4381-8926-2be10b4c45ca',
    28498456,
    28498444,
    3.4,
    'Nice experience overall.',
    '2026-02-15 01:24:17'
  ),
  (
    'ded92a7a-cb50-4381-8926-2be10b4c45ca',
    28498458,
    28498448,
    4.3,
    'Enjoyed the ride, thank you!',
    '2026-02-15 01:24:17'
  ),
  (
    'e4006a76-2154-4b20-ab75-7e2e8184c837',
    28498443,
    28498461,
    3.3,
    'Nice experience overall.',
    '2026-02-15 01:24:17'
  ),
  (
    'e4006a76-2154-4b20-ab75-7e2e8184c837',
    28498459,
    28498444,
    3.6,
    'Nice experience overall.',
    '2026-02-15 01:24:17'
  ),
  (
    'e4006a76-2154-4b20-ab75-7e2e8184c837',
    28498460,
    28498452,
    4.5,
    'Ride was fine, nothing to complain about.',
    '2026-02-15 01:24:17'
  ),
  (
    'e50d3163-58e1-4708-a621-efafef1425d6',
    28498455,
    28498458,
    4.7,
    'Pleasant trip, no issues.',
    '2026-02-15 01:24:17'
  ),
  (
    'e50d3163-58e1-4708-a621-efafef1425d6',
    28498457,
    28498465,
    4.1,
    'Comfortable ride, would recommend.',
    '2026-02-15 01:24:17'
  ),
  (
    'e50d3163-58e1-4708-a621-efafef1425d6',
    28498462,
    28498448,
    4.4,
    'Clean car and comfortable journey.',
    '2026-02-15 01:24:17'
  ),
  (
    'e83d295e-e4ef-48f1-aca2-ae62debe3381',
    28498444,
    28498442,
    4.3,
    'Enjoyed the ride, thank you!',
    '2026-02-15 01:24:17'
  ),
  (
    'e83d295e-e4ef-48f1-aca2-ae62debe3381',
    28498458,
    28498441,
    4.7,
    'Comfortable ride, would recommend.',
    '2026-02-15 01:24:17'
  ),
  (
    'e83d295e-e4ef-48f1-aca2-ae62debe3381',
    28498459,
    28498464,
    3.9,
    'Pleasant trip, no issues.',
    '2026-02-15 01:24:17'
  ),
  (
    'e98af64b-0dd8-4ae5-90db-063445fb203a',
    28498445,
    28498442,
    4.8,
    'Ride was fine, nothing to complain about.',
    '2026-02-15 01:24:17'
  ),
  (
    'e98af64b-0dd8-4ae5-90db-063445fb203a',
    28498445,
    28498450,
    4.5,
    'Friendly and cooperative member.',
    '2026-02-15 01:24:17'
  ),
  (
    'e98af64b-0dd8-4ae5-90db-063445fb203a',
    28498456,
    28498454,
    4.7,
    'Great ride, very smooth!',
    '2026-02-15 01:24:17'
  ),
  (
    'f45f8311-e93f-4eba-b0a1-caa4ca41f858',
    28498443,
    28498452,
    3.9,
    'Clean car and comfortable journey.',
    '2026-02-15 01:24:17'
  ),
  (
    'f45f8311-e93f-4eba-b0a1-caa4ca41f858',
    28498448,
    28498458,
    4.1,
    'Good communication and coordination.',
    '2026-02-15 01:24:17'
  ),
  (
    'f45f8311-e93f-4eba-b0a1-caa4ca41f858',
    28498456,
    28498465,
    4.9,
    'Good communication and coordination.',
    '2026-02-15 01:24:17'
  );

/*!40000 ALTER TABLE `MemberRatings` ENABLE KEYS */;

UNLOCK TABLES;

--
-- Table structure for table `MemberStats`
--
DROP TABLE IF EXISTS `MemberStats`;

/*!40101 SET @saved_cs_client     = @@character_set_client */;

/*!50503 SET character_set_client = utf8mb4 */;

CREATE TABLE
  `MemberStats` (
    `MemberID` int NOT NULL,
    `AverageRating` decimal(3, 2) NOT NULL DEFAULT '0.00',
    `TotalRidesTaken` int NOT NULL DEFAULT '0',
    `TotalRidesHosted` int NOT NULL DEFAULT '0',
    `NumberOfRatings` int NOT NULL DEFAULT '0',
    PRIMARY KEY (`MemberID`),
    CONSTRAINT `fk_stats_member` FOREIGN KEY (`MemberID`) REFERENCES `Members` (`MemberID`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MemberStats`
--
LOCK TABLES `MemberStats` WRITE;

/*!40000 ALTER TABLE `MemberStats` DISABLE KEYS */;

INSERT INTO
  `MemberStats`
VALUES
  (28498438, 3.43, 99, 1, 198),
  (28498439, 4.67, 73, 54, 146),
  (28498440, 3.06, 76, 1, 152),
  (28498441, 3.24, 100, 99, 200),
  (28498442, 2.00, 104, 64, 208),
  (28498443, 2.25, 52, 33, 104),
  (28498444, 3.59, 103, 49, 206),
  (28498445, 4.53, 73, 6, 146),
  (28498446, 1.24, 104, 36, 208),
  (28498447, 1.26, 131, 75, 262),
  (28498448, 1.51, 169, 88, 338),
  (28498449, 2.83, 65, 38, 130),
  (28498450, 4.13, 138, 73, 276),
  (28498451, 3.75, 116, 96, 232),
  (28498452, 1.49, 102, 44, 204),
  (28498453, 2.38, 125, 57, 250),
  (28498454, 2.87, 74, 2, 148),
  (28498455, 4.69, 67, 64, 134),
  (28498456, 2.18, 108, 35, 216),
  (28498457, 1.62, 79, 46, 158),
  (28498458, 1.27, 35, 25, 70),
  (28498459, 3.86, 97, 49, 194),
  (28498460, 3.28, 98, 96, 196),
  (28498461, 2.66, 70, 2, 140),
  (28498462, 1.79, 46, 23, 92),
  (28498463, 1.63, 70, 47, 140),
  (28498464, 3.52, 131, 60, 262),
  (28498465, 3.71, 44, 38, 88),
  (28498466, 3.72, 164, 68, 328),
  (28498467, 3.17, 132, 66, 264),
  (28498468, 4.00, 4, 3, 3),
  (28498474, 4.00, 1, 1, 1),
  (28498489, 2.00, 1, 1, 1),
  (28498490, 0.00, 0, 1, 0);

/*!40000 ALTER TABLE `MemberStats` ENABLE KEYS */;

UNLOCK TABLES;

--
-- Table structure for table `Members`
--
DROP TABLE IF EXISTS `Members`;

/*!40101 SET @saved_cs_client     = @@character_set_client */;

/*!50503 SET character_set_client = utf8mb4 */;

CREATE TABLE
  `Members` (
    `MemberID` int NOT NULL AUTO_INCREMENT,
    `GoogleSub` varchar(255) NOT NULL,
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
    UNIQUE KEY `GoogleSub` (`GoogleSub`),
    UNIQUE KEY `Email` (`Email`),
    UNIQUE KEY `ContactNumber` (`ContactNumber`),
    KEY `idx_email` (`Email`)
  ) ENGINE = InnoDB AUTO_INCREMENT = 28498491 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Members`
--
LOCK TABLES `Members` WRITE;

/*!40000 ALTER TABLE `Members` DISABLE KEYS */;

INSERT INTO
  `Members`
VALUES
  (
    28498438,
    'dummy_sub_28498438',
    'Myra Khan',
    'https://robohash.org/28498438.png?set=set4',
    'M.Tech.',
    'Computer Science and Engineering',
    2029,
    'myra.khan@iitgn.ac.in',
    '6371872528',
    22,
    'F'
  ),
  (
    28498439,
    'dummy_sub_28498439',
    'Anaya Mehta',
    'https://robohash.org/28498439.png?set=set4',
    'M.Tech.',
    'Integrated Circuit Design and Technology',
    2029,
    'anaya.mehta@iitgn.ac.in',
    '6157043256',
    24,
    'F'
  ),
  (
    28498440,
    'dummy_sub_28498440',
    'Ayaan Nair',
    'https://robohash.org/28498440.png?set=set4',
    'PhD',
    'Artificial Intelligence',
    2026,
    'ayaan.nair@iitgn.ac.in',
    '9965758745',
    29,
    'M'
  ),
  (
    28498441,
    'dummy_sub_28498441',
    'Kiara Singh',
    'https://robohash.org/28498441.png?set=set4',
    'B.Tech.-M.Tech. Dual Degree',
    'Artificial Intelligence',
    2028,
    'kiara.singh@iitgn.ac.in',
    '9146086242',
    22,
    'F'
  ),
  (
    28498442,
    'dummy_sub_28498442',
    'Arjun Mishra',
    'https://robohash.org/28498442.png?set=set4',
    'B.Tech.',
    'Computer Science and Engineering',
    2029,
    'arjun.mishra@iitgn.ac.in',
    '9036360323',
    23,
    'M'
  ),
  (
    28498443,
    'dummy_sub_28498443',
    'Aadhya Yadav',
    'https://robohash.org/28498443.png?set=set4',
    'PhD',
    'Physics',
    2031,
    'aadhya.yadav@iitgn.ac.in',
    '8957796664',
    31,
    'F'
  ),
  (
    28498444,
    'dummy_sub_28498444',
    'Aadhya Mishra',
    'https://robohash.org/28498444.png?set=set4',
    'PhD',
    'Mechanical Engineering',
    2029,
    'aadhya.mishra@iitgn.ac.in',
    '6977276542',
    24,
    'F'
  ),
  (
    28498445,
    'dummy_sub_28498445',
    'Shanaya Khan',
    'https://robohash.org/28498445.png?set=set4',
    'PhD',
    'Design',
    2030,
    'shanaya.khan@iitgn.ac.in',
    '7127783953',
    30,
    'F'
  ),
  (
    28498446,
    'dummy_sub_28498446',
    'Ishaan Chaudhary',
    'https://robohash.org/28498446.png?set=set4',
    'B.Tech.',
    'Computer Science and Engineering',
    2026,
    'ishaan.chaudhary@iitgn.ac.in',
    '8938941125',
    18,
    'M'
  ),
  (
    28498447,
    'dummy_sub_28498447',
    'Kiaan Khan',
    'https://robohash.org/28498447.png?set=set4',
    'B.Tech.-M.Tech. Dual Degree',
    'Mechanical Engineering',
    2026,
    'kiaan.khan@iitgn.ac.in',
    '8955939794',
    22,
    'M'
  ),
  (
    28498448,
    'dummy_sub_28498448',
    'Inaaya Shah',
    'https://robohash.org/28498448.png?set=set4',
    'B.Tech.',
    'Integrated Circuit Design & Technology',
    2030,
    'inaaya.shah@iitgn.ac.in',
    '6083558530',
    18,
    'F'
  ),
  (
    28498449,
    'dummy_sub_28498449',
    'Aadhya Sharma',
    'https://robohash.org/28498449.png?set=set4',
    'PhD',
    'Design',
    2030,
    'aadhya.sharma@iitgn.ac.in',
    '9167768520',
    28,
    'F'
  ),
  (
    28498450,
    'dummy_sub_28498450',
    'Diya Rao',
    'https://robohash.org/28498450.png?set=set4',
    'PhD',
    'Design',
    2030,
    'diya.rao@iitgn.ac.in',
    '7685045165',
    26,
    'F'
  ),
  (
    28498451,
    'dummy_sub_28498451',
    'Diya Iyer',
    'https://robohash.org/28498451.png?set=set4',
    'PhD',
    'Humanities & Social Sciences',
    2026,
    'diya.iyer@iitgn.ac.in',
    '7992992383',
    35,
    'F'
  ),
  (
    28498452,
    'dummy_sub_28498452',
    'Ishaan Reddy',
    'https://robohash.org/28498452.png?set=set4',
    'M.Tech.',
    'Computer Science and Engineering',
    2029,
    'ishaan.reddy@iitgn.ac.in',
    '7440844189',
    23,
    'M'
  ),
  (
    28498453,
    'dummy_sub_28498453',
    'Diya Sharma',
    'https://robohash.org/28498453.png?set=set4',
    'PhD',
    'Electrical Engineering',
    2026,
    'diya.sharma@iitgn.ac.in',
    '6832443945',
    24,
    'F'
  ),
  (
    28498454,
    'dummy_sub_28498454',
    'Aadhya Khan',
    'https://robohash.org/28498454.png?set=set4',
    'B.Tech.-M.Tech. Dual Degree',
    'Computer Science and Engineering',
    2028,
    'aadhya.khan@iitgn.ac.in',
    '7467612805',
    20,
    'F'
  ),
  (
    28498455,
    'dummy_sub_28498455',
    'Reyansh Reddy',
    'https://robohash.org/28498455.png?set=set4',
    'B.Tech.-M.Tech. Dual Degree',
    'Integrated Circuit Design & Technology',
    2027,
    'reyansh.reddy@iitgn.ac.in',
    '7336558203',
    19,
    'M'
  ),
  (
    28498456,
    'dummy_sub_28498456',
    'Vihaan Kumar',
    'https://robohash.org/28498456.png?set=set4',
    'PhD',
    'Design',
    2027,
    'vihaan.kumar@iitgn.ac.in',
    '8456766208',
    26,
    'M'
  ),
  (
    28498457,
    'dummy_sub_28498457',
    'Vihaan Khan',
    'https://robohash.org/28498457.png?set=set4',
    'B.Tech.-M.Tech. Dual Degree',
    'Computer Science and Engineering',
    2031,
    'vihaan.khan@iitgn.ac.in',
    '9442511298',
    21,
    'M'
  ),
  (
    28498458,
    'dummy_sub_28498458',
    'Navya Shah',
    'https://robohash.org/28498458.png?set=set4',
    'M.Tech.',
    'Computer Science and Engineering',
    2031,
    'navya.shah@iitgn.ac.in',
    '7405900382',
    24,
    'F'
  ),
  (
    28498459,
    'dummy_sub_28498459',
    'Vamika Singh',
    'https://robohash.org/28498459.png?set=set4',
    'B.Tech.',
    'Chemical Engineering',
    2031,
    'vamika.singh@iitgn.ac.in',
    '6550707418',
    20,
    'F'
  ),
  (
    28498460,
    'dummy_sub_28498460',
    'Shaurya Patel',
    'https://robohash.org/28498460.png?set=set4',
    'B.Tech.',
    'Computer Science and Engineering',
    2026,
    'shaurya.patel@iitgn.ac.in',
    '6532512076',
    20,
    'M'
  ),
  (
    28498461,
    'dummy_sub_28498461',
    'Arjun Gupta',
    'https://robohash.org/28498461.png?set=set4',
    'M.Tech.',
    'Artificial Intelligence',
    2029,
    'arjun.gupta@iitgn.ac.in',
    '6691635952',
    27,
    'M'
  ),
  (
    28498462,
    'dummy_sub_28498462',
    'Shaurya Singh',
    'https://robohash.org/28498462.png?set=set4',
    'B.Tech.-M.Tech. Dual Degree',
    'Materials Engineering',
    2031,
    'shaurya.singh@iitgn.ac.in',
    '8866823487',
    23,
    'M'
  ),
  (
    28498463,
    'dummy_sub_28498463',
    'Reyansh Agarwal',
    'https://robohash.org/28498463.png?set=set4',
    'B.Tech.',
    'Integrated Circuit Design & Technology',
    2027,
    'reyansh.agarwal@iitgn.ac.in',
    '7170048076',
    21,
    'M'
  ),
  (
    28498464,
    'dummy_sub_28498464',
    'Kiara Rao',
    'https://robohash.org/28498464.png?set=set4',
    'B.Tech.',
    'Integrated Circuit Design & Technology',
    2026,
    'kiara.rao@iitgn.ac.in',
    '9896175005',
    21,
    'F'
  ),
  (
    28498465,
    'dummy_sub_28498465',
    'Shaurya Gupta',
    'https://robohash.org/28498465.png?set=set4',
    'B.Tech.',
    'Materials Engineering',
    2028,
    'shaurya.gupta@iitgn.ac.in',
    '6560622915',
    18,
    'M'
  ),
  (
    28498466,
    'dummy_sub_28498466',
    'Reyansh Mishra',
    'https://robohash.org/28498466.png?set=set4',
    'B.Tech.',
    'Computer Science and Engineering',
    2028,
    'reyansh.mishra@iitgn.ac.in',
    '7001045689',
    23,
    'M'
  ),
  (
    28498467,
    'dummy_sub_28498467',
    'Anaya Shah',
    'https://robohash.org/28498467.png?set=set4',
    'B.Tech.',
    'Artificial Intelligence',
    2028,
    'anaya.shah@iitgn.ac.in',
    '8845782775',
    22,
    'F'
  ),
  (
    28498468,
    '103550138619826229515',
    'Vedant Acharya',
    'https://lh3.googleusercontent.com/a/ACg8ocIO7FekHihQUHzNwP5u4jIgNJXa_WBFXP19hGO_0tRcQ8Z_cTQ=s96-c',
    'B.Tech',
    'CSE',
    2025,
    'vedant.acharya@iitgn.ac.in',
    '9328400669',
    20,
    'M'
  ),
  (
    28498472,
    '115296628781583554818',
    'Chavda Haarit Ravindrakumar',
    'https://lh3.googleusercontent.com/a/ACg8ocJL5oLjME02LsOPdAZsX-m_zNKTnAn8CUuftX03DmIkfhKkAZes=s96-c',
    'B.Tech',
    'CSE',
    2023,
    'haarit.chavda@iitgn.ac.in',
    '9978272883',
    20,
    'M'
  ),
  (
    28498474,
    '116571502198990145343',
    'Vedant Acharya',
    'https://lh3.googleusercontent.com/a/ACg8ocK_sOlEu2baXaM_1hhpRSfdlEDrk72CgWXWNRJF60LiSAC8hgQ=s96-c',
    'B.Tech',
    'EE',
    2026,
    'vedantsadhuff2006@gmail.com',
    '9367881021',
    21,
    'F'
  ),
  (
    28498489,
    '109787735348269282371',
    'Darpana Dharmesh Desai 23110085',
    'https://lh3.googleusercontent.com/a/ACg8ocI47uYNS3qOSiF6QdeWSDWG89w1moPXx-PpZTVI8GZieqxByDhL=s96-c',
    'B.Tech',
    'CSE',
    2023,
    'darpana.desai@iitgn.ac.in',
    '7016109752',
    20,
    'F'
  ),
  (
    28498490,
    '100181344598369680347',
    'Vedant Acharya',
    'https://lh3.googleusercontent.com/a/ACg8ocJdmifm9eK3HZAb_eYOLYY9_BSupjUL5vzCcRH-CweBFcHqLsE=s96-c',
    'B.Tech',
    'CSE',
    2025,
    'vedant.acharya2911@gmail.com',
    '9328400699',
    20,
    'F'
  );

/*!40000 ALTER TABLE `Members` ENABLE KEYS */;

UNLOCK TABLES;

--
-- Table structure for table `MessageHistory`
--
DROP TABLE IF EXISTS `MessageHistory`;

/*!40101 SET @saved_cs_client     = @@character_set_client */;

/*!50503 SET character_set_client = utf8mb4 */;

CREATE TABLE
  `MessageHistory` (
    `MessageID` int NOT NULL AUTO_INCREMENT,
    `RideID` varchar(50) NOT NULL,
    `SenderID` int NOT NULL,
    `MessageText` varchar(500) NOT NULL,
    `Timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `IsRead` tinyint (1) NOT NULL DEFAULT '0',
    PRIMARY KEY (`MessageID`),
    KEY `fk_message_sender` (`SenderID`),
    KEY `idx_msg_ride_time` (`RideID`, `Timestamp`),
    CONSTRAINT `fk_message_ride` FOREIGN KEY (`RideID`) REFERENCES `ActiveRides` (`RideID`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_message_sender` FOREIGN KEY (`SenderID`) REFERENCES `Members` (`MemberID`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = InnoDB AUTO_INCREMENT = 48 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MessageHistory`
--
LOCK TABLES `MessageHistory` WRITE;

/*!40000 ALTER TABLE `MessageHistory` DISABLE KEYS */;

INSERT INTO
  `MessageHistory`
VALUES
  (
    1,
    'dd1ee643-2f02-4546-977c-bc55fd4b55ea',
    28498463,
    'Hi, I have booked the ride. Are you near the pickup point?',
    '2026-02-10 09:00:00',
    0
  ),
  (
    2,
    '6e0180e5-20d9-4e12-872f-f6b45ef5cd82',
    28498446,
    'Yes, I am 2 minutes away. Please wait near the main gate.',
    '2026-02-10 09:02:00',
    0
  ),
  (
    4,
    'c409227a-e96e-4444-8749-15c2bd03d2ae',
    28498455,
    'Yes, that is fine. I am starting from my location now.',
    '2026-02-10 11:00:00',
    0
  ),
  (
    5,
    '6f179c80-7958-4a77-b0fb-00d61de45087',
    28498445,
    'I am standing outside the mall entrance. Can you see me?',
    '2026-02-10 12:30:00',
    0
  ),
  (
    6,
    'bc1f49d4-f927-4adf-97a8-86c33187bf44',
    28498459,
    'I have reached the pickup spot. Please confirm your location.',
    '2026-02-10 13:10:00',
    0
  ),
  (
    7,
    '9735ef94-75bf-49ed-bb07-953d50455b23',
    28498438,
    'I just booked the ride. What is your exact pickup point?',
    '2026-02-10 14:00:00',
    0
  ),
  (
    8,
    '4d54af73-b35e-4410-b352-f3eb42ebf559',
    28498438,
    'Let us meet near the petrol pump on the left side.',
    '2026-02-10 14:02:00',
    0
  ),
  (
    10,
    'a1287b4e-2a85-444b-9813-c5a4759cce8c',
    28498439,
    'I can see your car. Should I get in now?',
    '2026-02-10 16:00:00',
    0
  ),
  (
    11,
    'f29f6565-5bc4-495a-9878-4b91b3b876c3',
    28498452,
    'Yes, please get in. We will leave immediately.',
    '2026-02-10 17:10:00',
    0
  ),
  (
    13,
    'b83d9c8b-0278-4a57-9ba7-4b9673550776',
    28498459,
    'It should take around 30 minutes depending on traffic.',
    '2026-02-10 19:15:00',
    0
  ),
  (
    14,
    '553aced0-6547-41e5-9aaa-26ddf8e769ed',
    28498442,
    'Thanks for accepting my shared ride request.',
    '2026-02-10 20:00:00',
    0
  ),
  (
    15,
    '7dad019c-c58d-42db-be4f-9d7d794b57ed',
    28498464,
    'No problem, happy to share the ride with you!',
    '2026-02-10 21:00:00',
    0
  ),
  (
    16,
    '7262c937-95e9-4526-9efc-1d2d65db305c',
    28498445,
    'I think Uber is better.',
    '2026-02-12 09:00:00',
    0
  ),
  (
    17,
    'b6facd13-306b-4a00-9ef0-da8c342217a1',
    28498449,
    'Can we include I more member?',
    '2026-02-12 09:05:00',
    0
  ),
  (
    20,
    'b673fea0-b774-41f3-9e76-2846183a7467',
    28498465,
    'Hello, I wanna go to Gandhinagar Capital Railway Station.',
    '2026-02-12 09:20:00',
    0
  ),
  (
    26,
    'b6facd13-306b-4a00-9ef0-da8c342217a1',
    28498468,
    'hi',
    '2026-03-20 19:25:58',
    0
  ),
  (
    27,
    '4d54af73-b35e-4410-b352-f3eb42ebf559',
    28498468,
    'bye bye',
    '2026-03-20 19:26:23',
    0
  ),
  (
    28,
    '7262c937-95e9-4526-9efc-1d2d65db305c',
    28498468,
    'hello',
    '2026-03-20 19:29:17',
    0
  ),
  (
    30,
    'b6facd13-306b-4a00-9ef0-da8c342217a1',
    28498468,
    'Hi',
    '2026-03-22 02:30:24',
    0
  ),
  (
    33,
    '4d54af73-b35e-4410-b352-f3eb42ebf559',
    28498468,
    'MessaHige',
    '2026-03-22 02:34:37',
    0
  ),
  (
    35,
    '4d54af73-b35e-4410-b352-f3eb42ebf559',
    28498472,
    'hello guys',
    '2026-03-22 02:44:05',
    0
  ),
  (
    38,
    '4d54af73-b35e-4410-b352-f3eb42ebf559',
    28498468,
    'Hi',
    '2026-03-22 17:15:54',
    0
  ),
  (
    39,
    '4d54af73-b35e-4410-b352-f3eb42ebf559',
    28498474,
    'Hello',
    '2026-03-22 17:16:08',
    0
  ),
  (
    40,
    '4d54af73-b35e-4410-b352-f3eb42ebf559',
    28498468,
    'Hi',
    '2026-03-22 17:27:33',
    0
  ),
  (
    44,
    'b83d9c8b-0278-4a57-9ba7-4b9673550776',
    28498489,
    'hi',
    '2026-03-28 16:32:39',
    0
  );

/*!40000 ALTER TABLE `MessageHistory` ENABLE KEYS */;

UNLOCK TABLES;

--
-- Table structure for table `RideFeedback`
--
DROP TABLE IF EXISTS `RideFeedback`;

/*!40101 SET @saved_cs_client     = @@character_set_client */;

/*!50503 SET character_set_client = utf8mb4 */;

CREATE TABLE
  `RideFeedback` (
    `RideID` varchar(50) NOT NULL,
    `MemberID` int NOT NULL,
    `FeedbackText` varchar(500) NOT NULL,
    `FeedbackCategory` varchar(50) DEFAULT NULL,
    `SubmittedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`RideID`, `MemberID`),
    KEY `fk_feedback_member` (`MemberID`),
    CONSTRAINT `fk_feedback_member` FOREIGN KEY (`MemberID`) REFERENCES `Members` (`MemberID`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RideFeedback`
--
LOCK TABLES `RideFeedback` WRITE;

/*!40000 ALTER TABLE `RideFeedback` DISABLE KEYS */;

INSERT INTO
  `RideFeedback`
VALUES
  (
    '119fb431-101b-49d7-be17-92e9caab7c87',
    28498438,
    'Felt safe throughout.',
    'Safety',
    '2026-02-11 09:20:00'
  ),
  (
    '152056fd-7799-4aab-8156-c216eb76f0c3',
    28498448,
    'Awesome experience',
    'Safety',
    '2026-02-15 01:03:11'
  ),
  (
    '1aa9cfe1-5983-4e69-b836-f2dd09f29b7b',
    28498461,
    'Slight delay due to traffic.',
    'Punctuality',
    '2026-02-11 10:20:00'
  ),
  (
    '1bea2983-7e49-4705-a8a9-36f467fd0873',
    28498442,
    'Nice Car',
    'Punctuality',
    '2026-02-15 01:03:11'
  ),
  (
    '253e09ea-d227-432f-811c-c1237a674c46',
    28498468,
    'Hello',
    'Safety',
    '2026-03-22 17:46:10'
  ),
  (
    '299116dc-e3bd-4f0f-9642-9ff7688891f2',
    28498468,
    'It was good, I liked it',
    'Comfort',
    '2026-03-22 07:13:38'
  ),
  (
    '2b1c3ff3-e65b-40d9-baa2-a294f843e35d',
    28498447,
    'On-time departure.',
    'Punctuality',
    '2026-02-11 10:50:00'
  ),
  (
    '351d6041-9b8f-4b93-b3c8-613788d14dbe',
    28498443,
    'Smooth driving experience.',
    NULL,
    '2026-02-12 10:30:00'
  ),
  (
    '3a5cad27-a2e5-4f20-a70e-ddea0e82a852',
    28498451,
    'bad copassenger',
    'Safety',
    '2026-02-15 01:03:11'
  ),
  (
    '3bcc7676-04a0-4b0e-92f0-a688ecbc3f6c',
    28498474,
    'Hello',
    'Safety',
    '2026-03-22 17:25:34'
  ),
  (
    '3cc9024d-a7ef-46db-87e7-480fadcfa16d',
    28498467,
    'Will recommned to friends',
    'Safety',
    '2026-02-15 01:03:11'
  ),
  (
    '4675faeb-4be3-40b5-8350-031e9bdfb2da',
    28498468,
    'Hello',
    'Safety',
    '2026-03-22 17:14:05'
  ),
  (
    '4ced265c-6fa0-4485-a41c-267d1b8c52bf',
    28498447,
    'Felt very safe during ride.',
    'Safety',
    '2026-02-12 10:20:00'
  ),
  (
    '4d54af73-b35e-4410-b352-f3eb42ebf559',
    28498438,
    'Driver polite and helpful.',
    'Safety',
    '2026-02-11 10:10:00'
  ),
  (
    '4e697d34-d415-484d-8ade-88d9c928a350',
    28498468,
    'nICE',
    'Safety',
    '2026-03-22 06:31:48'
  ),
  (
    '525867bd-3a18-403b-a0bb-601eee3ce3ee',
    28498450,
    'AC not working',
    'Comfort',
    '2026-02-15 01:03:11'
  ),
  (
    '553aced0-6547-41e5-9aaa-26ddf8e769ed',
    28498442,
    'Driver was friendly.',
    'Safety',
    '2026-02-11 11:10:00'
  ),
  (
    '5f2acb79-ebf8-49ef-8588-dd63706e769a',
    28498465,
    'Friendly co-passengers',
    'Comfort',
    '2026-02-15 01:03:11'
  ),
  (
    '62e067d5-5155-4b71-b65f-f7fdc2e1bbf9',
    28498442,
    'Nice',
    'Comfort',
    '2026-02-15 01:03:11'
  ),
  (
    '66e87cba-96f7-4da4-bc09-eccea50bc882',
    28498468,
    'nice',
    'Safety',
    '2026-04-02 02:51:49'
  ),
  (
    '66e87cba-96f7-4da4-bc09-eccea50bc882',
    28498489,
    'good',
    'Punctuality',
    '2026-03-28 16:41:21'
  ),
  (
    '6e0180e5-20d9-4e12-872f-f6b45ef5cd82',
    28498446,
    'Driver was punctual.',
    'Punctuality',
    '2026-02-11 09:10:00'
  ),
  (
    '6f179c80-7958-4a77-b0fb-00d61de45087',
    28498445,
    'Reached on time.',
    'Punctuality',
    '2026-02-11 09:40:00'
  ),
  (
    '7262c937-95e9-4526-9efc-1d2d65db305c',
    28498445,
    'Nice and comfortable ride.',
    'Comfort',
    '2026-02-12 10:00:00'
  ),
  (
    '766d2473-dc58-413f-a814-8c54c928e701',
    28498460,
    'Will recommned to friends',
    'Safety',
    '2026-02-15 01:03:11'
  ),
  (
    '7bafd39b-6e2c-44fb-8b65-373ab4607608',
    28498456,
    'Need to improve chat UI',
    'Comfort',
    '2026-02-15 01:03:11'
  ),
  (
    '7dad019c-c58d-42db-be4f-9d7d794b57ed',
    28498464,
    'Ride was average.',
    NULL,
    '2026-02-11 11:20:00'
  ),
  (
    '8f5dedd8-21b3-4a5d-a1cf-8bd93db74b8c',
    28498439,
    'Friendly co-passengers',
    'Safety',
    '2026-02-15 01:03:11'
  ),
  (
    '8f7877f9-d082-4046-a9d0-daa413c1bcf8',
    28498439,
    'Driver was late',
    'Comfort',
    '2026-02-15 01:03:11'
  ),
  (
    '9735ef94-75bf-49ed-bb07-953d50455b23',
    28498438,
    'AC was not working.',
    'Comfort',
    '2026-02-11 10:00:00'
  ),
  (
    '9bd17bb6-2bf9-4245-bae6-5ac56f517ce4',
    28498462,
    'Nice Car',
    'Punctuality',
    '2026-02-15 01:03:11'
  ),
  (
    'a1287b4e-2a85-444b-9813-c5a4759cce8c',
    28498439,
    'Comfortable seats.',
    'Comfort',
    '2026-02-11 10:30:00'
  ),
  (
    'a8749424-ac53-4119-9b95-6d621d37d052',
    28498438,
    'Awesome experience',
    'Comfort',
    '2026-02-15 01:03:11'
  ),
  (
    'b3b7e197-41bd-442c-b30e-94d2ed874009',
    28498440,
    'bad copassenger',
    'Comfort',
    '2026-02-15 01:03:11'
  ),
  (
    'b539a100-4699-41d7-bc48-892b1d89bad2',
    28498452,
    'Need to improve chat UI',
    'Safety',
    '2026-02-15 01:03:11'
  ),
  (
    'b673fea0-b774-41f3-9e76-2846183a7467',
    28498465,
    'Vehicle was clean and neat.',
    'Comfort',
    '2026-02-12 10:40:00'
  ),
  (
    'b6facd13-306b-4a00-9ef0-da8c342217a1',
    28498449,
    'Driver arrived on time.',
    'Punctuality',
    '2026-02-12 10:10:00'
  ),
  (
    'b83d9c8b-0278-4a57-9ba7-4b9673550776',
    28498459,
    'Great experience overall.',
    NULL,
    '2026-02-11 11:00:00'
  ),
  (
    'bc1f49d4-f927-4adf-97a8-86c33187bf44',
    28498459,
    'Good driving skills.',
    'Safety',
    '2026-02-11 09:50:00'
  ),
  (
    'bda24468-ca06-4713-988e-2f9e2cdaa500',
    28498465,
    'Very great experience',
    'Safety',
    '2026-02-15 01:03:11'
  ),
  (
    'c2720c19-64e7-4608-bd08-5645c277aa96',
    28498489,
    'Nice',
    'Comfort',
    '2026-03-28 16:34:42'
  ),
  (
    'c409227a-e96e-4444-8749-15c2bd03d2ae',
    28498455,
    'Car was clean.',
    'Comfort',
    '2026-02-11 09:30:00'
  ),
  (
    'cf97d981-4613-4bac-971e-e6865052db20',
    28498449,
    'Driver was late',
    'Comfort',
    '2026-02-15 01:03:11'
  ),
  (
    'dd1ee643-2f02-4546-977c-bc55fd4b55ea',
    28498463,
    'Very smooth ride.',
    'Comfort',
    '2026-02-11 09:00:00'
  ),
  (
    'e83d295e-e4ef-48f1-aca2-ae62debe3381',
    28498460,
    'Awesome experience',
    'Punctuality',
    '2026-02-15 01:03:11'
  ),
  (
    'e98af64b-0dd8-4ae5-90db-063445fb203a',
    28498465,
    'AC not working',
    'Comfort',
    '2026-02-15 01:03:11'
  ),
  (
    'f29f6565-5bc4-495a-9878-4b91b3b876c3',
    28498452,
    'Felt very secure.',
    'Safety',
    '2026-02-11 10:40:00'
  ),
  (
    'f45f8311-e93f-4eba-b0a1-caa4ca41f858',
    28498463,
    'Will recommned to friends',
    'Safety',
    '2026-02-15 01:03:11'
  );

/*!40000 ALTER TABLE `RideFeedback` ENABLE KEYS */;

UNLOCK TABLES;

--
-- Table structure for table `RideHistory`
--
DROP TABLE IF EXISTS `RideHistory`;

/*!40101 SET @saved_cs_client     = @@character_set_client */;

/*!50503 SET character_set_client = utf8mb4 */;

CREATE TABLE
  `RideHistory` (
    `RideID` varchar(50) NOT NULL,
    `AdminID` int NOT NULL,
    `RideDate` date NOT NULL,
    `StartTime` time NOT NULL,
    `Source` varchar(100) NOT NULL,
    `Destination` varchar(100) NOT NULL,
    `Platform` varchar(30) NOT NULL,
    `Price` int NOT NULL,
    `FemaleOnly` tinyint (1) DEFAULT NULL,
    PRIMARY KEY (`RideID`),
    KEY `fk_ridehistory_admin` (`AdminID`),
    CONSTRAINT `fk_ridehistory_admin` FOREIGN KEY (`AdminID`) REFERENCES `Members` (`MemberID`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RideHistory`
--
LOCK TABLES `RideHistory` WRITE;

/*!40000 ALTER TABLE `RideHistory` DISABLE KEYS */;

INSERT INTO
  `RideHistory`
VALUES
  (
    '034e164c-6fe2-4d51-861c-95d02eb3f6ed',
    28498490,
    '2026-04-24',
    '02:26:00',
    'IIT Gandhinagar, Acad Block Path, - 382019, GJ, India',
    'Sector 9, Panchkula, India',
    'ols',
    50,
    0
  ),
  (
    '0e255964-65fb-4e26-955c-beb69785393b',
    28498442,
    '2026-02-12',
    '06:15:00',
    'IIT Gandhinagar (Palaj)',
    'IIT Gandhinagar (Palaj)',
    'InDrive',
    196,
    0
  ),
  (
    '152056fd-7799-4aab-8156-c216eb76f0c3',
    28498441,
    '2026-02-13',
    '22:30:00',
    'IIT Gandhinagar (Palaj)',
    'IIT Gandhinagar (Palaj)',
    'InDrive',
    451,
    1
  ),
  (
    '17bcba21-075c-49c6-8574-47214519b2e1',
    28498456,
    '2026-02-02',
    '07:30:00',
    'Gift City',
    'IIT Gandhinagar (Palaj)',
    'Private',
    384,
    0
  ),
  (
    '1bea2983-7e49-4705-a8a9-36f467fd0873',
    28498444,
    '2026-02-07',
    '10:15:00',
    'Ahmedabad Railway Station',
    'Ahmedabad Railway Station',
    'InDrive',
    423,
    1
  ),
  (
    '1fd3e50d-c543-4110-ba47-7144a7321122',
    28498462,
    '2026-02-14',
    '08:15:00',
    'IIT Gandhinagar (Palaj)',
    'IIT Gandhinagar (Palaj)',
    'Private',
    133,
    0
  ),
  (
    '253e09ea-d227-432f-811c-c1237a674c46',
    28498468,
    '2026-03-22',
    '17:44:00',
    'IIT Gandhinagar, Acad Block Path, - 382019, GJ, India',
    'Sector 16-9, Maharaja Agarsen Chowk, Sector 16, Panchkula - 134108, HR, India',
    'Uber',
    20,
    0
  ),
  (
    '3357e8ea-a4a9-4f99-9a0a-3643a89d1a51',
    28498464,
    '2026-01-29',
    '16:30:00',
    'Ahmedabad Railway Station',
    'IIT Gandhinagar (Palaj)',
    'Ola',
    209,
    0
  ),
  (
    '3a5cad27-a2e5-4f20-a70e-ddea0e82a852',
    28498446,
    '2026-02-07',
    '11:15:00',
    'Ahmedabad Railway Station',
    'IIT Gandhinagar (Palaj)',
    'InDrive',
    599,
    1
  ),
  (
    '3bcc7676-04a0-4b0e-92f0-a688ecbc3f6c',
    28498474,
    '2026-03-22',
    '17:15:00',
    'IIT Gandhinagar, Acad Block Path, - 382019, GJ, India',
    'Sector 9, Panchkula, India',
    'Ola',
    10,
    0
  ),
  (
    '3cc9024d-a7ef-46db-87e7-480fadcfa16d',
    28498441,
    '2026-02-03',
    '08:30:00',
    'Infocity',
    'IIT Gandhinagar (Palaj)',
    'Private',
    382,
    0
  ),
  (
    '4515709e-df3f-4f01-829c-9bfa6aac3af7',
    28498449,
    '2026-02-09',
    '17:00:00',
    'IIT Gandhinagar (Palaj)',
    'IIT Gandhinagar (Palaj)',
    'Uber',
    488,
    0
  ),
  (
    '458849ce-94ef-4371-bd9b-1c55b9bec9b6',
    28498449,
    '2026-02-01',
    '16:30:00',
    'IIT Gandhinagar (Palaj)',
    'SVPI Airport',
    'Private',
    231,
    0
  ),
  (
    '4675faeb-4be3-40b5-8350-031e9bdfb2da',
    28498468,
    '2026-03-22',
    '17:03:00',
    'IIT Gandhinagar, Acad Block Path, - 382019, GJ, India',
    'Jal Mandap, Gandhinagar Taluka, India',
    'Uber',
    100,
    0
  ),
  (
    '480d513c-d0f3-44ae-802c-da1b7b64a87f',
    28498445,
    '2026-02-13',
    '09:00:00',
    'Ahmedabad Railway Station',
    'Ahmedabad Railway Station',
    'Ola',
    146,
    0
  ),
  (
    '525867bd-3a18-403b-a0bb-601eee3ce3ee',
    28498448,
    '2026-01-27',
    '10:30:00',
    'Infocity',
    'IIT Gandhinagar (Palaj)',
    'InDrive',
    574,
    1
  ),
  (
    '5f2acb79-ebf8-49ef-8588-dd63706e769a',
    28498457,
    '2026-01-30',
    '22:00:00',
    'Ahmedabad Railway Station',
    'IIT Gandhinagar (Palaj)',
    'Uber',
    271,
    0
  ),
  (
    '62e067d5-5155-4b71-b65f-f7fdc2e1bbf9',
    28498465,
    '2026-01-29',
    '06:15:00',
    'Infocity',
    'Infocity',
    'Ola',
    164,
    1
  ),
  (
    '66e87cba-96f7-4da4-bc09-eccea50bc882',
    28498468,
    '2026-03-28',
    '20:37:00',
    'IIT Gandhinagar, Acad Block Path, - 382019, GJ, India',
    'Shiholi Lake, Shiholi - 382355, GJ, India',
    'Ola',
    100,
    0
  ),
  (
    '754e06d2-a43b-4b62-8f4e-df9e15593eed',
    28498446,
    '2026-01-31',
    '21:00:00',
    'IIT Gandhinagar (Palaj)',
    'IIT Gandhinagar (Palaj)',
    'Uber',
    278,
    0
  ),
  (
    '766d2473-dc58-413f-a814-8c54c928e701',
    28498466,
    '2026-02-04',
    '13:00:00',
    'Ahmedabad Railway Station',
    'Ahmedabad Railway Station',
    'Ola',
    155,
    0
  ),
  (
    '78d88260-537c-4439-b175-ff06c4eb0fcd',
    28498447,
    '2026-01-27',
    '12:30:00',
    'IIT Gandhinagar (Palaj)',
    'Ahmedabad Railway Station',
    'Ola',
    424,
    1
  ),
  (
    '7bafd39b-6e2c-44fb-8b65-373ab4607608',
    28498460,
    '2026-01-31',
    '08:15:00',
    'IIT Gandhinagar (Palaj)',
    'IIT Gandhinagar (Palaj)',
    'Private',
    327,
    0
  ),
  (
    '8469215d-ac85-4a64-ae88-51ec8a89bc09',
    28498454,
    '2026-01-30',
    '06:15:00',
    'IIT Gandhinagar (Palaj)',
    'IIT Gandhinagar (Palaj)',
    'Uber',
    183,
    0
  ),
  (
    '8a668859-41ad-4a2e-baa8-8e9afd0f1061',
    28498455,
    '2026-02-13',
    '07:15:00',
    'Gift City',
    'IIT Gandhinagar (Palaj)',
    'Uber',
    247,
    0
  ),
  (
    '8f5dedd8-21b3-4a5d-a1cf-8bd93db74b8c',
    28498439,
    '2026-02-03',
    '15:30:00',
    'SVPI Airport',
    'IIT Gandhinagar (Palaj)',
    'Ola',
    248,
    0
  ),
  (
    '8f7877f9-d082-4046-a9d0-daa413c1bcf8',
    28498447,
    '2026-02-07',
    '22:15:00',
    'Infocity',
    'Infocity',
    'InDrive',
    231,
    0
  ),
  (
    '939a2d5e-4b8b-4614-b5a3-c3ac9fd6242f',
    28498454,
    '2026-02-12',
    '22:30:00',
    'IIT Gandhinagar (Palaj)',
    'SVPI Airport',
    'Ola',
    414,
    1
  ),
  (
    '974ff030-0e5b-4c22-a242-dee141ffe44b',
    28498460,
    '2026-02-06',
    '13:15:00',
    'Kudasan',
    'IIT Gandhinagar (Palaj)',
    'Uber',
    566,
    0
  ),
  (
    '9bd17bb6-2bf9-4245-bae6-5ac56f517ce4',
    28498467,
    '2026-01-27',
    '14:15:00',
    'SG Highway',
    'IIT Gandhinagar (Palaj)',
    'Uber',
    114,
    0
  ),
  (
    '9cdc933e-0676-41ba-ae65-7637db70d3ab',
    28498439,
    '2026-02-12',
    '16:15:00',
    'IIT Gandhinagar (Palaj)',
    'IIT Gandhinagar (Palaj)',
    'InDrive',
    484,
    0
  ),
  (
    '9e1bc7fd-a916-4453-a378-017a0e304316',
    28498440,
    '2026-02-02',
    '19:15:00',
    'IIT Gandhinagar (Palaj)',
    'Ahmedabad Railway Station',
    'Ola',
    461,
    0
  ),
  (
    'a8749424-ac53-4119-9b95-6d621d37d052',
    28498450,
    '2026-02-11',
    '16:15:00',
    'SG Highway',
    'SG Highway',
    'Uber',
    446,
    0
  ),
  (
    'b3b7e197-41bd-442c-b30e-94d2ed874009',
    28498452,
    '2026-02-04',
    '16:30:00',
    'SG Highway',
    'SG Highway',
    'Private',
    483,
    0
  ),
  (
    'b539a100-4699-41d7-bc48-892b1d89bad2',
    28498439,
    '2026-02-02',
    '12:15:00',
    'Ahmedabad Railway Station',
    'Ahmedabad Railway Station',
    'Uber',
    133,
    0
  ),
  (
    'bda24468-ca06-4713-988e-2f9e2cdaa500',
    28498453,
    '2026-02-01',
    '13:00:00',
    'IIT Gandhinagar (Palaj)',
    'IIT Gandhinagar (Palaj)',
    'Ola',
    510,
    0
  ),
  (
    'c2720c19-64e7-4608-bd08-5645c277aa96',
    28498489,
    '2026-03-29',
    '16:33:00',
    'IIT Gandhinagar, Acad Block Path, - 382019, GJ, India',
    'GIFT City, Gandhinagar Taluka, India',
    'Uber',
    200,
    0
  ),
  (
    'cf56023f-de0e-4c63-9db6-bbbd554d452b',
    28498451,
    '2026-02-14',
    '20:00:00',
    'Ahmedabad Railway Station',
    'IIT Gandhinagar (Palaj)',
    'Ola',
    243,
    0
  ),
  (
    'cf97d981-4613-4bac-971e-e6865052db20',
    28498450,
    '2026-01-26',
    '11:15:00',
    'Infocity',
    'IIT Gandhinagar (Palaj)',
    'InDrive',
    330,
    0
  ),
  (
    'd0f95a70-14c5-4c70-914b-b12771c1098a',
    28498458,
    '2026-02-03',
    '07:30:00',
    'IIT Gandhinagar (Palaj)',
    'IIT Gandhinagar (Palaj)',
    'Uber',
    261,
    0
  ),
  (
    'ded92a7a-cb50-4381-8926-2be10b4c45ca',
    28498449,
    '2026-01-26',
    '16:00:00',
    'IIT Gandhinagar (Palaj)',
    'Gift City',
    'Uber',
    476,
    0
  ),
  (
    'e4006a76-2154-4b20-ab75-7e2e8184c837',
    28498450,
    '2026-01-27',
    '11:15:00',
    'SVPI Airport',
    'IIT Gandhinagar (Palaj)',
    'InDrive',
    496,
    0
  ),
  (
    'e50d3163-58e1-4708-a621-efafef1425d6',
    28498450,
    '2026-02-12',
    '22:15:00',
    'IIT Gandhinagar (Palaj)',
    'IIT Gandhinagar (Palaj)',
    'Ola',
    200,
    1
  ),
  (
    'e83d295e-e4ef-48f1-aca2-ae62debe3381',
    28498459,
    '2026-01-30',
    '09:30:00',
    'SG Highway',
    'IIT Gandhinagar (Palaj)',
    'Uber',
    356,
    0
  ),
  (
    'e98af64b-0dd8-4ae5-90db-063445fb203a',
    28498446,
    '2026-02-10',
    '07:15:00',
    'SG Highway',
    'SG Highway',
    'Private',
    474,
    1
  ),
  (
    'f45f8311-e93f-4eba-b0a1-caa4ca41f858',
    28498463,
    '2026-02-07',
    '22:00:00',
    'IIT Gandhinagar (Palaj)',
    'SVPI Airport',
    'Private',
    459,
    0
  );

/*!40000 ALTER TABLE `RideHistory` ENABLE KEYS */;

UNLOCK TABLES;

--
-- Table structure for table `RidePassengerMap`
--
DROP TABLE IF EXISTS `RidePassengerMap`;

/*!40101 SET @saved_cs_client     = @@character_set_client */;

/*!50503 SET character_set_client = utf8mb4 */;

CREATE TABLE
  `RidePassengerMap` (
    `RideID` varchar(50) NOT NULL,
    `PassengerID` int NOT NULL,
    `IsConfirmed` tinyint (1) NOT NULL DEFAULT '0',
    PRIMARY KEY (`RideID`, `PassengerID`),
    KEY `fk_ridemap_passenger` (`PassengerID`),
    CONSTRAINT `fk_ridemap_passenger` FOREIGN KEY (`PassengerID`) REFERENCES `Members` (`MemberID`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RidePassengerMap`
--
LOCK TABLES `RidePassengerMap` WRITE;

/*!40000 ALTER TABLE `RidePassengerMap` DISABLE KEYS */;

INSERT INTO
  `RidePassengerMap`
VALUES
  (
    '034e164c-6fe2-4d51-861c-95d02eb3f6ed',
    28498468,
    1
  ),
  (
    '034e164c-6fe2-4d51-861c-95d02eb3f6ed',
    28498490,
    1
  ),
  (
    '17187c24-a88e-4d91-98e9-f66c32de3489',
    28498468,
    1
  ),
  (
    '19487c13-c598-46ec-aa3c-407a1bf05669',
    28498490,
    1
  ),
  (
    '1cfec5d6-f24e-477c-85c5-506cb42a6995',
    28498468,
    1
  ),
  (
    '253e09ea-d227-432f-811c-c1237a674c46',
    28498468,
    1
  ),
  (
    '299116dc-e3bd-4f0f-9642-9ff7688891f2',
    28498468,
    1
  ),
  (
    '351d6041-9b8f-4b93-b3c8-613788d14dbe',
    28498440,
    0
  ),
  (
    '351d6041-9b8f-4b93-b3c8-613788d14dbe',
    28498459,
    1
  ),
  (
    '3bcc7676-04a0-4b0e-92f0-a688ecbc3f6c',
    28498474,
    1
  ),
  (
    '4675faeb-4be3-40b5-8350-031e9bdfb2da',
    28498468,
    1
  ),
  (
    '4675faeb-4be3-40b5-8350-031e9bdfb2da',
    28498474,
    1
  ),
  (
    '4ced265c-6fa0-4485-a41c-267d1b8c52bf',
    28498439,
    1
  ),
  (
    '4e697d34-d415-484d-8ade-88d9c928a350',
    28498468,
    1
  ),
  (
    '553aced0-6547-41e5-9aaa-26ddf8e769ed',
    28498439,
    1
  ),
  (
    '553aced0-6547-41e5-9aaa-26ddf8e769ed',
    28498461,
    0
  ),
  (
    '66e87cba-96f7-4da4-bc09-eccea50bc882',
    28498468,
    1
  ),
  (
    '66e87cba-96f7-4da4-bc09-eccea50bc882',
    28498489,
    1
  ),
  (
    '6e0180e5-20d9-4e12-872f-f6b45ef5cd82',
    28498445,
    0
  ),
  (
    '6e0180e5-20d9-4e12-872f-f6b45ef5cd82',
    28498461,
    0
  ),
  (
    '6f179c80-7958-4a77-b0fb-00d61de45087',
    28498454,
    1
  ),
  (
    '6f179c80-7958-4a77-b0fb-00d61de45087',
    28498466,
    0
  ),
  (
    '7262c937-95e9-4526-9efc-1d2d65db305c',
    28498439,
    1
  ),
  (
    '7262c937-95e9-4526-9efc-1d2d65db305c',
    28498456,
    1
  ),
  (
    '7dad019c-c58d-42db-be4f-9d7d794b57ed',
    28498440,
    1
  ),
  (
    '7dad019c-c58d-42db-be4f-9d7d794b57ed',
    28498453,
    1
  ),
  (
    '8eb5c093-a825-46a4-a335-cbe5cdbf43ea',
    28498468,
    1
  ),
  (
    '9735ef94-75bf-49ed-bb07-953d50455b23',
    28498456,
    1
  ),
  (
    'a1287b4e-2a85-444b-9813-c5a4759cce8c',
    28498448,
    1
  ),
  (
    'a1287b4e-2a85-444b-9813-c5a4759cce8c',
    28498451,
    1
  ),
  (
    'b673fea0-b774-41f3-9e76-2846183a7467',
    28498452,
    0
  ),
  (
    'b83d9c8b-0278-4a57-9ba7-4b9673550776',
    28498446,
    0
  ),
  (
    'b83d9c8b-0278-4a57-9ba7-4b9673550776',
    28498451,
    1
  ),
  (
    'bc1f49d4-f927-4adf-97a8-86c33187bf44',
    28498447,
    0
  ),
  (
    'bc1f49d4-f927-4adf-97a8-86c33187bf44',
    28498450,
    0
  ),
  (
    'c2720c19-64e7-4608-bd08-5645c277aa96',
    28498489,
    1
  ),
  (
    'c33b289b-0a64-4175-97f8-5186c3cdf0da',
    28498468,
    1
  ),
  (
    'c409227a-e96e-4444-8749-15c2bd03d2ae',
    28498465,
    1
  ),
  (
    'f29f6565-5bc4-495a-9878-4b91b3b876c3',
    28498450,
    1
  ),
  (
    'f29f6565-5bc4-495a-9878-4b91b3b876c3',
    28498464,
    1
  ),
  (
    'fe48ca24-e6f8-4870-8d40-191d38e0a94d',
    28498468,
    1
  );

/*!40000 ALTER TABLE `RidePassengerMap` ENABLE KEYS */;

UNLOCK TABLES;

--
-- Table structure for table `Vehicles`
--
DROP TABLE IF EXISTS `Vehicles`;

/*!40101 SET @saved_cs_client     = @@character_set_client */;

/*!50503 SET character_set_client = utf8mb4 */;

CREATE TABLE
  `Vehicles` (
    `VehicleID` int NOT NULL AUTO_INCREMENT,
    `VehicleType` varchar(30) NOT NULL,
    `MaxCapacity` int NOT NULL,
    PRIMARY KEY (`VehicleID`),
    CONSTRAINT `Vehicles_chk_1` CHECK ((`MaxCapacity` > 0))
  ) ENGINE = InnoDB AUTO_INCREMENT = 10 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Vehicles`
--
LOCK TABLES `Vehicles` WRITE;

/*!40000 ALTER TABLE `Vehicles` DISABLE KEYS */;

INSERT INTO
  `Vehicles`
VALUES
  (1, 'Bike', 1),
  (2, 'Auto Rickshaw', 3),
  (3, 'Mini Cab', 4),
  (4, 'Sedan Cab', 4),
  (5, 'SUV Cab', 6),
  (6, 'Premium SUV', 7),
  (7, 'New Cab', 10),
  (8, 'New Cab', 20),
  (9, 'Car', 5);

/*!40000 ALTER TABLE `Vehicles` ENABLE KEYS */;

UNLOCK TABLES;