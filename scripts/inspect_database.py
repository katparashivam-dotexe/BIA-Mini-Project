
from pathlib import Path
import sys
import csv
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FOLDER = PROJECT_ROOT / "data"
REPORT_FOLDER = PROJECT_ROOT / "reports"

# Find the database file
if len(sys.argv) > 1:
    DB_PATH = Path(sys.argv[1]).expanduser().resolve()
else:
    candidates = [
        p for p in DATA_FOLDER.iterdir()
        if p.is_file() and p.suffix.lower() in {".duckdb", ".ddb", ".db"}
    ]

    if len(candidates) != 1:
        raise SystemExit(
            "Put exactly one database file in the data folder, "
            "or pass its full path as an argument."
        )

    DB_PATH = candidates[0]

if not DB_PATH.is_file():
    raise SystemExit(f"Database not found: {DB_PATH}")

print(f"\nDatabase: {DB_PATH}")

con = duckdb.connect(str(DB_PATH), read_only=True)

try:
    # 1. List tables and views
    tables = con.execute("""
        SELECT table_schema, table_name, table_type
        FROM information_schema.tables
        WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY table_schema, table_name
    """).fetchall()

    print("\n" + "=" * 65)
    print("1. TABLES AND VIEWS")
    print("=" * 65)

    for schema, name, table_type in tables:
        print(f"{schema}.{name} [{table_type}]")

    # 2. List columns and data types
    columns = con.execute("""
        SELECT table_schema, table_name, ordinal_position,
               column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY table_schema, table_name, ordinal_position
    """).fetchall()

    print("\n" + "=" * 65)
    print("2. COLUMN DETAILS")
    print("=" * 65)

    for schema, table, position, column, dtype, nullable in columns:
        print(
            f"{schema}.{table} | {position}. {column} "
            f"| {dtype} | Nullable: {nullable}"
        )

    # 3. Row counts and sample data
    print("\n" + "=" * 65)
    print("3. ROW COUNTS AND SAMPLE DATA")
    print("=" * 65)

    for schema, name, table_type in tables:
        # Safely quote SQL identifiers
        qualified_name = (
            '"' + schema.replace('"', '""') + '"."'
            + name.replace('"', '""') + '"'
        )

        try:
            count = con.execute(
                f"SELECT COUNT(*) FROM {qualified_name}"
            ).fetchone()[0]

            print(f"\n{schema}.{name}: {count:,} rows")

            cursor = con.execute(
                f"SELECT * FROM {qualified_name} LIMIT 5"
            )
            sample = cursor.fetchall()
            headers = [item[0] for item in cursor.description]

            print("Columns:", ", ".join(headers))

            for record in sample:
                print(record)

        except Exception as error:
            print(f"Could not inspect {name}: {error}")

    # 4. Save inventories without Pandas
    REPORT_FOLDER.mkdir(exist_ok=True)

    with open(
        REPORT_FOLDER / "table_inventory.csv",
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["schema", "table_name", "table_type"])
        writer.writerows(tables)

    with open(
        REPORT_FOLDER / "column_inventory.csv",
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow([
            "schema", "table_name", "position",
            "column_name", "data_type", "nullable"
        ])
        writer.writerows(columns)

    print("\nInspection completed successfully.")
    print("Reports saved in:", REPORT_FOLDER)

finally:
    con.close()
