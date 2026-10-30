# Codebase Explanation: Parking Lot Management System

This document provides a comprehensive overview of the Parking Lot Management System codebase, explaining its architecture, core components, request flows, and key functionalities.

## 1. Overall Architecture

The application is built using **FastAPI**, a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints. It leverages **SQLAlchemy** as the Object Relational Mapper (ORM) for interacting with the database (SQLite by default). **Pydantic** is used for data validation and serialization. **APScheduler** handles background tasks for automated processes.

The project follows a modular structure, separating concerns into distinct directories and files:

*   **`app/main.py`**: The entry point of the FastAPI application.
*   **`app/database.py`**: Configures database connection and session management.
*   **`app/constants.py`**: Defines application-wide constants like Enums and timezone.
*   **`app/models/`**: Contains SQLAlchemy models representing database tables.
*   **`app/schemas/`**: Defines Pydantic models for request (input) and response (output) data validation and serialization.
*   **`app/routers/`**: Defines API endpoints (routes) and links them to service logic.
*   **`app/services/`**: Implements the business logic for each feature area.
*   **`app/utils/`**: Contains helper functions and utilities used across services.
*   **`app/scheduler.py`**: Manages the background task scheduler.

## 2. Core Components Explained

### `app/main.py`

*   **Purpose**: Initializes the FastAPI application, sets up JSON encoders, includes API routers, and manages application startup/shutdown events.
*   **Key points**:
    *   `app = FastAPI(lifespan=lifespan)`: Uses FastAPI's modern `lifespan` event handler to manage startup and shutdown processes.
    *   `app.json_encoders = {datetime: datetime.custom_datetime_encoder}`: Configures how `datetime` objects are serialized in JSON responses, ensuring timezone-aware IST formatting.
    *   `app.include_router(...)`: Registers all API endpoint groups (`auth`, `parking`, `booking`, `admin`).
    *   `Base.metadata.create_all(bind=engine)`: Creates all database tables defined by SQLAlchemy models when the application starts if they don't already exist.
    *   `lifespan` function: An `asynccontextmanager` that calls `start_scheduler()` on startup and `shutdown_scheduler()` on application shutdown, integrating the background tasks.

### `app/database.py`

*   **Purpose**: Sets up the SQLAlchemy engine and session factory.
*   **Key points**:
    *   `SQLALCHEMY_DATABASE_URL`: Defines the database connection string (e.g., `sqlite:///./app/data.db` for a SQLite file named `data.db` inside the `app` directory).
    *   `engine`: The SQLAlchemy engine that connects to the database.
    *   `SessionLocal`: A factory for creating database sessions. Each API request typically gets its own session.
    *   `Base`: The declarative base class for SQLAlchemy models.
    *   `get_db()`: A dependency injector function for FastAPI that provides a database session to route handlers and ensures it's closed afterward.

### `app/constants.py`

*   **Purpose**: Stores global constants.
*   **Key points**:
    *   `ParkingType` (Enum): `TW` (Two-Wheeler), `FW` (Four-Wheeler).
    *   `UserRole` (Enum): `ADMIN`, `PUBLIC`.
    *   `ParkingHistoryStatus` (Enum): `BOOKED`, `ACTIVE`, `COMPLETED`, `CANCELLED`.
    *   `IST`: Defines the `Asia/Kolkata` timezone using `pytz`, ensuring all datetime operations are consistent.

### `app/models/` (SQLAlchemy Models)

These files define the structure of your database tables.

*   **`app/models/user.py`**:
    *   `User` table: Stores `id`, `name`, `password` (hashed), and `role`.
    *   `parking_history`: A relationship indicating a user can have multiple parking history records.
*   **`app/models/parking_space.py`**:
    *   `ParkingSpace` table: Stores `id`, `level`, `twa` (two-wheeler available), and `fwa` (four-wheeler available).
