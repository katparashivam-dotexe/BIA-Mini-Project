
from pathlib import Path
import sqlite3
import csv
import json

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "warehouse" / "valorant_warehouse.db"
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)

if not DB_PATH.exists():
    raise FileNotFoundError(f"Warehouse not found: {DB_PATH}")

con = sqlite3.connect(DB_PATH)

reports = {
    "team_win_rates": """
        WITH team_results AS (
            SELECT team0_id AS team_id,
                   CASE WHEN score0 > score1 THEN 1 ELSE 0 END AS won
            FROM fact_match
            WHERE status = 'final'
              AND team0_id IS NOT NULL
              AND team1_id IS NOT NULL
              AND score0 IS NOT NULL
              AND score1 IS NOT NULL
              AND score0 != score1

            UNION ALL

            SELECT team1_id AS team_id,
                   CASE WHEN score1 > score0 THEN 1 ELSE 0 END AS won
            FROM fact_match
            WHERE status = 'final'
              AND team0_id IS NOT NULL
              AND team1_id IS NOT NULL
              AND score0 IS NOT NULL
              AND score1 IS NOT NULL
              AND score0 != score1
        )
        SELECT
            t.team_name,
            COUNT(*) AS matches_played,
            SUM(r.won) AS wins,
            ROUND(100.0 * SUM(r.won) / COUNT(*), 2)
                AS win_rate_pct
        FROM team_results r
        JOIN dim_team t ON t.team_id = r.team_id
        GROUP BY t.team_id, t.team_name
        HAVING COUNT(*) >= 10
        ORDER BY win_rate_pct DESC, matches_played DESC
    """,

    "map_performance": """
        SELECT
            d.map_name,
            COUNT(*) AS maps_played,
            SUM(CASE WHEN f.score0 > f.score1 THEN 1 ELSE 0 END)
                AS team0_wins,
            SUM(CASE WHEN f.score1 > f.score0 THEN 1 ELSE 0 END)
                AS team1_wins,
            ROUND(AVG(f.score0), 2) AS avg_team0_score,
            ROUND(AVG(f.score1), 2) AS avg_team1_score
        FROM fact_map f
        JOIN dim_map d ON d.map_key = f.map_key
        WHERE f.score0 IS NOT NULL
          AND f.score1 IS NOT NULL
          AND f.score0 != f.score1
        GROUP BY d.map_name
        ORDER BY maps_played DESC
    """,

    "top_players": """
        SELECT
            p.player_name,
            COUNT(*) AS maps_with_performance,
            ROUND(AVG(f.rating), 3) AS avg_rating,
            ROUND(AVG(f.acs), 2) AS avg_acs,
            ROUND(AVG(f.kills), 2) AS avg_kills,
            ROUND(AVG(f.deaths), 2) AS avg_deaths,
            ROUND(AVG(f.headshot_pct), 2) AS avg_headshot_pct
        FROM fact_player_map f
        JOIN dim_player p ON p.player_id = f.player_id
        GROUP BY p.player_id, p.player_name
        HAVING COUNT(f.acs) >= 10
        ORDER BY avg_acs DESC
    """,

    "event_trends": """
        SELECT
            COALESCE(e.event_name, 'Unknown event') AS event_name,
            d.year,
            COUNT(*) AS matches_played
        FROM fact_match f
        LEFT JOIN dim_event e ON e.event_id = f.event_id
        LEFT JOIN dim_date d ON d.date_key = f.date_key
        WHERE f.status = 'final'
        GROUP BY e.event_name, d.year
        ORDER BY d.year, matches_played DESC
    """,

    "regional_matches": """
        SELECT
            COALESCE(region, 'Unknown') AS region,
            COUNT(*) AS matches_played,
            ROUND(AVG(ABS(score0 - score1)), 2)
                AS avg_series_score_gap
        FROM fact_match
        WHERE status = 'final'
          AND score0 IS NOT NULL
          AND score1 IS NOT NULL
        GROUP BY region
        ORDER BY matches_played DESC
    """
}


def export_report(name, query):
    cursor = con.execute(query)
    headers = [column[0] for column in cursor.description]
    rows = cursor.fetchall()

    output_path = REPORT_DIR / f"{name}.csv"

    with open(
        output_path, "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"\n{'=' * 65}")
    print(name.replace("_", " ").upper())
    print("=" * 65)
    print("Rows returned:", len(rows))

    for row in rows[:10]:
        print(row)

    print("Saved:", output_path)


try:
    # Run the SQL-based reports.
    for report_name, query in reports.items():
        export_report(report_name, query)

    # --------------------------------------------------
    # AGENT USAGE: EXPAND EACH AGENT INDIVIDUALLY
    # --------------------------------------------------
    print("\n" + "=" * 65)
    print("AGENT USAGE")
    print("=" * 65)

    agent_rows = con.execute("""
        SELECT agents, acs, kills, rating
        FROM fact_player_map
        WHERE agents IS NOT NULL
    """).fetchall()

    agent_stats = {}

    for agents_value, acs, kills, rating in agent_rows:
        try:
            agents = json.loads(agents_value)
        except (json.JSONDecodeError, TypeError):
            agents = [agents_value]

        if not isinstance(agents, list):
            agents = [agents]

        # Avoid counting repeated agent names within one record twice.
        unique_agents = {
            str(agent).strip()
            for agent in agents
            if agent is not None and str(agent).strip()
        }

        for agent in unique_agents:
            stats = agent_stats.setdefault(
                agent,
                {
                    "appearances": 0,
                    "acs_values": [],
                    "kill_values": [],
                    "rating_values": []
                }
            )

            stats["appearances"] += 1

            if acs is not None:
                stats["acs_values"].append(acs)

            if kills is not None:
                stats["kill_values"].append(kills)

            if rating is not None:
                stats["rating_values"].append(rating)

    agent_report = []

    for agent, stats in agent_stats.items():
        def safe_average(values):
            return (
                round(sum(values) / len(values), 2)
                if values else None
            )

        agent_report.append((
            agent,
            stats["appearances"],
            safe_average(stats["acs_values"]),
            safe_average(stats["kill_values"]),
            safe_average(stats["rating_values"])
        ))

    agent_report.sort(
        key=lambda row: row[1],
        reverse=True
    )

    agent_path = REPORT_DIR / "agent_usage.csv"

    with open(
        agent_path, "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.writer(file)
        writer.writerow([
            "agent",
            "player_map_appearances",
            "avg_acs",
            "avg_kills",
            "avg_rating"
        ])
        writer.writerows(agent_report)

    for row in agent_report[:10]:
        print(row)

    print("Saved:", agent_path)
    print("\nAll OLAP reports generated successfully.")

finally:
    con.close()
