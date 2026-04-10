"""
migration.py  —  End-to-End Sharded Migration
===============================================

Hybrid Partitioning:
  HASH-BASED  : Members, MemberStats          key → SHA256(MemberID) % 3
                ActiveRides, RideHistory       key → SHA256(AdminID)  % 3
  DIRECTORY   : BookingRequest, MessageHistory,
                RidePassengerMap, MemberRating,
                RideFeedback, Cancellation     key → RideID (JSON lookup)
  REPLICATED  : Vehicle                        → all 3 shards

Migration order (FK-safe):
  Phase 1 — no dependencies  : Member, Vehicle, MemberStat
  Phase 2 — build directory  : ActiveRide, RideHistory
  Phase 3 — consume directory: BookingRequest, MessageHistory,
                               RidePassengerMap, MemberRating,
                               RideFeedback, Cancellation
"""

import csv
import hashlib
import json
import os

from sqlalchemy import create_engine, Integer, Float, Boolean, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.mysql import insert as mysql_insert

from models import (
    Base,
    Member,
    ActiveRide,
    BookingRequest,
    MessageHistory,
    MemberStat,
    RidePassengerMap,
    Vehicle,
    MemberRating,
    RideFeedback,
    RideHistory,
    Cancellation,
)

# Shard connection engines
SHARD_URLS = {
    0: "mysql+pymysql://root:rootpass@10.7.59.24:3307/RideShare",
    1: "mysql+pymysql://root:rootpass@10.7.59.24:3308/RideShare",
    2: "mysql+pymysql://root:rootpass@10.7.59.24:3309/RideShare",
}

shard_engines  = {sid: create_engine(url, pool_pre_ping=True) for sid, url in SHARD_URLS.items()}
shard_sessions = {sid: sessionmaker(bind=eng, autocommit=False, autoflush=False)
                  for sid, eng in shard_engines.items()}

# Shard config
SHARD_CONFIG = {
    Member:          {"method": "hash",      "key": "MemberID"},
    MemberStat:      {"method": "hash",      "key": "MemberID"},
    ActiveRide:      {"method": "hash",      "key": "AdminID"},
    RideHistory:     {"method": "hash",      "key": "AdminID"},

    BookingRequest:  {"method": "directory", "key": "RideID"},
    MessageHistory:  {"method": "directory", "key": "RideID"},
    RidePassengerMap:{"method": "directory", "key": "RideID"},
    MemberRating:    {"method": "directory", "key": "RideID"},
    RideFeedback:    {"method": "directory", "key": "RideID"},
    Cancellation:    {"method": "hash",      "key": "MemberID"},

    Vehicle:         {"method": "replicate", "key": None},
}

DIRECTORY_BUILDERS = {ActiveRide, RideHistory, Cancellation}  # these write to the directory

# Tables that have a RideID column (used during pre-scan)
RIDEID_COLUMN_INDEX = {
    # model              : column name that holds RideID in flat file
    ActiveRide:          "RideID",
    RideHistory:         "RideID",
    BookingRequest:      "RideID",
    MessageHistory:      "RideID",
    RidePassengerMap:    "RideID",
    MemberRating:        "RideID",
    RideFeedback:        "RideID",
    Cancellation:        "RideID",   # scanned to register cancelled RideIDs in directory
}

TABLES_DIR     = "tables"
DIRECTORY_FILE = "ride_shard_directory.json"

# FK-check helpers

def disable_fk_checks() -> None:
    print("\n[FK] Disabling foreign_key_checks on all shards...")
    for sid, engine in shard_engines.items():
        with engine.connect() as conn:
            conn.execute(text("SET foreign_key_checks = 0"))
            conn.commit()
        print(f"  ✓ Shard {sid} — foreign_key_checks = 0")


def enable_fk_checks() -> None:
    print("\n[FK] Re-enabling foreign_key_checks on all shards...")
    for sid, engine in shard_engines.items():
        with engine.connect() as conn:
            conn.execute(text("SET foreign_key_checks = 1"))
            conn.commit()
        print(f"  ✓ Shard {sid} — foreign_key_checks = 1")

# Directory helpers

def load_directory() -> dict:
    if os.path.exists(DIRECTORY_FILE):
        with open(DIRECTORY_FILE, "r") as f:
            data = json.load(f)
        print(f"[DIR] Loaded '{DIRECTORY_FILE}' — {len(data)} existing entries")
        return data
    print(f"[DIR] '{DIRECTORY_FILE}' not found — starting fresh")
    return {}