*   **`app/models/parking_history.py`**:
    *   `ParkingHistory` table: Records individual parking sessions/bookings. Stores `id`, `user_id`, `level`, `type`, `vehicle_number`, `lot`, `in_time`, `scheduled_out_time` (nullable for immediate parking), `out_time` (nullable until checkout), `fee` (nullable until checkout), and `status`.

### `app/schemas/` (Pydantic Models)

These files define the data shape for API requests and responses.

*   **`app/schemas/user.py`**:
    *   `UserCreate`: For user registration (username, password).
*   **`app/schemas/parking_space.py`**:
    *   `ParkingSpaceCreate`: For admin to add new parking levels (level, twa, fwa).
    *   `AdminAvailabilityResponse`: Detailed availability for admins.
    *   `PublicAvailabilityResponse`: Simple boolean availability for public users.
*   **`app/schemas/parking_history.py`**:
    *   `ParkingLockRequest`, `ParkingLockResponse`: For locking a parking spot.
    *   `ParkingUnlockRequest`, `ParkingUnlockResponse`: For unlocking a parking spot and calculating fees.
    *   `BookingCreate`, `BookingResponse`: For pre-booking parking.
    *   `ParkingHistoryResponse`: Generic response model for parking history lists.

### `app/routers/` (API Endpoints)

These files define the API routes. Each router includes a `get_db` dependency to manage database sessions and `oauth2_scheme` for authentication.

*   **`app/routers/auth.py`**:
    *   `/register`: POST endpoint for new user registration.
    *   `/token`: POST endpoint for user login and JWT access token generation.
*   **`app/routers/parking.py`**:
    *   `/availability`: GET endpoint to check parking availability (different responses for ADMIN/PUBLIC).
    *   `/lock`: POST endpoint to assign and activate a parking spot.
    *   `/unlock`: POST endpoint to release a parking spot and calculate fees.
    *   `/my_history`: GET endpoint to view a user's parking history.
*   **`app/routers/booking.py`**:
    *   `/create`: POST endpoint for users to pre-book a parking spot.
    *   `/cancel/{booking_id}`: DELETE endpoint for users to cancel a future booking.
    *   `/my_bookings`: GET endpoint to view a user's active (booked) pre-bookings.
*   **`app/routers/admin.py`**:
    *   `/parking_space`: POST endpoint for admins to create new parking levels.
    *   `/history`: GET endpoint for admins to view all parking history records.
    *   `/history/{vehicle_number}`: GET endpoint for admins to view parking history for a specific vehicle.

### `app/services/` (Business Logic)

These files contain the core business logic, decoupled from the API layer. They interact with SQLAlchemy models and Pydantic schemas.

*   **`app/services/auth_service.py`**: Handles user registration, password hashing/verification, and JWT token creation.
*   **`app/services/booking_service.py`**: Manages the creation and cancellation of parking bookings.
*   **`app/services/parking_service.py`**: Handles parking lot availability checks, locking (entry), unlocking (exit), and fee calculation.
*   **`app/services/admin_service.py`**: Provides administrative functionalities like creating parking levels and viewing global history.

### `app/utils/` (Helper Functions)

