
from pathlib import Path
import sqlite3
import csv
import duckdb

# ==================================================
# 1. PROJECT PATHS
# ==================================================
ROOT = Path(__file__).resolve().parent.parent
SOURCE_DB = ROOT / "data" / "vct_reference.duckdb"
WAREHOUSE_DIR = ROOT / "warehouse"
REPORT_DIR = ROOT / "reports"

WAREHOUSE_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

TARGET_DB = WAREHOUSE_DIR / "valorant_warehouse.db"

if not SOURCE_DB.exists():
    raise FileNotFoundError(f"Source database not found: {SOURCE_DB}")


# ==================================================
# 2. HELPER FUNCTIONS
# ==================================================
def fetch_rows(connection, query):
    return connection.execute(query).fetchall()



def insert_rows(connection, table, columns, rows):
    import json

    if not rows:
        return 0

    column_names = ", ".join(f'"{column}"' for column in columns)
    placeholders = ", ".join("?" for _ in columns)

    query = (
        f'INSERT OR REPLACE INTO "{table}" '
        f'({column_names}) VALUES ({placeholders})'
    )

    def make_sqlite_compatible(value):
        # SQLite cannot directly store Python lists or dictionaries.
        if isinstance(value, (list, dict)):
            return json.dumps(value, default=str)

        # Convert dates and timestamps into strings.
        if hasattr(value, "isoformat"):
            return value.isoformat()

        # Convert booleans into SQLite-compatible integers.
        if isinstance(value, bool):
            return int(value)

        return value

    converted_rows = [
        tuple(make_sqlite_compatible(value) for value in row)
        for row in rows
    ]

    connection.executemany(query, converted_rows)
    return len(converted_rows)



# ==================================================
# 3. CONNECT TO DATABASES
# ==================================================
print("Connecting to source database...")

source = duckdb.connect(str(SOURCE_DB), read_only=True)
target = sqlite3.connect(str(TARGET_DB))

