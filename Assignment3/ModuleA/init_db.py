"""
Step 1: Initialize database by loading all 11 CSV tables
and saving their B+ tree state to disk.

Run from inside Assignment3/ModuleA:
    python init_db.py
"""

import os
from db_manager import DatabaseManager

def main():
    storage_dir = os.path.join(os.getcwd(), "storage")
    os.makedirs(storage_dir, exist_ok=True)

    db = DatabaseManager(db_path=storage_dir)
    db.create_database("QueryWorksDB")

    schemas = {
        "Vehicles": {"VehicleID": int, "VehicleType": str, "MaxCapacity": int},
        "Members": {"MemberID": int, "FullName": str, "ProfileImageURL": str,
                    "Programme": str, "Branch": str, "BatchYear": int,
                    "Email": str, "ContactNumber": str, "Age": int, "Gender": str},
        "MemberStats": {"MemberID": int, "AverageRating": float,
                        "TotalRidesTaken": int, "TotalRidesHosted": int,
                        "NumberOfRatings": int},
        "ActiveRides": {"RideID": str, "AdminID": int, "AvailableSeats": int,
                        "PassengerCount": int, "Source": str, "Destination": str,
                        "VehicleType": str, "StartTime": str, "EstimatedTime": int,
                        "FemaleOnly": int},
        "RideHistory": {"RideID": str, "AdminID": int, "RideDate": str,
                        "StartTime": str, "Source": str, "Destination": str,
                        "Platform": str, "Price": int, "FemaleOnly": int},
        "BookingRequests": {"RequestID": int, "RideID": str, "PassengerID": int,
                            "RequestStatus": str, "RequestedAt": str},
        "RidePassengerMap": {"RideID": str, "PassengerID": int, "IsConfirmed": int},
        "Cancellation": {"RideID": str, "MemberID": int, "CancellationReason": str},
        "RideFeedback": {"RideID": str, "MemberID": int, "FeedbackText": str,
                         "FeedbackCategory": str, "SubmittedAt": str},
        "MemberRatings": {"RideID": str, "SenderMemberID": int, "ReceiverMemberID": int,
                          "Rating": float, "RatingComment": str, "RatedAt": str},
        "MessageHistory": {"MessageID": int, "RideID": str, "SenderID": int,
                           "MessageText": str, "Timestamp": str, "IsRead": int}
    }

    for name, schema in schemas.items():
        key = list(schema.keys())[0]
        table = db.create_table(name, key, schema=schema)
        table.load_csv(f"tables/{name}.csv")
        db.save_index(name)

    print("\n--- Database initialized and saved ---")

if __name__ == "__main__":
    main()