def save_directory(directory: dict) -> None:
    with open(DIRECTORY_FILE, "w") as f:
        json.dump(directory, f, indent=2)


def register_ride(ride_id: str, shard_id: int, directory: dict) -> None:
    directory[ride_id] = shard_id
    save_directory(directory)


def lookup_ride(ride_id: str, directory: dict) -> int:
    """
    Return shard_id for a RideID.
    If not in directory (orphaned / cancelled ride), fall back to UUID hash
    and register it so subsequent tables are routed consistently.
    """
    if ride_id in directory:
        return directory[ride_id]

    shard_id = int(hashlib.sha256(ride_id.encode('utf-8')).hexdigest(), 16) % 3
    print(
        f"  [WARN] RideID '{ride_id}' not in directory "
        f"(cancelled ride) — SHA256 hash fallback → Shard {shard_id}"
    )
    register_ride(ride_id, shard_id, directory)
    return shard_id

# Pre-scan: build a complete directory BEFORE migration starts

def build_full_directory(directory: dict) -> None:
    """
    Pre-scan every CSV file that contains a RideID column.

    Priority:
      1. ActiveRides / RideHistory  →  shard = AdminID % 3  (authoritative)
      2. All other tables           →  UUID hash fallback (for cancelled rides)

    This ensures every RideID is in the directory before Phase 3 tables
    are processed, eliminating KeyError on orphaned RideIDs.
    """
    print("\n[DIR] Pre-scanning all CSVs to build complete RideID directory...")

    # Each entry: (model, column used as shard key)
    pass1_sources = [
        (ActiveRide,  "AdminID"),    # shard = SHA256(AdminID)  % 3
        (RideHistory, "AdminID"),    # shard = SHA256(AdminID)  % 3
        (Cancellation,"MemberID"),   # shard = SHA256(MemberID) % 3
    ]

    for model, shard_col in pass1_sources:
        filepath = os.path.join(TABLES_DIR, model.__tablename__ + ".csv")
        if not os.path.exists(filepath):
            print(f"  [SKIP] {filepath} not found")
            continue

        columns    = get_columns(model)
        shard_idx  = columns.index(shard_col)
        ride_idx   = columns.index("RideID")

        count = 0
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            for row in reader:
                if len(row) < max(shard_idx, ride_idx) + 1:
                    continue
                ride_id   = row[ride_idx].strip()
                shard_val = row[shard_idx].strip()
                if ride_id and ride_id not in directory:
                    directory[ride_id] = int(hashlib.sha256(shard_val.encode('utf-8')).hexdigest(), 16) % 3
                    count += 1

        print(f"  {model.__tablename__} (key={shard_col}): registered {count} new RideID(s)")

    for model, ride_col in RIDEID_COLUMN_INDEX.items():
        if model in (ActiveRide, RideHistory):
            continue  # already handled above

        filepath = os.path.join(TABLES_DIR, model.__tablename__ + ".csv")
        if not os.path.exists(filepath):
            continue

        columns  = get_columns(model)
        ride_idx = columns.index(ride_col)

        count = 0
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            for row in reader:
                if len(row) < ride_idx + 1:
                    continue
                ride_id = row[ride_idx].strip()
                if ride_id and ride_id not in directory:
                    shard_id = int(hashlib.sha256(ride_id.encode('utf-8')).hexdigest(), 16) % 3
                    directory[ride_id] = shard_id
                    count += 1

        if count:
            print(
                f"  {model.__tablename__}: {count} orphaned RideID(s) "
                f"assigned via SHA256 hash (cancelled rides)"
            )

    save_directory(directory)
    print(f"[DIR] Directory complete — {len(directory)} total RideID(s)\n")

# Generic row helpers

def get_columns(model) -> list:
    return [col.key for col in inspect(model).mapper.columns]


def cast_row(model, raw: dict) -> dict:
    casted = {}
    for col in inspect(model).mapper.columns:
        val = raw.get(col.key)
        if val in (None, "", "NULL", "None", "null"):
            casted[col.key] = None
            continue
        if isinstance(col.type, Integer):
            casted[col.key] = int(val)
        elif isinstance(col.type, Float):
            casted[col.key] = float(val)
        elif isinstance(col.type, Boolean):
            casted[col.key] = val.strip().lower() in ("1", "true", "yes")
        else:
            casted[col.key] = val
    return casted


