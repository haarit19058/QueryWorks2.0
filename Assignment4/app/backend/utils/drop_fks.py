import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_URLS = {
    0: os.getenv("SHARD0_DATABASE_URL"),
    1: os.getenv("SHARD1_DATABASE_URL"),
    2: os.getenv("SHARD2_DATABASE_URL")
}

statements = [
    "ALTER TABLE ActiveRides DROP FOREIGN KEY fk_activeride_admin;",
    "ALTER TABLE BookingRequests DROP FOREIGN KEY fk_booking_passenger;",
    "ALTER TABLE BookingRequests DROP FOREIGN KEY fk_booking_ride;",
    "ALTER TABLE Cancellations DROP FOREIGN KEY fk_cancellation_member;",
    "ALTER TABLE MemberRatings DROP FOREIGN KEY fk_memberrating_receiver;",
    "ALTER TABLE MemberRatings DROP FOREIGN KEY fk_memberrating_sender;",
    "ALTER TABLE MemberStats DROP FOREIGN KEY fk_stats_member;",
    "ALTER TABLE MessageHistory DROP FOREIGN KEY fk_message_ride;",
    "ALTER TABLE MessageHistory DROP FOREIGN KEY fk_message_sender;",
    "ALTER TABLE RideFeedback DROP FOREIGN KEY fk_feedback_member;",
    "ALTER TABLE RideHistory DROP FOREIGN KEY fk_ridehistory_admin;",
    "ALTER TABLE RideMap DROP FOREIGN KEY fk_ridemap_passenger;"
]

for shard_id, url in DB_URLS.items():
    if not url: continue
    print(f"Dropping FKs on shard {shard_id} at {url}")
    engine = create_engine(url)
    with engine.connect() as conn:
        for stmt in statements:
            try:
                conn.execute(text(stmt))
                print(f"✓ Executed: {stmt[:40]}...")
            except Exception as e:
                print(f"Skipped (perhaps already dropped): {stmt[:40]}...")
        conn.commit()

print("All foreign keys removed.")
