from sqlalchemy import create_engine, text

urls = [
    "mysql+mysqlconnector://root:rootpass@127.0.0.1:3307/RideShare",
    "mysql+mysqlconnector://root:rootpass@127.0.0.1:3308/RideShare",
    "mysql+mysqlconnector://root:rootpass@127.0.0.1:3309/RideShare"
]

for i, url in enumerate(urls):
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM Members"))
            conn.execute(text("DELETE FROM ActiveRides"))
            conn.commit()
            result = conn.execute(text("SELECT * FROM Members"))

            print(f"\n--- Shard {i} Data ---")

            for row in result:
                print(row)

        print(f"Shard {i} ✅ OK")

    except Exception as e:
        print(f"Shard {i} ❌ FAILED: {e}")