def read_flat_file(model, first_row_only: bool = False) -> list:
    filepath = os.path.join(TABLES_DIR, model.__tablename__ + ".csv")
    if not os.path.exists(filepath):
        print(f"  [SKIP] File not found: {filepath}")
        return []

    columns = get_columns(model)
    rows = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip header
        for line_no, raw_row in enumerate(reader, start=2):
            if len(raw_row) != len(columns):
                print(
                    f"  [WARN] {model.__tablename__} line {line_no}: "
                    f"expected {len(columns)} cols, got {len(raw_row)} — skipping"
                )
                continue
            rows.append(cast_row(model, dict(zip(columns, raw_row))))
            if first_row_only:
                break
    return rows


def insert_ignore(model, row: dict, session: Session) -> None:
    """
    Upsert: insert new rows, update existing rows with CSV values.
    """
    stmt = mysql_insert(model.__table__).values(**row)

    update_cols = {
        col.name: stmt.inserted[col.name]
        for col in model.__table__.columns
        if not col.primary_key
    }

    session.execute(stmt.on_duplicate_key_update(**update_cols))


# Shard routing

def resolve_shard(model, row: dict, directory: dict) -> int | None:
    cfg    = SHARD_CONFIG[model]
    method = cfg["method"]
    key    = cfg["key"]

    if method == "hash":
        val_str = str(row[key])
        shard_id = int(hashlib.sha256(val_str.encode('utf-8')).hexdigest(), 16) % 3
        print(f"  [HASH] {key}={val_str}  →  SHA256 % 3 = {shard_id}  →  Shard {shard_id}")
        return shard_id

    if method == "directory":
        ride_id  = row[key]
        shard_id = lookup_ride(ride_id, directory)
        print(f"  [DIR ] {key}={ride_id}  →  Shard {shard_id}")
        return shard_id

    return None  # replicate

# Core migration function

def migrate_table(model, directory: dict, first_row_only: bool = False) -> None:
    cfg        = SHARD_CONFIG[model]
    table_name = model.__tablename__

    print(f"\n{'='*60}")
    print(f"Table  : {table_name}")
    print(f"Method : {cfg['method'].upper()}  |  Key: {cfg['key'] or '—'}")
    print(f"{'='*60}")

    rows = read_flat_file(model, first_row_only=first_row_only)
    if not rows:
        return

    sessions = {sid: shard_sessions[sid]() for sid in shard_sessions}
    inserted = {0: 0, 1: 0, 2: 0}

    try:
        for row in rows:
            shard_id = resolve_shard(model, row, directory)

            if shard_id is None:
                for sid, sess in sessions.items():
                    insert_ignore(model, row, sess)
                    inserted[sid] += 1
                print(f"  → ALL shards | {row}")
            else:
                insert_ignore(model, row, sessions[shard_id])
                inserted[shard_id] += 1
                print(f"  → Shard {shard_id} | {row}")

                if model in DIRECTORY_BUILDERS:
                    register_ride(str(row["RideID"]), shard_id, directory)

        for sid, sess in sessions.items():
            sess.commit()
            print(f"  ✓ Shard {sid} committed — {inserted[sid]} row(s)")

    except Exception as exc:
        for sess in sessions.values():
            sess.rollback()
        print(f"  [ERROR] Rolling back all shards: {exc}")
        raise

    finally:
        for sess in sessions.values():
            sess.close()

# Connection test

def test_connections() -> bool:
    print("=== Testing shard connections ===")
    all_ok = True
    for sid, engine in shard_engines.items():
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"  ✓ Shard {sid}  ({SHARD_URLS[sid]})")
        except Exception as exc:
            print(f"  ✗ Shard {sid} UNREACHABLE: {exc}")
            all_ok = False
    return all_ok

def truncate_all_tables() -> None:
    print("\n=== Wiping Existing Data ===")
    tables = [
        Member, Vehicle, MemberStat, ActiveRide, RideHistory, Cancellation,
        BookingRequest, MessageHistory, RidePassengerMap, MemberRating, RideFeedback
    ]
    for sid, engine in shard_engines.items():
        try:
            with engine.connect() as conn:
                conn.execute(text("SET foreign_key_checks = 0"))
                for model in tables:
                    conn.execute(text(f"TRUNCATE TABLE `{model.__tablename__}`"))
                conn.execute(text("SET foreign_key_checks = 1"))
                conn.commit()
            print(f"  ✓ Shard {sid} — all tables truncated.")
        except Exception as exc:
            print(f"  ✗ Shard {sid} failed to truncate: {exc}")