try:
    # --------------------------------------------------
    # 4. CREATE WAREHOUSE TABLES
    # --------------------------------------------------
    print("Creating warehouse tables...")

    target.executescript("""
        DROP TABLE IF EXISTS fact_round;
        DROP TABLE IF EXISTS fact_player_map;
        DROP TABLE IF EXISTS fact_map;
        DROP TABLE IF EXISTS fact_match;

        DROP TABLE IF EXISTS dim_date;
        DROP TABLE IF EXISTS dim_event;
        DROP TABLE IF EXISTS dim_map;
        DROP TABLE IF EXISTS dim_player;
        DROP TABLE IF EXISTS dim_team;

        CREATE TABLE dim_team (
            team_id INTEGER PRIMARY KEY,
            team_name TEXT,
            country TEXT
        );

        CREATE TABLE dim_player (
            player_id INTEGER PRIMARY KEY,
            player_name TEXT,
            country TEXT
        );

        CREATE TABLE dim_map (
            map_key INTEGER PRIMARY KEY,
            map_name TEXT UNIQUE
        );

        CREATE TABLE dim_event (
            event_id INTEGER PRIMARY KEY,
            event_name TEXT,
            event_slug TEXT
        );

        CREATE TABLE dim_date (
            date_key INTEGER PRIMARY KEY,
            full_date TEXT UNIQUE,
            year INTEGER,
            month INTEGER,
            month_name TEXT,
            quarter INTEGER
        );

        CREATE TABLE fact_match (
            match_id TEXT PRIMARY KEY,
            date_key INTEGER,
            event_id INTEGER,
            team0_id INTEGER,
            team1_id INTEGER,
            score0 INTEGER,
            score1 INTEGER,
            winner_team_id INTEGER,
            status TEXT,
            match_format TEXT,
            region TEXT,
            is_international INTEGER
        );

        CREATE TABLE fact_map (
            match_id TEXT,
            game_id TEXT,
            map_key INTEGER,
            picked_by_team INTEGER,
            duration TEXT,
            score0 INTEGER,
            score1 INTEGER,
            performance_available INTEGER,
            economy_available INTEGER,
            PRIMARY KEY (match_id, game_id)
        );

        CREATE TABLE fact_player_map (
            player_id INTEGER,
            match_id TEXT,
            game_id TEXT,
            team_idx INTEGER,
            team_id INTEGER,
            agents TEXT,
            rating REAL,
            acs INTEGER,
            adr INTEGER,
            kills INTEGER,
            deaths INTEGER,
            assists INTEGER,
            first_kills INTEGER,
            first_deaths INTEGER,
            kast INTEGER,
            headshot_pct INTEGER,
            clutches_1v1 INTEGER,
            clutches_1v2 INTEGER,
            clutches_1v3 INTEGER,
            clutches_1v4 INTEGER,
            clutches_1v5 INTEGER,
            PRIMARY KEY (player_id, match_id, game_id)
        );

        CREATE TABLE fact_round (
            match_id TEXT,
            game_id TEXT,
            round_num INTEGER,
            winner_team INTEGER,
            side TEXT,
            outcome TEXT,
            loadout_t0 INTEGER,
            loadout_t1 INTEGER,
            bank_t0 INTEGER,
            bank_t1 INTEGER,
            PRIMARY KEY (match_id, game_id, round_num)
        );
    """)

    # --------------------------------------------------
    # 5. LOAD TEAM DIMENSION
    # --------------------------------------------------
    print("Loading teams...")

    rows = fetch_rows(source, """
        SELECT team_id, team_name, country
        FROM teams
        WHERE team_id IS NOT NULL
    """)

    insert_rows(
        target, "dim_team",
        ["team_id", "team_name", "country"],
        rows
    )

    # --------------------------------------------------
    # 6. LOAD PLAYER DIMENSION
    # --------------------------------------------------
    print("Loading players...")

    rows = fetch_rows(source, """
        SELECT player_id, player_name, country
        FROM players
        WHERE player_id IS NOT NULL
    """)

    insert_rows(
        target, "dim_player",
        ["player_id", "player_name", "country"],
        rows
    )

    # --------------------------------------------------
    # 7. LOAD MAP DIMENSION
    # --------------------------------------------------
    print("Loading maps...")

    rows = fetch_rows(source, """
        SELECT DISTINCT map_name
        FROM maps
        WHERE map_name IS NOT NULL
        ORDER BY map_name
    """)

    insert_rows(
        target, "dim_map",
        ["map_name"],
        [(row[0],) for row in rows]
    )

    # IMPORTANT:
    # Read map IDs from SQLite, not from DuckDB.
    map_key_lookup = {
        name: key
        for key, name in target.execute(
            "SELECT map_key, map_name FROM dim_map"
        ).fetchall()
    }

    # --------------------------------------------------
    # 8. LOAD EVENT DIMENSION
    # --------------------------------------------------
    print("Loading events...")

    rows = fetch_rows(source, """
        SELECT event_id, MIN(event), MIN(event_slug)
        FROM matches
        WHERE event_id IS NOT NULL
        GROUP BY event_id
    """)

    insert_rows(
        target, "dim_event",
        ["event_id", "event_name", "event_slug"],
        rows
    )

    # --------------------------------------------------
    # 9. LOAD DATE DIMENSION
    # --------------------------------------------------
    print("Loading dates...")

    dates = fetch_rows(source, """
        SELECT DISTINCT CAST(utc_timestamp AS DATE)
        FROM matches
        WHERE utc_timestamp IS NOT NULL
        ORDER BY 1
    """)

    date_rows = []

    for (date_value,) in dates:
        date_text = date_value.isoformat()

        date_rows.append((
            int(date_text.replace("-", "")),
            date_text,
            date_value.year,
            date_value.month,
            date_value.strftime("%B"),
            (date_value.month - 1) // 3 + 1
        ))

    insert_rows(
        target, "dim_date",
        ["date_key", "full_date", "year", "month",
         "month_name", "quarter"],
        date_rows
    )

    # --------------------------------------------------
    # 10. LOAD MATCH FACT
    # --------------------------------------------------
    print("Loading matches...")

    rows = fetch_rows(source, """
        SELECT
            match_id,
            CAST(utc_timestamp AS DATE),
            event_id,
            team0_id,
            team1_id,
            score0,
            score1,
            CASE
                WHEN score0 > score1 THEN team0_id
                WHEN score1 > score0 THEN team1_id
                ELSE NULL
            END,
            status,
            format,
            region,
            is_international
        FROM matches
        WHERE match_id IS NOT NULL
    """)

    match_rows = []

    for row in rows:
        values = list(row)
        match_date = values[1]

        values[1] = (
            int(match_date.isoformat().replace("-", ""))
            if match_date is not None else None
        )

        values[11] = (
            int(values[11]) if values[11] is not None else None
        )

        match_rows.append(tuple(values))

    insert_rows(
        target, "fact_match",
        ["match_id", "date_key", "event_id", "team0_id",
         "team1_id", "score0", "score1", "winner_team_id",
         "status", "match_format", "region", "is_international"],
        match_rows
    )

    # --------------------------------------------------
    # 11. LOAD MAP FACT
    # --------------------------------------------------
    print("Loading map results...")

    rows = fetch_rows(source, """
        SELECT
            match_id,
            game_id,
            map_name,
            picked_by_team,
            duration,
            score0,
            score1,
            performance_available,
            economy_available
        FROM maps
        WHERE match_id IS NOT NULL
          AND game_id IS NOT NULL
    """)

    map_rows = []

    for row in rows:
        (
            match_id, game_id, map_name, picked_by_team,
            duration, score0, score1,
            performance_available, economy_available
        ) = row

        map_rows.append((
            match_id,
            game_id,
            map_key_lookup.get(map_name),
            picked_by_team,
            duration,
            score0,
            score1,
            performance_available,
            economy_available
        ))

    insert_rows(
        target, "fact_map",
        ["match_id", "game_id", "map_key", "picked_by_team",
         "duration", "score0", "score1",
         "performance_available", "economy_available"],
        map_rows
    )

    # --------------------------------------------------
    # 12. LOAD PLAYER PERFORMANCE FACT
    # --------------------------------------------------
    print("Loading player performance...")

    rows = fetch_rows(source, """
        SELECT
            p.player_id,
            p.match_id,
            p.game_id,
            p.team_idx,
            CASE
                WHEN p.team_idx = 0 THEN m.team0_id
                WHEN p.team_idx = 1 THEN m.team1_id
                ELSE NULL
            END,
            p.agents,
            p.rating_all,
            p.acs_all,
            p.adr_all,
            p.kills_all,
            p.deaths_all,
            p.assists_all,
            p.fk_all,
            p.fd_all,
            p.kast_all,
            p.hs_pct_all,
            p.clutch_1v1,
            p.clutch_1v2,
            p.clutch_1v3,
            p.clutch_1v4,
            p.clutch_1v5
        FROM player_map p
        LEFT JOIN matches m
            ON p.match_id = m.match_id
        WHERE p.player_id IS NOT NULL
          AND p.match_id IS NOT NULL
          AND p.game_id IS NOT NULL
    """)

    player_rows = [
        tuple(row)
        for row in rows
    ]

    insert_rows(
        target, "fact_player_map",
        ["player_id", "match_id", "game_id", "team_idx",
         "team_id", "agents", "rating", "acs", "adr",
         "kills", "deaths", "assists", "first_kills",
         "first_deaths", "kast", "headshot_pct",
         "clutches_1v1", "clutches_1v2", "clutches_1v3",
         "clutches_1v4", "clutches_1v5"],
        player_rows
    )

    # --------------------------------------------------
    # 13. LOAD ROUND FACT
    # --------------------------------------------------
    print("Loading round data...")

    rows = fetch_rows(source, """
        SELECT
            match_id, game_id, round_num, winner_team,
            side, outcome, loadout_t0, loadout_t1,
            bank_t0, bank_t1
        FROM rounds
        WHERE match_id IS NOT NULL
          AND game_id IS NOT NULL
          AND round_num IS NOT NULL
    """)

    insert_rows(
        target, "fact_round",
        ["match_id", "game_id", "round_num", "winner_team",
         "side", "outcome", "loadout_t0", "loadout_t1",
         "bank_t0", "bank_t1"],
        rows
    )

    # --------------------------------------------------
    # 14. CREATE INDEXES
    # --------------------------------------------------
    print("Creating indexes...")

    target.executescript("""
        CREATE INDEX idx_match_date
            ON fact_match(date_key);

        CREATE INDEX idx_match_event
            ON fact_match(event_id);

        CREATE INDEX idx_match_region
            ON fact_match(region);

        CREATE INDEX idx_map_name
            ON fact_map(map_key);

        CREATE INDEX idx_player_id
            ON fact_player_map(player_id);

        CREATE INDEX idx_player_match
            ON fact_player_map(match_id);

        CREATE INDEX idx_player_team
            ON fact_player_map(team_id);

        CREATE INDEX idx_round_match
            ON fact_round(match_id);
    """)

    target.commit()

    # --------------------------------------------------
    # 15. DATA QUALITY REPORT
    # --------------------------------------------------
    print("Generating data-quality report...")

    report_tables = [
        "dim_team",
        "dim_player",
        "dim_map",
        "dim_event",
        "dim_date",
        "fact_match",
        "fact_map",
        "fact_player_map",
        "fact_round"
    ]

    quality_rows = []

    for table in report_tables:
        count = target.execute(
            f'SELECT COUNT(*) FROM "{table}"'
        ).fetchone()[0]

        quality_rows.append((table, count))

    with open(
        REPORT_DIR / "warehouse_table_counts.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["table_name", "row_count"])
        writer.writerows(quality_rows)

    # Check missing values in important columns
    missing_checks = [
        ("fact_match", "match_id"),
        ("fact_match", "date_key"),
        ("fact_match", "team0_id"),
        ("fact_match", "team1_id"),
        ("fact_map", "map_key"),
        ("fact_player_map", "player_id"),
        ("fact_player_map", "rating"),
        ("fact_round", "winner_team")
    ]

    missing_rows = []

    for table, column in missing_checks:
        count = target.execute(
            f'SELECT COUNT(*) FROM "{table}" '
            f'WHERE "{column}" IS NULL'
        ).fetchone()[0]

        missing_rows.append((table, column, count))

    with open(
        REPORT_DIR / "warehouse_missing_values.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["table_name", "column_name", "missing_count"])
        writer.writerows(missing_rows)

    # --------------------------------------------------
    # 16. SUMMARY
    # --------------------------------------------------
    print("\n" + "=" * 55)
    print("VALORANT ESPORTSIQ BI - WAREHOUSE SUMMARY")
    print("=" * 55)

    for table, count in quality_rows:
        print(f"{table:22} {count:>10,} rows")

    print("\nMissing-value checks:")
    for table, column, count in missing_rows:
        print(f"{table}.{column}: {count:,} missing")

    print(f"\nDatabase: {TARGET_DB}")
    print(f"Reports:  {REPORT_DIR}")
    print("\nWarehouse build completed successfully!")

except Exception:
    target.rollback()
    raise

finally:
    target.close()
    source.close()
