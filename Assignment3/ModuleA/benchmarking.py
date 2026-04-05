import os
import time
import threading
import matplotlib.pyplot as plt
from db_manager import DatabaseManager

from sqlalchemy import create_engine, Column, Integer, String, update
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import event

# --- Configurations ---
NUM_TXNS = 500
CONCURRENCY_LEVEL = 10
STORAGE_DIR = os.path.join(os.getcwd(), "benchmark_storage")

# The SQLAlchemy Database URL. You can change this to postgresql://... or mysql://...
DB_URL = f"mysql+mysqlconnector://root:rootpass@10.7.5.171:3306/temp1"

# --- SQLAlchemy Models ---
Base = declarative_base()

class Member(Base):
    __tablename__ = 'members'
    member_id = Column(Integer, primary_key=True)
    balance = Column(Integer)

class Vehicle(Base):
    __tablename__ = 'vehicles'
    vehicle_id = Column(Integer, primary_key=True)
    stock = Column(Integer)

class ActiveRide(Base):
    __tablename__ = 'active_rides'
    # Add a length to the String, e.g., String(50)
    ride_id = Column(String(50), primary_key=True) 
    admin_id = Column(Integer)
    vehicle_id = Column(Integer)

# --- Database Setup Functions ---

def setup_custom_db():
    """Initialize the Custom B+ Tree DB and populate initial data."""
    os.makedirs(STORAGE_DIR, exist_ok=True)
    db = DatabaseManager(db_path=STORAGE_DIR)
    db.create_database("BenchmarkDB")
    
    db.create_table("Members", "MemberID", schema={"MemberID": int, "Balance": int})
    db.create_table("Vehicles", "VehicleID", schema={"VehicleID": int, "Stock": int})
    db.create_table("ActiveRides", "RideID", schema={"RideID": str, "AdminID": int, "VehicleID": int})
    
    # Initialize some data
    tid = db.txn_begin()
    for i in range(1, NUM_TXNS + 1):
        db.get_table("Members").insert({"MemberID": i, "Balance": 1000}, tid=tid, dbm=db)
        db.get_table("Vehicles").insert({"VehicleID": i, "Stock": 5}, tid=tid, dbm=db)
    db.txn_commit(tid)
    return db

def setup_sqlalchemy_db(db_url):
    """Initialize the SQLAlchemy DB, populate data, and return the engine."""
    # If using SQLite, add a timeout to prevent instant lock failures
    connect_args = {'timeout': 15.0} if db_url.startswith("sqlite") else {}
    engine = create_engine(db_url, connect_args=connect_args)
    
    # Optimize SQLite for concurrent writes using WAL mode
    if db_url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()

    # Drop and recreate tables for a clean slate
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as session:
        # Bulk insert initial data
        members = [Member(member_id=i, balance=1000) for i in range(1, NUM_TXNS + 1)]
        vehicles = [Vehicle(vehicle_id=i, stock=5) for i in range(1, NUM_TXNS + 1)]
        session.add_all(members)
        session.add_all(vehicles)
        session.commit()
        
    return engine

# --- Worker Threads ---

def custom_db_worker(db, start_id, count):
    """Worker thread for Custom DB executing multi-table transactions."""
    members = db.get_table("Members")
    vehicles = db.get_table("Vehicles")
    rides = db.get_table("ActiveRides")
    
    for i in range(start_id, start_id + count):
        try:
            tid = db.txn_begin()
            # Multi-table transaction (3 relations as required)
            members.update(i, {"MemberID": i, "Balance": 900}, tid=tid, dbm=db)
            vehicles.update(i, {"VehicleID": i, "Stock": 4}, tid=tid, dbm=db)
            rides.insert({"RideID": f"RIDE_{i}", "AdminID": i, "VehicleID": i}, tid=tid, dbm=db)
            db.txn_commit(tid)
        except Exception:
            db.txn_abort(tid)

def sqlalchemy_worker(engine, start_id, count):
    """Worker thread for SQLAlchemy executing multi-table ORM transactions."""
    SessionLocal = sessionmaker(bind=engine)
    
    # Each thread gets its own session
    with SessionLocal() as session:
        for i in range(start_id, start_id + count):
            try:
                # session.begin() creates a transaction context
                with session.begin():
                    # Update Member
                    session.execute(
                        update(Member).where(Member.member_id == i).values(balance=900)
                    )
                    # Update Vehicle
                    session.execute(
                        update(Vehicle).where(Vehicle.vehicle_id == i).values(stock=4)
                    )
                    # Insert ActiveRide
                    new_ride = ActiveRide(ride_id=f"RIDE_{i}", admin_id=i, vehicle_id=i)
                    session.add(new_ride)
            except Exception:
                # session.begin() automatically rolls back on exception
                pass

# --- Benchmark Execution ---

def run_benchmark():
    print("Setting up Custom B+ Tree database...")
    custom_db = setup_custom_db()
    
    print(f"Setting up SQLAlchemy database at {DB_URL}...")
    sa_engine = setup_sqlalchemy_db(DB_URL)

    txns_per_thread = NUM_TXNS // CONCURRENCY_LEVEL

    # Test Custom DB
    print(f"\nRunning Custom DB Benchmark ({NUM_TXNS} txns, {CONCURRENCY_LEVEL} threads)...")
    start_time = time.time()
    threads = []
    for i in range(CONCURRENCY_LEVEL):
        start_id = (i * txns_per_thread) + 1
        t = threading.Thread(target=custom_db_worker, args=(custom_db, start_id, txns_per_thread))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    custom_time = time.time() - start_time
    custom_tps = NUM_TXNS / custom_time

    # Test SQLAlchemy DB
    print(f"Running SQLAlchemy Benchmark ({NUM_TXNS} txns, {CONCURRENCY_LEVEL} threads)...")
    start_time = time.time()
    threads = []
    for i in range(CONCURRENCY_LEVEL):
        start_id = (i * txns_per_thread) + 1
        t = threading.Thread(target=sqlalchemy_worker, args=(sa_engine, start_id, txns_per_thread))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    sa_time = time.time() - start_time
    sa_tps = NUM_TXNS / sa_time

    print("\n--- Results ---")
    print(f"Custom DB:  {custom_time:.2f} seconds ({custom_tps:.2f} TPS)")
    print(f"SQLAlchemy: {sa_time:.2f} seconds ({sa_tps:.2f} TPS)")

    generate_plots(custom_tps, sa_tps)

def generate_plots(custom_tps, sa_tps):
    """Generates and saves a bar chart comparing throughput."""
    labels = ['Custom B+ Tree DB', 'SQLAlchemy (SQLite)']
    tps_values = [custom_tps, sa_tps]

    plt.figure(figsize=(8, 5))
    colors = ['#1f77b4', '#ff7f0e']
    bars = plt.bar(labels, tps_values, color=colors, width=0.5)
    
    plt.ylabel('Transactions Per Second (TPS)')
    plt.title('Multi-Table ACID Transaction Throughput')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + (max(tps_values)*0.02), 
                 f"{yval:.1f} TPS", ha='center', va='bottom', fontweight='bold')

    plt.savefig('acid_throughput_comparison.png', dpi=300, bbox_inches='tight')
    print("\nPlot saved successfully as 'acid_throughput_comparison.png'")

if __name__ == "__main__":
    run_benchmark()