from collections import Counter
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

# Normalization helpers

def _normalize_numeric(v):
    """
    Normalize numeric values so equivalent values compare equal:
    2, 2.0, Decimal('2.0') -> '2'
    0.0 -> '0'
    2.500 -> '2.5'
    """
    try:
        d = Decimal(str(v)).normalize()
        s = format(d, "f")
        return s.rstrip("0").rstrip(".") if "." in s else s
    except (InvalidOperation, ValueError, TypeError):
        return str(v).strip()

def normalize_value(v):
    if v is None:
        return None

    if isinstance(v, bytes):
        v = v.decode("utf-8", errors="replace")

    if isinstance(v, bool):
        return "1" if v else "0"

    if isinstance(v, datetime):
        return v.isoformat(sep=" ", timespec="seconds")

    if isinstance(v, date):
        return v.isoformat()

    if isinstance(v, (int, float, Decimal)):
        return _normalize_numeric(v)

    if isinstance(v, str):
        s = v.strip()
        # If it looks numeric, normalize it too
        try:
            if s and any(ch in s for ch in ".eE"):
                return _normalize_numeric(s)
        except Exception:
            pass
        return s

    return str(v).strip()


def get_pk_columns(model):
    pk_cols = [col.key for col in inspect(model).primary_key]
    return pk_cols if pk_cols else get_columns(model)


def row_signature(model, row_dict):
    cols = get_columns(model)
    return tuple(normalize_value(row_dict.get(col)) for col in cols)


def pk_signature(model, row_dict):
    pk_cols = get_pk_columns(model)
    return tuple(normalize_value(row_dict.get(col)) for col in pk_cols)


def fetch_table_rows(engine, table_name):
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT * FROM `{table_name}`"))
        return [dict(row) for row in result.mappings().all()]


def compare_row_values(model, csv_row: dict, shard_row: dict):
    diffs = []
    for col in get_columns(model):
        csv_val = normalize_value(csv_row.get(col))
        shard_val = normalize_value(shard_row.get(col))
        if csv_val != shard_val:
            diffs.append((col, csv_val, shard_val))
    return diffs

def format_row(row: dict, model) -> str:
    cols = get_columns(model)
    return "{" + ", ".join(f"{c}={normalize_value(row.get(c))}" for c in cols) + "}"

def print_row_differences(model, pk, csv_row, shard_row, shard_id):
    diffs = compare_row_values(model, csv_row, shard_row)

    print(f"       PK: {pk}")
    print(f"       CSV row   : {format_row(csv_row, model)}")
    print(f"       Shard {shard_id}: {format_row(shard_row, model)}")

    if diffs:
        print("       Column mismatches:")
        for col, csv_val, shard_val in diffs:
            print(f"         - {col}: CSV='{csv_val}' | Shard {shard_id}='{shard_val}'")
    else:
        print("       No column-level difference found after normalization.")

    print("       Suggested fix: truncate MemberStats on all shards and rerun migration,")
    print("       or update the stale shard row so it matches the CSV exactly.")

# Integrity Check

def test_integrity():
    print("\n=== Integrity Check (No loss / no duplication) ===\n")

