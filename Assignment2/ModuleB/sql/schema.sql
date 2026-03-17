CREATE DATABASE IF NOT EXISTS RideShare;
USE RideShare;
CREATE TABLE IF NOT EXISTS Members (
    MemberID INT PRIMARY KEY AUTO_INCREMENT,
    FullName VARCHAR(100) NOT NULL,
    ProfileImageURL VARCHAR(255) DEFAULT 'default_avatar.png',
    -- Points to a default image initially
    Programme VARCHAR(50) NOT NULL,
    Branch VARCHAR(50),
    BatchYear YEAR NOT NULL,            
    Email VARCHAR(100) NOT NULL UNIQUE,
    ContactNumber VARCHAR(15) NOT NULL UNIQUE,
    Age INT NULL,                      
    Gender CHAR(1) NULL                
);

CREATE TABLE IF NOT EXISTS MemberStats (
    MemberID INT PRIMARY KEY,
    AverageRating DECIMAL(3,2) NOT NULL DEFAULT 0.00,
    TotalRidesTaken INT NOT NULL DEFAULT 0,
    TotalRidesHosted INT NOT NULL DEFAULT 0,
    NumberOfRatings INT NOT NULL DEFAULT 0,
    CONSTRAINT fk_stats_member FOREIGN KEY (MemberID)
        REFERENCES Members(MemberID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS
 ActiveRides (
   RideID VARCHAR(50) PRIMARY KEY,
   AdminID INT NOT NULL,
   AvailableSeats INT NOT NULL CHECK (AvailableSeats >= 0),
   PassengerCount INT NOT NULL CHECK (PassengerCount >= 1),
   Source VARCHAR(100) NOT NULL,
   Destination VARCHAR(100) NOT NULL,
   VehicleType VARCHAR(30) NOT NULL,
   StartTime DATETIME NOT NULL,
   EstimatedTime INT NOT NULL,
   FemaleOnly boolean,
   CONSTRAINT fk_activeride_admin FOREIGN KEY (AdminID)
       REFERENCES Members(MemberID)
       ON DELETE CASCADE
       ON UPDATE CASCADE
);

CREATE TABLE  IF NOT EXISTS RidePassengerMap (
   RideID VARCHAR(50) NOT NULL,
   PassengerID INT NOT NULL,
   IsConfirmed BOOLEAN NOT NULL DEFAULT FALSE,
   PRIMARY KEY (RideID, PassengerID),
   CONSTRAINT fk_ridemap_ride FOREIGN KEY (RideID)
       REFERENCES ActiveRides(RideID)
       ON DELETE CASCADE
       ON UPDATE CASCADE,
   CONSTRAINT fk_ridemap_passenger FOREIGN KEY (PassengerID)
       REFERENCES Members(MemberID)
       ON DELETE CASCADE
       ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Vehicles (
    VehicleID INT PRIMARY KEY AUTO_INCREMENT,
    VehicleType VARCHAR(30) NOT NULL,
    MaxCapacity INT NOT NULL CHECK (MaxCapacity > 0)
);

CREATE TABLE IF NOT EXISTS MessageHistory (
    MessageID INT PRIMARY KEY AUTO_INCREMENT,
    RideID VARCHAR(50) NOT NULL,
    SenderID INT NOT NULL,
    MessageText TEXT NOT NULL,
    Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    IsRead BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_message_ride FOREIGN KEY (RideID)
        REFERENCES ActiveRides(RideID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_message_sender FOREIGN KEY (SenderID)
        REFERENCES Members(MemberID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE  IF NOT EXISTS MemberRatings (
    RideID VARCHAR(50) NOT NULL,
    SenderMemberID INT NOT NULL,
    ReceiverMemberID INT NOT NULL,
    Rating DECIMAL(2,1) NOT NULL CHECK (Rating >= 1.0 AND Rating <= 5.0),
    RatingComment VARCHAR(500),
    RatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (RideID, SenderMemberID, ReceiverMemberID),
    CONSTRAINT fk_memberrating_sender FOREIGN KEY (SenderMemberID)
        REFERENCES Members(MemberID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_memberrating_receiver FOREIGN KEY (ReceiverMemberID)
        REFERENCES Members(MemberID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


CREATE TABLE  IF NOT EXISTS RideFeedback (
    RideID VARCHAR(50) PRIMARY KEY,
    MemberID INT NOT NULL,
    FeedbackText TEXT NOT NULL,
    FeedbackCategory VARCHAR(50),
    SubmittedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_feedback_member FOREIGN KEY (MemberID)
        REFERENCES Members(MemberID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE  IF NOT EXISTS RideHistory (
    RideID VARCHAR(50) PRIMARY KEY,
    AdminID INT NOT NULL,
    RideDate DATE NOT NULL,
    StartTime TIME NOT NULL,
    Source VARCHAR(100) NOT NULL,
    Destination VARCHAR(100) NOT NULL,
    Platform VARCHAR(30) NOT NULL,
    Price INT NOT NULL,
    FemaleOnly boolean,
    CONSTRAINT fk_ridehistory_admin FOREIGN KEY (AdminID)
        REFERENCES Members(MemberID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE  IF NOT EXISTS Cancellation (
    RideID VARCHAR(50) NOT NULL,
    MemberID INT NOT NULL,
    CancellationReason VARCHAR(255) NOT NULL,
    CONSTRAINT fk_cancellation_ride FOREIGN KEY (RideID)
        REFERENCES ActiveRides(RideID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_cancellation_member FOREIGN KEY (MemberID)
        REFERENCES Members(MemberID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE  IF NOT EXISTS BookingRequests (
    RequestID INT PRIMARY KEY AUTO_INCREMENT,
    RideID VARCHAR(50) NOT NULL,
    PassengerID INT NOT NULL,
    RequestStatus VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    RequestedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_booking_ride FOREIGN KEY (RideID)
        REFERENCES ActiveRides(RideID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_booking_passenger FOREIGN KEY (PassengerID)
        REFERENCES Members(MemberID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);