*   **`app/utils/auth.py`**: Utility functions for password hashing (Bcrypt) and JWT token operations (creation, verification).
*   **`app/utils/datetime.py`**: Contains `custom_datetime_encoder` to ensure consistent datetime formatting in JSON responses.
*   **`app/utils/fee.py`**: `calculate_parking_fee()` function, which computes parking costs based on type, duration, and applies a late fee if `out_time` exceeds `scheduled_out_time`.
*   **`app/utils/parking.py`**: This is a critical utility file with many helper functions for parking logic:
    *   `find_parking_space()`: Retrieves a `ParkingSpace` record by level.
    *   `get_parking_lots_in_level()`: Generates a list of all possible lot numbers for a given level and type.
    *   `get_occupied_lots()`: Identifies lots currently occupied by `ACTIVE` parking sessions within a time window.
    *   `get_booked_lots()`: Identifies lots reserved by `BOOKED` sessions that conflict with a time window.
    *   `_get_available_lots_raw()`: (Private helper) The core logic for finding truly available lots by excluding `ACTIVE` and `BOOKED` conflicts. It applies `SELECT FOR UPDATE` for pessimistic locking and returns a raw list (can be empty).
    *   `get_available_lots()`: (Public API) Wraps `_get_available_lots_raw`, and raises an `HTTPException` if no lots are found.
    *   `try_assign_lot()`: **Crucial for concurrency**. This function attempts to get an available lot, picks a random candidate, and then handles retries with database locking (`SELECT FOR UPDATE` within `_get_available_lots_raw`) if it encounters a conflict (e.g., another concurrent request just took the lot).
    *   `decrease_parking_availability()`, `increase_parking_availability()`: Update the `twa`/`fwa` counts in `ParkingSpace`.
    *   `select_random_lot()`: Picks a random lot number from a given list.
    *   `check_vehicle_active_parking_session()`: Checks if a specific vehicle already has an active parking session.
    *   `auto_cancel_expired_bookings()`: Identifies and cancels `BOOKED` entries where `in_time` has passed plus a grace period.

### `app/scheduler.py`

*   **Purpose**: Sets up and manages the `APScheduler` background scheduler.
*   **Key points**:
    *   `scheduler = BackgroundScheduler()`: Initializes the scheduler.
    *   `scheduled_auto_cancel_job()`: A wrapper function that creates a dedicated database session, calls `auto_cancel_expired_bookings(db)` from `app.utils.parking`, and ensures the session is closed. This is vital for background tasks to have isolated DB contexts.
    *   `start_scheduler()`: Adds `scheduled_auto_cancel_job` to run at an `interval` (e.g., every 5 minutes) and starts the scheduler.
    *   `shutdown_scheduler()`: Gracefully stops the scheduler.

## 3. Flow of Content / Request Lifecycle

Let's trace a few typical request flows:

### A. User Registration/Login

1.  **Client (Browser/App)**: Sends POST request to `/register` or `/token`.
2.  **`app/main.py`**: Routes the request to `app/routers/auth.py`.
3.  **`app/routers/auth.py`**:
    *   Receives `UserCreate` schema or username/password.
    *   Calls `get_db()` dependency to get a `db: Session`.
    *   Calls `auth_service.register_user()` or `auth_service.login_user()`.
4.  **`app/services/auth_service.py`**:
    *   `register_user()`: Hashes password, checks for existing username, creates `User` model, `db.add()`, `db.commit()`, `db.refresh()`.
    *   `login_user()`: Queries `User` by username, verifies password, generates JWT access token using `app.utils.auth.create_access_token()`.
5.  **`app/routers/auth.py`**: Returns the appropriate response (e.g., success message, JWT token).

### B. Creating a Booking

1.  **Client**: Sends POST request to `/booking/create` with `BookingCreate` data (vehicle details, level, type, start/end times) and JWT token.
2.  **`app/main.py`**: Routes to `app/routers/booking.py`.
3.  **`app/routers/booking.py`**:
    *   Authenticates user via JWT.
    *   Gets `db: Session`.
    *   Calls `booking_service.create_booking()`.
4.  **`app/services/booking_service.py`**:
    *   Converts `request.start_time` and `request.end_time` to IST-aware datetimes.
    *   Validates booking times (future, end after start).
    *   Calls `app.utils.parking.find_parking_space()` to ensure level exists.
    *   **Concurrency Handling**: Calls `app.utils.parking.try_assign_lot()` with the desired booking `start_time` and `end_time`.
        *   `try_assign_lot` internally calls `_get_available_lots_raw` (which uses `SELECT FOR UPDATE` to lock relevant `ParkingHistory` rows).
        *   It will retry `max_retries` times if the lot selection fails due to a concurrency conflict.
        *   It returns the `selected_lot_number` that was successfully secured.
    *   Creates a `ParkingHistory` model with `status=BOOKED`, including the `selected_lot_number`.
    *   `db.add()`, `db.commit()`, `db.refresh()`.