# Table-by-table: check all migrated tables for integrity.
    tables = [
        Member,
        MemberStat,
        ActiveRide,
        RideHistory,
        BookingRequest,
        MessageHistory,
        RidePassengerMap,
        MemberRating,
        RideFeedback,
        Cancellation,
        Vehicle,
    ]

    for model in tables:
        table_name = model.__tablename__

        print(f"\nTable: {table_name}")

        csv_rows = read_flat_file(model)
        csv_count = len(csv_rows)

        csv_by_pk = {}
        csv_pk_counts = Counter()
        for row in csv_rows:
            pk = pk_signature(model, row)
            csv_by_pk[pk] = row
            csv_pk_counts[pk] += 1

        dup_csv = [pk for pk, c in csv_pk_counts.items() if c > 1]
        if dup_csv:
            print(f"  ❌ CSV duplicate primary keys: {len(dup_csv)}")
            for pk in dup_csv[:10]:
                print(f"     - {pk}")

        total_rows = 0
        seen_pk_counts = Counter()
        combined_by_pk = {}
        pk_to_shard = {}
        any_shard_error = False

        for sid, engine in shard_engines.items():
            try:
                shard_rows = fetch_table_rows(engine, table_name)
                shard_count = len(shard_rows)
                total_rows += shard_count
                print(f"  Shard {sid}: {shard_count} rows")

                shard_pk_counts = Counter()
                for row in shard_rows:
                    pk = pk_signature(model, row)
                    shard_pk_counts[pk] += 1
                    seen_pk_counts[pk] += 1
                    combined_by_pk[pk] = row
                    pk_to_shard[pk] = sid

                dup_inside = [pk for pk, c in shard_pk_counts.items() if c > 1]
                if dup_inside:
                    print(f"  ❌ Shard {sid}: {len(dup_inside)} duplicated primary key(s) inside this shard")
                    for pk in dup_inside[:10]:
                        print(f"     - {pk}")

            except Exception as e:
                print(f"  ❌ Shard {sid}: ERROR ({e})")
                any_shard_error = True

        if any_shard_error:
            return

        if model == Vehicle:
            if total_rows != csv_count * len(shard_engines):
                print(f"  ❌ COUNT MISMATCH (Replicated): CSV={csv_count} (expected {csv_count * len(shard_engines)} total), Shards={total_rows}")
            else:
                print(f"  ✅ Count matches expected for replicated table ({total_rows})")
            print("  ✅ Skipping cross-shard duplication check for replicated table")
        else:
            if total_rows != csv_count:
                print(f"  ❌ COUNT MISMATCH: CSV={csv_count}, Shards={total_rows}")
            else:
                print(f"  ✅ Count matches CSV ({csv_count})")

            cross_dupes = [pk for pk, c in seen_pk_counts.items() if c > 1]
            if cross_dupes:
                print(f"  ❌ DUPLICATION: {len(cross_dupes)} primary key(s) appear in more than one shard")
                for pk in cross_dupes[:10]:
                    print(f"     - {pk}")
            else:
                print("  ✅ No cross-shard duplication")

        missing = set(csv_by_pk) - set(combined_by_pk)
        extra = set(combined_by_pk) - set(csv_by_pk)
        mismatched = [
            pk for pk in (set(csv_by_pk) & set(combined_by_pk))
            if row_signature(model, csv_by_pk[pk]) != row_signature(model, combined_by_pk[pk])
        ]

        if missing or extra or mismatched:
            print("  ❌ DATA MISMATCH with CSV")

            if missing:
                print(f"     → Missing rows: {len(missing)}")
                for pk in list(missing)[:10]:
                    print(f"       - Missing PK={pk}")

            if extra:
                print(f"     → Extra rows: {len(extra)}")
                for pk in list(extra)[:10]:
                    print(f"       - Extra PK={pk} (present in shard, not in CSV)")

            if mismatched:
                print(f"     → Same primary key, different values: {len(mismatched)}")
                print("     Detailed differences:")
                for pk in mismatched:
                    sid = pk_to_shard.get(pk, "?")
                    print(f"       PK={pk} found on Shard {sid}")
                    print_row_differences(
                        model,
                        pk,
                        csv_by_pk[pk],
                        combined_by_pk[pk],
                        sid,
                    )
        else:
            print("  ✅ Data matches CSV exactly")

# Entry point

def main():
    print("=== Shard Migration — End to End ===\n")

    if not test_connections():
        print("\n[ABORT] Fix shard connections and retry.")
        return
        
    truncate_all_tables()

    # Load or initialise directory
    directory = load_directory()

    # Pre-scan ALL CSVs to populate directory completely before any inserts.
    build_full_directory(directory)

    disable_fk_checks()

    try:
        # Phase 1 — no FK dependencies
        migrate_table(Member,          directory)
        migrate_table(Vehicle,         directory)   # replicated
        migrate_table(MemberStat,      directory)
        migrate_table(Cancellation,    directory)   # hash on MemberID

        # Phase 2 — build RideID directory (authoritative shard assignment)
        migrate_table(ActiveRide,      directory)   # SHA256(AdminID)  % 3 → registers RideID
        migrate_table(RideHistory,     directory)   # SHA256(AdminID)  % 3 → registers RideID
        migrate_table(Cancellation,    directory)   # SHA256(MemberID) % 3 → registers RideID

        # Phase 3 — directory consumers (directory is now fully populated)
        migrate_table(BookingRequest,  directory)
        migrate_table(MessageHistory,  directory)
        migrate_table(RidePassengerMap,directory)
        migrate_table(MemberRating,    directory)
        migrate_table(RideFeedback,    directory)

    finally:
        enable_fk_checks()

    print("\n=== Migration complete ===")
    test_integrity()


if __name__ == "__main__":
    main()