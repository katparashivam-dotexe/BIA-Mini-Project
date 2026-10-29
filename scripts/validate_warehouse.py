
from pathlib import Path
import sqlite3
import csv

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "warehouse" / "valorant_warehouse.db"
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)

if not DB_PATH.exists():
    raise FileNotFoundError(f"Warehouse not found: {DB_PATH}")

con = sqlite3.connect(DB_PATH)

checks = []

def add_check(name, sql, expected="PASS"):
    result = con.execute(sql).fetchone()[0]
    status = "PASS" if result == 0 else "CHECK"
    checks.append((name, result, status, expected))
    print(f"{status:6} | {name}: {result:,}")

try:
    print("\nVALORANT ESPORTSIQ BI - VALIDATION")
    print("=" * 65)

    # 1. Check duplicate business keys
    add_check(
        "Duplicate match IDs",
        """
        SELECT COUNT(*) FROM (
            SELECT match_id
            FROM fact_match
            GROUP BY match_id
            HAVING COUNT(*) > 1
        )
        """
    )

    add_check(
        "Duplicate map records",
        """
        SELECT COUNT(*) FROM (
            SELECT match_id, game_id
            FROM fact_map
            GROUP BY match_id, game_id
            HAVING COUNT(*) > 1
        )
        """
    )

    add_check(
        "Duplicate player-map records",
        """
        SELECT COUNT(*) FROM (
            SELECT player_id, match_id, game_id
            FROM fact_player_map
            GROUP BY player_id, match_id, game_id
            HAVING COUNT(*) > 1
        )
        """
    )

    add_check(
        "Duplicate round records",
        """
        SELECT COUNT(*) FROM (
            SELECT match_id, game_id, round_num
            FROM fact_round
            GROUP BY match_id, game_id, round_num
            HAVING COUNT(*) > 1
        )
        """
    )

    # 2. Check unmatched team references
    add_check(
        "Matches with unknown team 0",
        """
        SELECT COUNT(*)
        FROM fact_match f
        LEFT JOIN dim_team d ON f.team0_id = d.team_id
        WHERE f.team0_id IS NOT NULL AND d.team_id IS NULL
        """
    )

    add_check(
        "Matches with unknown team 1",
        """
        SELECT COUNT(*)
        FROM fact_match f
        LEFT JOIN dim_team d ON f.team1_id = d.team_id
        WHERE f.team1_id IS NOT NULL AND d.team_id IS NULL
        """
    )

    # 3. Check unmatched player references
    add_check(
        "Player records without a dimension match",
        """
        SELECT COUNT(*)
        FROM fact_player_map f
        LEFT JOIN dim_player d ON f.player_id = d.player_id
        WHERE d.player_id IS NULL
        """
    )

    # 4. Check unmatched map references
    add_check(
        "Map records without a dimension match",
        """
        SELECT COUNT(*)
        FROM fact_map f
        LEFT JOIN dim_map d ON f.map_key = d.map_key
        WHERE d.map_key IS NULL
        """
    )

    # 5. Check missing values
    add_check(
        "Matches with missing date keys",
        """
        SELECT COUNT(*) FROM fact_match
        WHERE date_key IS NULL
        """
    )

    add_check(
        "Player records with missing ratings",
        """
        SELECT COUNT(*) FROM fact_player_map
        WHERE rating IS NULL
        """
    )

    # 6. Check score validity
    add_check(
        "Map records with negative scores",
        """
        SELECT COUNT(*) FROM fact_map
        WHERE score0 < 0 OR score1 < 0
        """
    )

    # 7. Save validation report
    report_path = REPORT_DIR / "warehouse_validation.csv"

    with open(
        report_path, "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow([
            "check_name", "issue_count", "status", "expected"
        ])
        writer.writerows(checks)

    print("\nValidation report saved to:")
    print(report_path)

finally:
    con.close()