5.  **`app/routers/booking.py`**: Returns `BookingResponse`.

### C. Locking a Parking Spot (Activating a Booking or Immediate Parking)

1.  **Client**: Sends POST request to `/parking/lock` with `ParkingLockRequest` (vehicle details, level, type) and JWT token.
2.  **`app/main.py`**: Routes to `app/routers/parking.py`.
3.  **`app/routers/parking.py`**:
    *   Authenticates user.
    *   Gets `db: Session`.
    *   Calls `parking_service.lock_parking()`.
4.  **`app/services/parking_service.py`**:
    *   Calls `app.utils.parking.find_parking_space()` to get `ParkingSpace` details.
    *   Calls `app.utils.parking.check_vehicle_active_parking_session()` to prevent a vehicle from having multiple active sessions.
    *   Queries for an existing `BOOKED` `ParkingHistory` record for the user/vehicle.
    *   **If a `booking_record` exists**:
        *   Validates booking: ensures `current_time` is within `booking_in_time` and `scheduled_out_time`.
        *   **Concurrency Handling (Original Lot Check)**: Calls `app.utils.parking.get_occupied_lots()` and `app.utils.parking.get_booked_lots()` to see if the `booking_record.lot` is still genuinely free *at `current_time`* (or has no conflicting future bookings).
        *   If the original `booking_record.lot` is **unavailable**:
            *   Calls `app.utils.parking.try_assign_lot()` to find an *alternative* available lot for the remainder of the booking duration (or next hour). This includes retry logic and database locking.
            *   Updates `booking_record.lot` with the newly assigned lot.
        *   Sets `booking_record.status = ACTIVE`.
        *   `parking_record_to_commit` is set to `booking_record`.
    *   **If NO `booking_record` (Immediate Parking)**:
        *   **Concurrency Handling**: Calls `app.utils.parking.try_assign_lot()` to find an available lot for immediate parking (e.g., for the next 1 hour).
        *   Creates a `new_history_record` with `status=ACTIVE`, `in_time=current_time`, and `scheduled_out_time=None`.
        *   `parking_record_to_commit` is set to `new_history_record`.
    *   Calls `app.utils.parking.decrease_parking_availability()` to decrement `twa`/`fwa` counts in `ParkingSpace`.
    *   `db.add(parking_record_to_commit)`, `db.commit()`, `db.refresh()`.
5.  **`app/routers/parking.py`**: Returns `ParkingLockResponse`.

### D. Unlocking a Parking Spot

1.  **Client**: Sends POST request to `/parking/unlock` with `ParkingUnlockRequest` (vehicle number, level, lot) and JWT token.
2.  **`app/main.py`**: Routes to `app/routers/parking.py`.
3.  **`app/routers/parking.py`**:
    *   Authenticates user.
    *   Gets `db: Session`.
    *   Calls `parking_service.unlock_parking()`.
4.  **`app/services/parking_service.py`**:
    *   Queries for the specific `ACTIVE` `ParkingHistory` record matching the request details and user. Raises `HTTP 404` if not found.
    *   Calls `app.utils.parking.find_parking_space()` to get `ParkingSpace` details.
    *   Sets `history.out_time = datetime.now(IST)`.
    *   Calls `app.utils.fee.calculate_parking_fee()` to determine the final fee.
    *   Sets `history.status = COMPLETED`.
    *   Calls `app.utils.parking.increase_parking_availability()` to increment `twa`/`fwa` counts.
    *   `db.commit()`, `db.refresh()`.
5.  **`app/routers/parking.py`**: Returns `ParkingUnlockResponse`.

## 4. Concurrency Handling (`try_assign_lot` with `SELECT FOR UPDATE`)

This is a critical part of the system's robustness, ensuring that two simultaneous requests don't inadvertently claim the same parking lot.

