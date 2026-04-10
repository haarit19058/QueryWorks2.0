### Authentication Endpoints
*   **`POST /auth/login`**
    *   **Tables:** `Member`
    *   **Action:** **SELECT**s the `Member` table by email to check if the user exists. If they do, authenticates them; if not, initiates the registration flow.
*   **`POST /auth/signup`**
    *   **Tables:** `Member`
    *   **Action:** **INSERT**s a new record into the `Member` table upon successful Google authentication.
*   **`GET /auth/me`** *(Uses `get_current_user` dependency)*
    *   **Tables:** `Member`
    *   **Action:** **SELECT**s the member matching the Session token payload ID to return the current logged-in user.

### Rides Endpoints
*   **`GET /rides`**
    *   **Tables:** `ActiveRide`, `Member`, `RidePassengerMap`
    *   **Action:** 
        *   **SELECT**s all `ActiveRide` records, joining with `Member` to get the host's details.
        *   **SELECT**s passengers for those rides from `RidePassengerMap`, joining with `Member` to retrieve passenger details.
*   **`POST /rides`**
    *   **Tables:** `Vehicle`, `ActiveRide`, `RidePassengerMap`
    *   **Action:**
        *   **SELECT**s the `Vehicle` table to locate maximum capacity constraints.
        *   **INSERT**s a new ride into `ActiveRide`.
        *   **INSERT**s the host as a confirmed passenger into the `RidePassengerMap`.
*   **`PATCH /rides/{ride_id}/status`**
    *   **Tables:** `ActiveRide`, `RideHistory`, `Cancellation`, `RidePassengerMap`, `MemberStat`
    *   **Action:** 
        *   **SELECT**s the `ActiveRide` to verify it exists and is owned by the requester.
        *   If status changes to `COMPLETED`: **INSERT**s the ride into `RideHistory`, **SELECT**s passengers from `RidePassengerMap`, **SELECT/UPDATE/INSERT**s aggregate driving statistics into `MemberStat` for all participants, and finally **DELETE**s the ride from `ActiveRide`.
        *   If status changes to `CANCELLED`: **INSERT**s a record into `Cancellation` and **DELETE**s the ride from `ActiveRide`.
        *   Otherwise: **UPDATE**s the status string in `ActiveRide`.

### Feedback & Ratings
*   **`POST /feedback`**
    *   **Tables:** `RideHistory`, `RidePassengerMap`, `RideFeedback`
    *   **Action:** 
        *   **SELECT**s `RideHistory` to ensure the ride is completed.
        *   **SELECT**s `RidePassengerMap` to ensure the user successfully participated.
        *   **SELECT**s `RideFeedback` to detect existing duplicate submissions.
        *   **INSERT**s a new feedback record into `RideFeedback`.
*   **`POST /ratings`**
    *   **Tables:** `MemberRating`, `MemberStat`
    *   **Action:**
        *   **SELECT**s `MemberRating` to prevent users from double-rating others for the same ride.
        *   **INSERT**s a new review record into `MemberRating`.
        *   **SELECT**s the recipient from `MemberStat` and **UPDATE**s their `AverageRating` and quantitative metrics.
*   **`GET /ride-history`**
    *   **Tables:** `RideHistory`, `RidePassengerMap`, `Member`, `RideFeedback`
    *   **Action:** 
        *   **SELECT**s rides built by the user natively parsing `RideHistory`.
        *   **SELECT**s rides joined by the user using a nested join between `RideHistory` and `RidePassengerMap`.
        *   For each ride returned, it recursively **SELECT**s admin details (`Member`), participants list (`RidePassengerMap` + `Member`), and checks if feedback was submitted (`RideFeedback`).

### Booking Requests
*   **`GET /booking-requests`**
    *   **Tables:** `BookingRequest`
    *   **Action:** **SELECT**s all requests created by the active `PassengerID`.
*   **`POST /booking-requests`**
    *   **Tables:** `BookingRequest`
    *   **Action:** **INSERT**s a new pending `BookingRequest` mapped against a generated `RideID`.
*   **`GET /booking-requests/pending`**
    *   **Tables:** `BookingRequest`, `ActiveRide`, `Member`
    *   **Action:** **SELECT**s pending approval bookings that align directly to the active user's created rides (matching `ActiveRide.AdminID`), pulling in names from `Member`.
*   **`PATCH /booking-requests/{request_id}`**
    *   **Tables:** `BookingRequest`, `ActiveRide`, `RidePassengerMap`
    *   **Action:** 
        *   **SELECT**s a specific `BookingRequest` followed by **UPDATE**-ing its status.
        *   If approved, **SELECT**s and **UPDATE**s seat counts inside `ActiveRide`. It then natively drops a new mapping item by **INSERT**-ing the passenger inside `RidePassengerMap`.

### Messages
*   **`GET /messages`**
    *   **Tables:** `MessageHistory`, `Member`
    *   **Action:** **SELECT**s message logs attached to a specific `RideID`, joined with `Member` to bundle in sender profile pictures and usernames.
*   **`POST /messages`**
    *   **Tables:** `MessageHistory`
    *   **Action:** **INSERT**s freshly received payload contents into the message table layout.

### User Profiles
*   **`GET /members/{member_id}`**
    *   **Tables:** `Member`, `MemberStat`
    *   **Action:** Extracts explicit outer-bound **SELECT** mappings correlating a user to their corresponding historic aggregations across both target tables.

### Admin Tools (Validates via `admin.json`)
*   **`GET /admin/current-admins`**
    *   **Tables:** `Member`
    *   **Action:** **SELECT**s member entities leveraging `Member.MemberID.in_()` lookup checks.
*   **`POST /admin/add-admin`**
    *   **Tables:** `Member`
    *   **Action:** **SELECT**s via email to map internal UUID validation hooks directly to file-system storage payloads.
*   **`GET /admin/see-member-table`**
    *   **Tables:** `Member`
    *   **Action:** Global **SELECT** dump of all active platform members across instances.
*   **`POST /admin/remove-ride`**
    *   **Tables:** `ActiveRide`
    *   **Action:** **SELECT**s isolated instances explicitly requesting to be **DELETE**-ed by admin authorization keys.
*   **`GET /admin/ridefeedback-table`**
    *   **Tables:** `RideFeedback`
    *   **Action:** Extracts a complete unfiltered matrix overview of all table rows with a wildcard **SELECT**.
*   **`GET /admin/see-vehicle`**
    *   **Tables:** `Vehicle`
    *   **Action:** **SELECT**s globally available vehicle taxonomy variants stored inside the system context.
*   **`POST /admin/add-vehicle`**
    *   **Tables:** `Vehicle`
    *   **Action:** Appends customized transportation categories natively into the configuration matrix via an **INSERT**.