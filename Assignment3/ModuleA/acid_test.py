"""
Step 2: ACID property verification test with checkpointing.

Run from inside Assignment3/ModuleA:
    python acid_test.py
"""

import os
from db_manager import DatabaseManager

def main():
    storage_dir = os.path.join(os.getcwd(), "storage")
    db = DatabaseManager(db_path=storage_dir)
    db.create_database("QueryWorksDB")

    # Reload tables from persisted indexes
    vehicles = db.create_table("Vehicles", "VehicleID",
        schema={"VehicleID": int, "VehicleType": str, "MaxCapacity": int})
    members = db.create_table("Members", "MemberID",
        schema={"MemberID": int, "FullName": str, "ProfileImageURL": str,
                "Programme": str, "Branch": str, "BatchYear": int,
                "Email": str, "ContactNumber": str, "Age": int, "Gender": str})
    activerides = db.create_table("ActiveRides", "RideID",
        schema={"RideID": str, "AdminID": int, "AvailableSeats": int,
                "PassengerCount": int, "Source": str, "Destination": str,
                "VehicleType": str, "StartTime": str, "EstimatedTime": int,
                "FemaleOnly": int})

    db.load_index("Vehicles")
    db.load_index("Members")
    db.load_index("ActiveRides")

    # --- Atomicity ---
    print("\n[Atomicity] Multi-table rollback")
    tid = db.txn_begin()
    members.update(28498438, members.get(28498438), tid=tid, dbm=db)
    vehicles.update(1, {"VehicleID": 1, "VehicleType": "Bike", "MaxCapacity": 2}, tid=tid, dbm=db)
    activerides.insert({"RideID": "TXN001", "AdminID": 28498438,
                        "AvailableSeats": 1, "PassengerCount": 0,
                        "Source": "IITGN", "Destination": "Airport",
                        "VehicleType": "Bike", "StartTime": "2026-03-31 08:00:00",
                        "EstimatedTime": 40, "FemaleOnly": 0}, tid=tid, dbm=db)
    print("During txn, TXN001:", activerides.get("TXN001"))
    db.txn_abort(tid)
    print("After abort, TXN001:", activerides.get("TXN001"))

    # --- Consistency ---
    print("\n[Consistency] Invalid record rejected")
    tid = db.txn_begin()
    bad_vehicle = {"VehicleID": 99, "VehicleType": "Bike", "MaxCapacity": -5}
    ok, err = vehicles.validate_record(bad_vehicle)
    print("Validation result:", ok, err)
    if ok:
        vehicles.insert(bad_vehicle, tid=tid, dbm=db)
        db.txn_commit(tid)
    else:
        db.txn_abort(tid)
    print("Vehicle 99 after consistency check:", vehicles.get(99))

    # --- Isolation ---
    print("\n[Isolation] Concurrent transactions")
    tid1 = db.txn_begin()
    tid2 = db.txn_begin()
    try:
        members.update(28498439, members.get(28498439), tid=tid1, dbm=db)
        members.update(28498439, members.get(28498439), tid=tid2, dbm=db)
        db.txn_commit(tid1)
        db.txn_abort(tid2)
        print("Member 28498439 after isolation:", members.get(28498439))
    except Exception as e:
        print("Isolation test: concurrent update blocked ->", e)
        db.txn_abort(tid1)
        db.txn_abort(tid2)

    # --- Durability ---
    print("\n[Durability] Commit survives restart")
    tid = db.txn_begin()
    activerides.insert({"RideID": "DURABLE1", "AdminID": 28498439,
                        "AvailableSeats": 2, "PassengerCount": 0,
                        "Source": "Gift City", "Destination": "IITGN",
                        "VehicleType": "Auto Rickshaw", "StartTime": "2026-03-31 12:00:00",
                        "EstimatedTime": 40, "FemaleOnly": 0}, tid=tid, dbm=db)
    db.txn_commit(tid)
    print("Ride DURABLE1 after commit:", activerides.get("DURABLE1"))

    # Restart simulation
    db2 = DatabaseManager(db_path=storage_dir)
    db2.create_database("QueryWorksDB")
    activerides2 = db2.create_table("ActiveRides", "RideID",
        schema={"RideID": str, "AdminID": int, "AvailableSeats": int,
                "PassengerCount": int, "Source": str, "Destination": str,
                "VehicleType": str, "StartTime": str, "EstimatedTime": int,
                "FemaleOnly": int})
    db2.load_index("ActiveRides")
    db2._recovery_mgr.recover()
    print("Ride DURABLE1 after recovery:", activerides2.get("DURABLE1"))

    # --- Checkpoint demonstration ---
    print("\n[Checkpoint] Trigger after 10 commits")
    for i in range(10):
        tid = db.txn_begin()
        activerides.insert({"RideID": f"CHK{i}", "AdminID": 28498438,
                            "AvailableSeats": 1, "PassengerCount": 0,
                            "Source": "IITGN", "Destination": "Gift City",
                            "VehicleType": "Sedan Cab", "StartTime": f"2026-03-31 0{i}:00:00",
                            "EstimatedTime": 30, "FemaleOnly": 0}, tid=tid, dbm=db)
        db.txn_commit(tid)  # after 10th commit, checkpoint runs

if __name__ == "__main__":
    main()