1.  **`_get_available_lots_raw()`**: When this helper function queries for conflicting `ParkingHistory` records (both `ACTIVE` and `BOOKED`), it uses `query(...).with_for_update(nowait=True, of=ParkingHistory)`.
    *   **`with_for_update()`**: This tells the database to acquire a pessimistic lock on the rows that match the query. If a row is part of a conflict, it gets locked.
    *   **`nowait=True`**: This is essential for a responsive API. If the database cannot acquire the lock immediately (because another transaction already holds it), it will raise an `OperationalError` rather than waiting.
    *   **`of=ParkingHistory`**: Specifies that the lock is on the `ParkingHistory` table.
2.  **`try_assign_lot()`**:
    *   This function wraps the call to `_get_available_lots_raw()` within a `try...except OperationalError` block and a retry loop (`max_retries = 5`).
    *   If `_get_available_lots_raw()` successfully returns a list, it means that (within the current transaction) all conflicting rows were either found and locked, or didn't exist. The `try_assign_lot` then picks a `random.choice()` from this list. Since the conflicts were locked, the chosen lot is guaranteed available for this transaction.
    *   If `_get_available_lots_raw()` (due to `nowait=True`) raises an `OperationalError` (because another concurrent transaction holds a lock on a critical row), `try_assign_lot` catches this. It then performs a `db.rollback()` (crucial to release any partial locks and clear the session state) and retries the entire process, hoping the lock is released on the next attempt.
    *   If all retries fail, it raises a `HTTPException` to the client.

This mechanism ensures that the act of determining availability and selecting a lot is as atomic as possible without requiring global database locks, effectively mitigating race conditions for lot assignments.

## 5. Background Scheduling (Automatic Booking Cancellation)

The application uses `APScheduler` to handle automatic cancellation of no-show bookings.

1.  **`app/scheduler.py`**: Defines the `BackgroundScheduler` and the job.
2.  **`scheduled_auto_cancel_job()`**: This function is the actual task executed by the scheduler. It creates its own isolated database session (`db = SessionLocal()`) to prevent conflicts with ongoing API request transactions. It then calls `auto_cancel_expired_bookings(db)`.
3.  **`auto_cancel_expired_bookings(db)` in `app/utils/parking.py`**:
    *   It defines a `grace_period = timedelta(minutes=15)`.
    *   It queries the database for `ParkingHistory` entries where `status == BOOKED` AND `in_time < (current_time - grace_period)`. This identifies bookings whose start time has passed and the grace period for a no-show has also elapsed.
    *   For each such booking, it updates its `status` to `CANCELLED` and commits the changes.
4.  **`app/main.py` (`lifespan` function)**:
    *   `start_scheduler()` is called during `app.on_event("startup")`.
    *   The scheduler is configured to run `scheduled_auto_cancel_job` every 5 minutes.
    *   `shutdown_scheduler()` is called during `app.on_event("shutdown")` for graceful termination.

This background task ensures that the system proactively frees up parking spots from no-show users, improving overall lot utilization without requiring direct user interaction to trigger the cancellation.

## 6. Datetime Management

The application strictly adheres to using **timezone-aware datetimes** in the `Asia/Kolkata` (IST) timezone.

*   `IST = pytz.timezone("Asia/Kolkata")` is defined in `app/constants.py`.
*   All new `datetime` objects representing "current time" are created as `datetime.now(IST)`.
*   Incoming `datetime` objects from API requests (via Pydantic schemas) are immediately converted to `astimezone(IST)`.
*   `datetime` objects retrieved from the database (which are typically naive by default) are explicitly converted to `astimezone(IST)` before being used in comparisons or calculations with other timezone-aware datetimes.
*   The `custom_datetime_encoder` ensures that all `datetime` objects in JSON responses are formatted consistently in IST.

This consistent approach prevents common timezone-related bugs and ensures accurate time-based calculations (like parking duration, conflicts, and grace periods).