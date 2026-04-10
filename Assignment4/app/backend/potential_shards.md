### Members Table
* **Shard Key:** `MemberID` (Primary Key)
* **Partition strategy:** `hash(MemberID) % num_shards`
* **If num_shards = 3 Tables:** `shard_Members_0`, `shard_Members_1`, `shard_Members_2`
* **Alternative Shard Key:** `Email`
* **Trade-offs if we use Email instead:** String hashing is slightly more computationally expensive than integer hashing. More importantly, your APIs heavily rely on `MemberID` extracted from the JWT token (e.g., `get_current_user`). If you shard by Email, you would have to decode the email from the token or do a secondary lookup every time to find which shard a user belongs to.

### ActiveRides Table
* **Shard Key:** `AdminID` (Foreign Key to MemberID)
* **Partition strategy:** `hash(AdminID) % num_shards`
* **If num_shards = 3 Tables:** `shard_ActiveRides_0`, `shard_ActiveRides_1`, `shard_ActiveRides_2`
* **Alternative Shard Key:** `RideID`
* **Trade-offs if we use RideID instead:** While `RideID` (a UUID) provides mathematically perfect data distribution, it destroys data locality for the host. In your `GET /ride-history` and `GET /booking-requests/pending` APIs, you query where `AdminID == user.MemberID`. If sharded by `RideID`, the database doesn't know which shard holds User 5's rides, forcing your FastAPI app to query all 3 shards simultaneously (Scatter-Gather) and merge the results in memory.

### BookingRequests Table
* **Shard Key:** `PassengerID` (Foreign Key to MemberID)
* **Partition strategy:** `hash(PassengerID) % num_shards`
* **If num_shards = 3 Tables:** `shard_BookingRequests_0`, `shard_BookingRequests_1`, `shard_BookingRequests_2`
* **Alternative Shard Key:** `RideID`
* **Trade-offs if we use RideID instead:** This is a tricky one. If you shard by `RideID`, fetching "Pending requests for my hosted rides" becomes easier for the Host. However, your API `GET /booking-requests` fetches requests where `PassengerID == user.MemberID`. If you shard by `RideID`, finding a user's *own* outgoing requests requires querying all 3 shards. Sharding by `PassengerID` keeps the user's outgoing requests local, but means cross-shard JOINs are required when the Host views them.

### MessageHistory Table
* **Shard Key:** `SenderID` (Foreign Key to MemberID)
* **Partition strategy:** `hash(SenderID) % num_shards`
* **If num_shards = 3 Tables:** `shard_MessageHistory_0`, `shard_MessageHistory_1`, `shard_MessageHistory_2`
* **Alternative Shard Key:** `RideID`
* **Trade-offs if we use RideID instead:** **Actually, for this table, `RideID` is the BETTER choice.** Your API `GET /messages` explicitly filters by `rideId`. If you shard by `SenderID`, the messages for a single ride are scattered across all 3 shards. You would have to query all 3 shards, bring the messages into Python, and sort them by `Timestamp`. If you shard by `RideID` (using `hash(RideID)`), all messages for a specific chat room live on the exact same shard, making the query instantaneous. 

### MemberStat Table
* **Shard Key:** `MemberID` (Primary / Foreign Key)
* **Partition strategy:** `hash(MemberID) % num_shards`
* **If num_shards = 3 Tables:** `shard_MemberStats_0`, `shard_MemberStats_1`, `shard_MemberStats_2`
* **Alternative Shard Key:** `AverageRating` (Range-Based)
* **Trade-offs if we use AverageRating instead:** Range partitioning by a mutable value is a database anti-pattern. Every time a user gets a new rating that pushes them from a 3.9 to a 4.1, the database would have to physically delete their row from Shard 0 and insert it into Shard 1. This causes massive write overhead.

### RidePassengerMap Table
* **Shard Key:** `PassengerID` (Foreign Key to MemberID)
* **Partition strategy:** `hash(PassengerID) % num_shards`
* **If num_shards = 3 Tables:** `shard_RidePassengerMap_0`, `shard_RidePassengerMap_1`, `shard_RidePassengerMap_2`
* **Alternative Shard Key:** `RideID`
* **Trade-offs if we use RideID instead:** Similar to `BookingRequests`. If you shard by `RideID`, you easily know who is in a specific ride. However, in your `/ride-history` API, you look up all rides a user has taken by filtering `PassengerID == user.MemberID`. If sharded by `RideID`, retrieving a user's history requires a Scatter-Gather across all nodes. 

### MemberRating Table
* **Shard Key:** `ReceiverMemberID` (Foreign Key to MemberID)
* **Partition strategy:** `hash(ReceiverMemberID) % num_shards`
* **If num_shards = 3 Tables:** `shard_MemberRatings_0`, `shard_MemberRatings_1`, `shard_MemberRatings_2`
* **Alternative Shard Key:** `SenderMemberID` or `RideID`
* **Trade-offs if we use Sender/RideID instead:** Ratings are almost entirely queried to aggregate a user's `MemberStat`. By sharding on `ReceiverMemberID`, all ratings *about* User 5 live on User 5's shard. If you shard by `SenderMemberID`, recalculating User 5's average rating requires scanning all 3 shards to find every time someone rated them.

### RideFeedback Table
* **Shard Key:** `MemberID` (Foreign Key to MemberID)
* **Partition strategy:** `hash(MemberID) % num_shards`
* **If num_shards = 3 Tables:** `shard_RideFeedback_0`, `shard_RideFeedback_1`, `shard_RideFeedback_2`
* **Alternative Shard Key:** `RideID`
* **Trade-offs if we use RideID instead:** In your `GET /ride-history` endpoint, you check if the current user has left feedback using `Feedback.MemberID == user.MemberID`. If sharded by `RideID`, this query might require cross-shard lookups depending on how you structure the Python loop.

### RideHistory Table
* **Shard Key:** `AdminID` (Foreign Key to MemberID)
* **Partition strategy:** `hash(AdminID) % num_shards`
* **If num_shards = 3 Tables:** `shard_RideHistory_0`, `shard_RideHistory_1`, `shard_RideHistory_2`
* **Alternative Shard Key:** `RideDate` (Range-Based)
* **Trade-offs if we use RideDate instead:** Sharding by Date (e.g., Shard 0: Jan-April, Shard 1: May-Aug) causes a "Write Hotspot". Because all rides happen in the present, 100% of your new inserts will hit a single shard (the current month's shard), while the others sit completely idle. Sharding by `AdminID` ensures writes are distributed evenly.

### Cancellation Table
* **Shard Key:** `MemberID` (Foreign Key to MemberID)
* **Partition strategy:** `hash(MemberID) % num_shards`
* **If num_shards = 3 Tables:** `shard_Cancellation_0`, `shard_Cancellation_1`, `shard_Cancellation_2`
* **Alternative Shard Key:** `RideID`
* **Trade-offs if we use RideID instead:** Cancellations are tied to the user who cancelled. If you want to build an administrative feature later to see "How many rides has User 5 cancelled?", sharding by `RideID` forces a scatter-gather query across the cluster.

---

### A Note on the `Vehicle` Table
You should **not** shard the `Vehicles` table. Because it is a small reference table (likely containing only a few rows like "Hatchback", "Sedan", "SUV"), it should be **replicated** (copied) entirely to all 3 shards. This ensures that any JOINs or lookups for `MaxCapacity` can happen locally on any shard without needing network requests.
