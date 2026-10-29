
from pathlib import Path
import duckdb
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DB = ROOT / "data" / "vct_reference.duckdb"
WAREHOUSE_DB = ROOT / "warehouse" / "valorant_warehouse.db"

source = duckdb.connect(str(SOURCE_DB), read_only=True)
warehouse = sqlite3.connect(str(WAREHOUSE_DB))

try:
    print("\n1. MAP RECORDS WITH MISSING OR UNMATCHED NAMES")
    print("=" * 60)

    rows = source.execute("""
        SELECT
            match_id,
            game_id,
            map_name,
            score0,
            score1
        FROM maps
        WHERE map_name IS NULL
        ORDER BY match_id
        LIMIT 30
    """).fetchall()

    if rows:
        for row in rows:
            print(row)
    else:
        print("No NULL map names found in the source.")

    null_count = source.execute("""
        SELECT COUNT(*)
        FROM maps
        WHERE map_name IS NULL
    """).fetchone()[0]

    print(f"\nSource rows with NULL map names: {null_count}")

    print("\n2. PLAYER RECORDS WITH MISSING RATINGS")
    print("=" * 60)

    player_stats = warehouse.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN rating IS NULL THEN 1 ELSE 0 END),
            SUM(CASE WHEN acs IS NULL THEN 1 ELSE 0 END),
            SUM(CASE WHEN kills IS NULL THEN 1 ELSE 0 END),
            SUM(CASE WHEN deaths IS NULL THEN 1 ELSE 0 END)
        FROM fact_player_map
    """).fetchone()

    print("Total player-map records:", player_stats[0])
    print("Missing ratings:", player_stats[1])
    print("Missing ACS:", player_stats[2])
    print("Missing kills:", player_stats[3])
    print("Missing deaths:", player_stats[4])

    print("\n3. SAMPLE PLAYER RECORDS WITH MISSING RATINGS")
    print("=" * 60)

    samples = warehouse.execute("""
        SELECT
            player_id,
            match_id,
            game_id,
            rating,
            acs,
            kills,
            deaths
        FROM fact_player_map
        WHERE rating IS NULL
        LIMIT 10
    """).fetchall()

    for row in samples:
        print(row)

finally:
    warehouse.close()
    source.close()
