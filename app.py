import sqlite3
from pathlib import Path
from html import escape

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# VALORANT ESPORTSIQ BI DASHBOARD
# ============================================================

st.set_page_config(
    page_title="Valorant EsportsIQ | BI Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# THEME
# ============================================================

st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">

    <style>
        :root {
            --red: #FF4655;
            --bg: #0B0B0E;
            --panel: #141419;
            --panel2: #19191F;
            --border: #292930;
            --muted: #92929F;
            --white: #F5F5F7;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background: var(--bg);
            color: var(--white);
        }

        [data-testid="stHeader"] {
            background: rgba(11, 11, 14, 0.95);
        }

        [data-testid="stSidebar"] {
            background: #101014;
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] * {
            color: var(--white);
        }

        h1, h2, h3 {
            font-family: 'Barlow Condensed', sans-serif !important;
            text-transform: uppercase;
            letter-spacing: 0.7px;
        }

        h1 {
            font-size: 3.1rem !important;
            font-weight: 800 !important;
        }

        h2 {
            font-size: 1.9rem !important;
            font-weight: 700 !important;
        }

        h3 {
            font-size: 1.35rem !important;
            font-weight: 600 !important;
        }

        p, label, span, div {
            font-family: 'Inter', sans-serif;
        }

        [data-testid="stMetric"] {
            background: linear-gradient(145deg, #19191F, #111115);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px 18px;
            min-height: 120px;
        }

        [data-testid="stMetricLabel"] {
            color: #A4A4B0 !important;
            font-size: 0.78rem !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        [data-testid="stMetricValue"] {
            color: #FFFFFF !important;
            font-family: 'Barlow Condensed', sans-serif !important;
            font-size: 2.3rem !important;
            font-weight: 700 !important;
        }

        [data-testid="stMetricDelta"] {
            font-size: 0.8rem !important;
        }

        .hero {
            padding: 30px 32px;
            border-radius: 15px;
            background:
                radial-gradient(circle at 85% 15%, rgba(255,70,85,0.17), transparent 32%),
                linear-gradient(120deg, #18181F, #101014);
            border: 1px solid #303039;
            margin-bottom: 25px;
            position: relative;
            overflow: hidden;
        }

        .hero-kicker {
            color: var(--red);
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 3px;
            margin-bottom: 8px;
        }

        .hero-title {
            font-family: 'Barlow Condensed', sans-serif;
            font-size: 3.5rem;
            font-weight: 900;
            line-height: 1;
            color: #FFFFFF;
            margin: 0;
        }

        .hero-title span {
            color: var(--red);
        }

        .hero-subtitle {
            color: #A5A5B1;
            margin-top: 14px;
            font-size: 0.9rem;
            max-width: 680px;
            line-height: 1.7;
        }

        .section-heading {
            font-family: 'Barlow Condensed', sans-serif;
            font-size: 1.8rem;
            font-weight: 700;
            text-transform: uppercase;
            margin-top: 12px;
            margin-bottom: 3px;
            color: #F5F5F7;
        }

        .section-subtitle {
            color: #92929F;
            font-size: 0.8rem;
            margin-bottom: 15px;
        }

        .panel {
            background: #141419;
            border: 1px solid #292930;
            border-radius: 12px;
            padding: 18px 20px;
            margin-bottom: 15px;
        }

        .panel-title {
            color: #FFFFFF;
            font-family: 'Barlow Condensed', sans-serif;
            text-transform: uppercase;
            font-size: 1.35rem;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .panel-subtitle {
            color: #92929F;
            font-size: 0.76rem;
            margin-bottom: 15px;
        }

        .accent-line {
            height: 3px;
            width: 45px;
            background: var(--red);
            margin: 10px 0 16px 0;
            border-radius: 2px;
        }

        .sidebar-brand {
            font-family: 'Barlow Condensed', sans-serif;
            font-size: 1.65rem;
            font-weight: 900;
            letter-spacing: 1px;
            color: white;
        }

        .sidebar-brand span {
            color: var(--red);
        }

        .sidebar-caption {
            color: #92929F;
            font-size: 0.68rem;
            letter-spacing: 2px;
            margin-top: -4px;
            margin-bottom: 24px;
        }

        .tag {
            display: inline-block;
            color: #FF6673;
            border: 1px solid rgba(255,70,85,0.35);
            background: rgba(255,70,85,0.08);
            border-radius: 5px;
            padding: 5px 9px;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 1px;
            margin-right: 5px;
        }

        .footer {
            border-top: 1px solid #292930;
            margin-top: 35px;
            padding-top: 18px;
            color: #777783;
            font-size: 0.72rem;
            text-align: center;
        }

        .empty-state {
            background: #141419;
            border: 1px dashed #383840;
            padding: 22px;
            border-radius: 10px;
            color: #A4A4B0;
            font-size: 0.85rem;
        }

        div[data-testid="stSelectbox"] label,
        div[data-testid="stMultiSelect"] label,
        div[data-testid="stSlider"] label {
            color: #C7C7D0;
            font-size: 0.82rem;
        }

        div[data-testid="stSelectbox"] > div > div {
            background-color: #19191F;
        }

        .stButton > button {
            background: var(--red);
            color: white;
            border: none;
            border-radius: 7px;
            font-weight: 700;
        }

        .stButton > button:hover {
            background: #E83949;
            color: white;
        }

        hr {
            border-color: #292930;
        }

        #MainMenu, footer {
            visibility: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "warehouse" / "valorant_warehouse.db"


def get_connection():
    if not DB_PATH.exists():
        st.error(
            f"Warehouse database not found at:\n{DB_PATH}\n\n"
            "Run scripts/build_warehouse.py first."
        )
        st.stop()

    connection = sqlite3.connect(str(DB_PATH))
    connection.row_factory = sqlite3.Row
    return connection


@st.cache_data(show_spinner=False)
def get_table_names():
    connection = get_connection()
    try:
        rows = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """
        ).fetchall()
        return [row["name"] for row in rows]
    finally:
        connection.close()


@st.cache_data(show_spinner=False)
def get_columns(table_name):
    if table_name not in get_table_names():
        return []

    connection = get_connection()
    try:
        rows = connection.execute(
            f'PRAGMA table_info("{table_name}")'
        ).fetchall()
        return [row["name"] for row in rows]
    finally:
        connection.close()


def find_column(table_name, candidates, required=True):
    columns = get_columns(table_name)
    lower_lookup = {column.lower(): column for column in columns}

    for candidate in candidates:
        if candidate.lower() in lower_lookup:
            return lower_lookup[candidate.lower()]

    if required:
        return None

    return None


def table_exists(table_name):
    return table_name in get_table_names()


def run_query(query, params=()):
    connection = get_connection()
    try:
        return pd.read_sql_query(query, connection, params=params)
    finally:
        connection.close()


def get_distinct_values(query, params=()):
    try:
        frame = run_query(query, params)
        if frame.empty:
            return []
        return frame.iloc[:, 0].dropna().tolist()
    except Exception:
        return []


def safe_identifier(identifier):
    if identifier is None:
        return None
    return '"' + str(identifier).replace('"', '""') + '"'


def show_table(data, limit=100):
    """
    Render a basic HTML table to avoid depending on PyArrow.
    """
    if data is None or data.empty:
        st.markdown(
            '<div class="empty-state">No data available for this selection.</div>',
            unsafe_allow_html=True,
        )
        return

    display_data = data.head(limit).copy()

    headers = "".join(
        f"""
        <th style="
            text-align:left;
            padding:11px 12px;
            background:#202027;
            color:#FF6673;
            border-bottom:1px solid #383840;
            font-size:11px;
            text-transform:uppercase;
            letter-spacing:0.7px;
            white-space:nowrap;
        ">{escape(str(column))}</th>
        """
        for column in display_data.columns
    )

    rows_html = []

    for index, row in display_data.iterrows():
        cells = []

        for value in row:
            if pd.isna(value):
                formatted = "—"
            elif isinstance(value, float):
                formatted = f"{value:,.2f}"
            else:
                formatted = str(value)

            cells.append(
                f"""
                <td style="
                    padding:10px 12px;
                    border-bottom:1px solid #292930;
                    color:#D8D8E0;
                    font-size:12px;
                    white-space:nowrap;
                ">{escape(formatted)}</td>
                """
            )

        row_background = "#15151A" if index % 2 == 0 else "#19191F"

        rows_html.append(
            f'<tr style="background:{row_background};">'
            + "".join(cells)
            + "</tr>"
        )

    html = f"""
    <div style="
        width:100%;
        overflow-x:auto;
        border:1px solid #292930;
        border-radius:8px;
        margin-bottom:8px;
    ">
        <table style="
            width:100%;
            border-collapse:collapse;
            font-family:Inter,sans-serif;
        ">
            <thead><tr>{headers}</tr></thead>
            <tbody>{''.join(rows_html)}</tbody>
        </table>
    </div>
    """

    # Render the HTML in an isolated iframe so Streamlit's Markdown parser
    # cannot display the table markup as literal text. This fixes every section
    # that uses show_table(), including Team Performance, Top Players,
    # Agent Intelligence, and Match Explorer.
    table_height = min(720, max(160, 58 + len(display_data) * 43))
    st.components.v1.html(
        html,
        height=table_height,
        scrolling=True,
    )

    if len(data) > limit:
        st.caption(f"Showing {limit:,} of {len(data):,} rows.")


def section_heading(title, subtitle=""):
    st.markdown(
        f"""
        <div class="section-heading">{escape(title)}</div>
        <div class="accent-line"></div>
        <div class="section-subtitle">{escape(subtitle)}</div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(message):
    st.markdown(
        f'<div class="empty-state">{escape(message)}</div>',
        unsafe_allow_html=True,
    )


def format_number(value, decimals=0):
    if value is None or pd.isna(value):
        return "—"

    try:
        if decimals:
            return f"{float(value):,.{decimals}f}"
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return str(value)


def plotly_dark(fig, height=340):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#D8D8E0", size=11),
        margin=dict(l=12, r=12, t=30, b=12),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#D8D8E0", size=10),
        ),
        xaxis=dict(
            gridcolor="#292930",
            zerolinecolor="#292930",
            linecolor="#292930",
        ),
        yaxis=dict(
            gridcolor="#292930",
            zerolinecolor="#292930",
            linecolor="#292930",
        ),
    )
    return fig


# ============================================================
# SCHEMA DETECTION
# ============================================================

REQUIRED_TABLES = [
    "fact_match",
    "dim_team",
    "dim_event",
    "dim_date",
    "fact_map",
    "dim_map",
    "fact_player_map",
    "dim_player",
]

missing_tables = [
    table for table in REQUIRED_TABLES
    if not table_exists(table)
]

if missing_tables:
    st.error(
        "Some required warehouse tables are missing: "
        + ", ".join(missing_tables)
    )
    st.stop()


# Match dimensions
MATCH_ID = find_column("fact_match", ["match_id"])
MATCH_EVENT_ID = find_column("fact_match", ["event_id"], required=False)
MATCH_DATE_KEY = find_column("fact_match", ["date_key"], required=False)
MATCH_REGION = find_column("fact_match", ["region"], required=False)
MATCH_SCORE0 = find_column("fact_match", ["score0"], required=False)
MATCH_SCORE1 = find_column("fact_match", ["score1"], required=False)
MATCH_STATUS = find_column("fact_match", ["status"], required=False)

DATE_KEY = find_column("dim_date", ["date_key"], required=False)
DATE_YEAR = find_column("dim_date", ["year"], required=False)

EVENT_ID = find_column("dim_event", ["event_id"], required=False)
EVENT_NAME = find_column(
    "dim_event",
    ["event_name", "name", "tournament_name"],
    required=False,
)

TEAM_ID = find_column("dim_team", ["team_id"], required=False)
TEAM_NAME = find_column(
    "dim_team",
    ["team_name", "name"],
    required=False,
)

# Map dimensions
MAP_MATCH_ID = find_column("fact_map", ["match_id"])
MAP_KEY = find_column("fact_map", ["map_key"])
MAP_NAME = find_column("dim_map", ["map_name"])
MAP_SCORE0 = find_column("fact_map", ["score0"])
MAP_SCORE1 = find_column("fact_map", ["score1"])

# Player dimensions
PM_MATCH_ID = find_column("fact_player_map", ["match_id"])
PM_PLAYER_ID = find_column("fact_player_map", ["player_id"])
PM_TEAM_ID = find_column("fact_player_map", ["team_id"], required=False)
PM_TEAM_IDX = find_column("fact_player_map", ["team_idx"], required=False)
PM_RATING = find_column("fact_player_map", ["rating"], required=False)
PM_ACS = find_column("fact_player_map", ["acs"], required=False)
PM_ADR = find_column("fact_player_map", ["adr"], required=False)
PM_KILLS = find_column("fact_player_map", ["kills"], required=False)
PM_DEATHS = find_column("fact_player_map", ["deaths"], required=False)
PM_ASSISTS = find_column("fact_player_map", ["assists"], required=False)
PM_FIRST_KILLS = find_column("fact_player_map", ["first_kills"], required=False)
PM_HS = find_column("fact_player_map", ["headshot_pct"], required=False)
PM_AGENTS = find_column("fact_player_map", ["agents"], required=False)

PLAYER_ID = find_column("dim_player", ["player_id"])
PLAYER_NAME = find_column("dim_player", ["player_name"])


# ============================================================
# FILTER QUERY BUILDER
# ============================================================

def build_match_joins():
    joins = []

    if (
        MATCH_DATE_KEY
        and DATE_KEY
        and DATE_YEAR
    ):
        joins.append(
            f'LEFT JOIN dim_date d '
            f'ON d.{safe_identifier(DATE_KEY)} = '
            f'f.{safe_identifier(MATCH_DATE_KEY)}'
        )

    if (
        MATCH_EVENT_ID
        and EVENT_ID
        and EVENT_NAME
    ):
        joins.append(
            f'LEFT JOIN dim_event e '
            f'ON e.{safe_identifier(EVENT_ID)} = '
            f'f.{safe_identifier(MATCH_EVENT_ID)}'
        )

    return " ".join(joins)


MATCH_JOIN = build_match_joins()


def build_filters(selected_year, selected_region, selected_event):
    conditions = []
    params = []

    if selected_year != "All":
        if DATE_YEAR and MATCH_DATE_KEY and DATE_KEY:
            conditions.append(
                f'd.{safe_identifier(DATE_YEAR)} = ?'
            )
            params.append(int(selected_year))
        else:
            year_column = find_column(
                "fact_match", ["year"], required=False
            )
            if year_column:
                conditions.append(
                    f'f.{safe_identifier(year_column)} = ?'
                )
                params.append(int(selected_year))

    if selected_region != "All" and MATCH_REGION:
        conditions.append(
            f'f.{safe_identifier(MATCH_REGION)} = ?'
        )
        params.append(selected_region)

    if selected_event != "All" and EVENT_NAME:
        conditions.append(
            f'e.{safe_identifier(EVENT_NAME)} = ?'
        )
        params.append(selected_event)

    where_sql = " AND ".join(conditions) if conditions else "1=1"

    return where_sql, params


def filtered_match_cte(where_sql):
    return f"""
        SELECT f.*
        FROM fact_match f
        {MATCH_JOIN}
        WHERE {where_sql}
    """


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">ESPORTS<span>IQ</span></div>
        <div class="sidebar-caption">VALORANT ANALYTICS PLATFORM</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### DATA FILTERS")

    year_query = None

    if DATE_YEAR and MATCH_DATE_KEY and DATE_KEY:
        year_query = f"""
            SELECT DISTINCT d.{safe_identifier(DATE_YEAR)} AS year
            FROM fact_match f
            LEFT JOIN dim_date d
              ON d.{safe_identifier(DATE_KEY)} =
                 f.{safe_identifier(MATCH_DATE_KEY)}
            WHERE d.{safe_identifier(DATE_YEAR)} IS NOT NULL
            ORDER BY year
        """
    else:
        fact_year = find_column(
            "fact_match", ["year"], required=False
        )
        if fact_year:
            year_query = f"""
                SELECT DISTINCT {safe_identifier(fact_year)} AS year
                FROM fact_match
                WHERE {safe_identifier(fact_year)} IS NOT NULL
                ORDER BY year
            """

    years = get_distinct_values(year_query) if year_query else []
    years = [str(int(year)) for year in years if str(year).replace(".", "", 1).isdigit()]
    year_options = ["All"] + years

    selected_year = st.selectbox(
        "YEAR",
        year_options,
        index=0,
    )

    if MATCH_REGION:
        region_options = get_distinct_values(
            f"""
            SELECT DISTINCT {safe_identifier(MATCH_REGION)}
            FROM fact_match
            WHERE {safe_identifier(MATCH_REGION)} IS NOT NULL
              AND TRIM({safe_identifier(MATCH_REGION)}) != ''
            ORDER BY 1
            """
        )
    else:
        region_options = []

    selected_region = st.selectbox(
        "REGION",
        ["All"] + [str(value) for value in region_options],
        index=0,
    )

    if EVENT_NAME and EVENT_ID and MATCH_EVENT_ID:
        event_options = get_distinct_values(
            f"""
            SELECT DISTINCT e.{safe_identifier(EVENT_NAME)}
            FROM fact_match f
            LEFT JOIN dim_event e
              ON e.{safe_identifier(EVENT_ID)} =
                 f.{safe_identifier(MATCH_EVENT_ID)}
            WHERE e.{safe_identifier(EVENT_NAME)} IS NOT NULL
              AND TRIM(e.{safe_identifier(EVENT_NAME)}) != ''
            ORDER BY 1
            """
        )
    else:
        event_options = []

    selected_event = st.selectbox(
        "TOURNAMENT",
        ["All"] + [str(value) for value in event_options],
        index=0,
    )

    st.markdown("---")

    st.markdown(
        """
        <div style="color:#92929F;font-size:0.75rem;line-height:1.7;">
            Explore competitive VALORANT data through match,
            map, team and player performance.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div style="
            margin-top:25px;
            padding:12px;
            border:1px solid #292930;
            border-radius:8px;
            background:#141419;
        ">
            <div style="font-size:10px;color:#92929F;letter-spacing:1px;">
                WAREHOUSE STATUS
            </div>
            <div style="color:#69D9A4;font-weight:700;margin-top:5px;">
                ● CONNECTED
            </div>
            <div style="font-size:10px;color:#777783;margin-top:4px;">
                SQLite analytics warehouse
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


FILTER_SQL, FILTER_PARAMS = build_filters(
    selected_year,
    selected_region,
    selected_event,
)

FILTERED_MATCHES = filtered_match_cte(FILTER_SQL)


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">COMPETITIVE INTELLIGENCE / BI PLATFORM</div>
        <div class="hero-title">VALORANT <span>ESPORTSIQ</span></div>
        <div class="hero-subtitle">
            A data-driven view of the competitive VALORANT ecosystem.
            Track match activity, map trends, team performance and
            individual player impact from one analytics workspace.
        </div>
        <div style="margin-top:20px;">
            <span class="tag">MATCH ANALYTICS</span>
            <span class="tag">MAP CONTROL</span>
            <span class="tag">PLAYER INTELLIGENCE</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FILTERED MATCH DATA
# ============================================================

match_select_columns = [
    f'f.{safe_identifier(MATCH_ID)} AS match_id'
]

if MATCH_SCORE0:
    match_select_columns.append(
        f'f.{safe_identifier(MATCH_SCORE0)} AS score0'
    )

if MATCH_SCORE1:
    match_select_columns.append(
        f'f.{safe_identifier(MATCH_SCORE1)} AS score1'
    )

if MATCH_STATUS:
    match_select_columns.append(
        f'f.{safe_identifier(MATCH_STATUS)} AS status'
    )

if MATCH_REGION:
    match_select_columns.append(
        f'f.{safe_identifier(MATCH_REGION)} AS region'
    )

if MATCH_EVENT_ID:
    match_select_columns.append(
        f'f.{safe_identifier(MATCH_EVENT_ID)} AS event_id'
    )

if MATCH_DATE_KEY:
    match_select_columns.append(
        f'f.{safe_identifier(MATCH_DATE_KEY)} AS date_key'
    )

matches_query = f"""
    SELECT {", ".join(match_select_columns)}
    FROM fact_match f
    {MATCH_JOIN}
    WHERE {FILTER_SQL}
"""

try:
    match_data = run_query(matches_query, FILTER_PARAMS)
except Exception as error:
    st.error(f"Could not load match data: {error}")
    match_data = pd.DataFrame()


# ============================================================
# KPI CARDS
# ============================================================

section_heading(
    "Command Center",
    "A snapshot of competitive activity under the current filters.",
)

total_matches = len(match_data)

unique_match_ids = (
    match_data["match_id"].nunique()
    if "match_id" in match_data.columns
    else total_matches
)

if "score0" in match_data.columns and "score1" in match_data.columns:
    score_data = match_data.dropna(subset=["score0", "score1"]).copy()
    total_rounds = score_data["score0"] + score_data["score1"]
    average_rounds = total_rounds.mean() if not total_rounds.empty else None
else:
    average_rounds = None

if MATCH_EVENT_ID and not match_data.empty and "event_id" in match_data.columns:
    total_events = match_data["event_id"].nunique()
else:
    total_events = 0

if MATCH_REGION and not match_data.empty and "region" in match_data.columns:
    total_regions = match_data["region"].nunique()
else:
    total_regions = 0

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("MATCHES ANALYZED", format_number(unique_match_ids))

with k2:
    st.metric("EVENTS REPRESENTED", format_number(total_events))

with k3:
    st.metric("REGIONS COVERED", format_number(total_regions))

with k4:
    st.metric(
        "AVG. TOTAL ROUNDS",
        format_number(average_rounds, 1)
        if average_rounds is not None
        else "N/A",
    )


# ============================================================
# MATCH ACTIVITY AND REGIONAL OVERVIEW
# ============================================================

st.markdown("")

left, right = st.columns([1.55, 1])

with left:
    section_heading(
        "Match Activity",
        "Number of matches recorded across years.",
    )

    if DATE_YEAR and MATCH_DATE_KEY and DATE_KEY:
        activity_query = f"""
            SELECT
                d.{safe_identifier(DATE_YEAR)} AS year,
                COUNT(DISTINCT f.{safe_identifier(MATCH_ID)}) AS matches
            FROM fact_match f
            LEFT JOIN dim_date d
              ON d.{safe_identifier(DATE_KEY)} =
                 f.{safe_identifier(MATCH_DATE_KEY)}
            {MATCH_JOIN.replace(
                f'LEFT JOIN dim_date d ON d.{safe_identifier(DATE_KEY)} = f.{safe_identifier(MATCH_DATE_KEY)}',
                ''
            )}
            WHERE {FILTER_SQL}
              AND d.{safe_identifier(DATE_YEAR)} IS NOT NULL
            GROUP BY d.{safe_identifier(DATE_YEAR)}
            ORDER BY year
        """

        try:
            activity_data = run_query(activity_query, FILTER_PARAMS)
        except Exception:
            activity_data = pd.DataFrame()
    else:
        activity_data = pd.DataFrame()

    if not activity_data.empty:
        activity_data["year"] = activity_data["year"].astype(str)

        fig = px.area(
            activity_data,
            x="year",
            y="matches",
            markers=True,
        )

        fig.update_traces(
            line=dict(color="#FF4655", width=3),
            fillcolor="rgba(255,70,85,0.14)",
            marker=dict(size=7, color="#FF4655"),
            hovertemplate="<b>%{x}</b><br>Matches: %{y:,}<extra></extra>",
        )

        fig.update_xaxes(title=None)
        fig.update_yaxes(title="Matches")
        st.plotly_chart(
            plotly_dark(fig, 350),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    else:
        empty_state("Year-wise match activity is unavailable for these filters.")

with right:
    section_heading(
        "Regional Landscape",
        "Distribution of matches by region.",
    )

    if MATCH_REGION:
        region_query = f"""
            SELECT
                f.{safe_identifier(MATCH_REGION)} AS region,
                COUNT(DISTINCT f.{safe_identifier(MATCH_ID)}) AS matches
            FROM fact_match f
            {MATCH_JOIN}
            WHERE {FILTER_SQL}
              AND f.{safe_identifier(MATCH_REGION)} IS NOT NULL
              AND TRIM(f.{safe_identifier(MATCH_REGION)}) != ''
            GROUP BY f.{safe_identifier(MATCH_REGION)}
            ORDER BY matches DESC
        """

        try:
            region_data = run_query(region_query, FILTER_PARAMS)
        except Exception:
            region_data = pd.DataFrame()
    else:
        region_data = pd.DataFrame()

    if not region_data.empty:
        fig = px.pie(
            region_data,
            names="region",
            values="matches",
            hole=0.68,
            color_discrete_sequence=[
                "#FF4655",
                "#D32F40",
                "#8B2635",
                "#5D2530",
                "#777783",
                "#45454F",
            ],
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent",
            hovertemplate="%{label}<br>Matches: %{value:,}<extra></extra>",
        )

        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", y=-0.12),
        )

        st.plotly_chart(
            plotly_dark(fig, 350),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    else:
        empty_state("Regional match information is unavailable.")


# ============================================================
# TEAM PERFORMANCE
# ============================================================

st.markdown("")
section_heading(
    "Team Performance",
    "Compare teams using the match scores available in the warehouse.",
)

if (
    MATCH_SCORE0
    and MATCH_SCORE1
    and TEAM_ID
    and TEAM_NAME
    and table_exists("dim_team")
):
    team0_col = find_column("fact_match", ["team0_id"], required=False)
    team1_col = find_column("fact_match", ["team1_id"], required=False)

    if team0_col and team1_col:
        team_query = f"""
            WITH filtered_matches AS (
                {FILTERED_MATCHES}
            ),
            team_results AS (
                SELECT
                    t0.{safe_identifier(TEAM_NAME)} AS team_name,
                    fm.{safe_identifier(MATCH_SCORE0)} AS team_score,
                    fm.{safe_identifier(MATCH_SCORE1)} AS opponent_score
                FROM filtered_matches fm
                JOIN dim_team t0
                  ON t0.{safe_identifier(TEAM_ID)} =
                     fm.{safe_identifier(team0_col)}
                WHERE fm.{safe_identifier(MATCH_SCORE0)} IS NOT NULL
                  AND fm.{safe_identifier(MATCH_SCORE1)} IS NOT NULL

                UNION ALL

                SELECT
                    t1.{safe_identifier(TEAM_NAME)} AS team_name,
                    fm.{safe_identifier(MATCH_SCORE1)} AS team_score,
                    fm.{safe_identifier(MATCH_SCORE0)} AS opponent_score
                FROM filtered_matches fm
                JOIN dim_team t1
                  ON t1.{safe_identifier(TEAM_ID)} =
                     fm.{safe_identifier(team1_col)}
                WHERE fm.{safe_identifier(MATCH_SCORE0)} IS NOT NULL
                  AND fm.{safe_identifier(MATCH_SCORE1)} IS NOT NULL
            )
            SELECT
                team_name,
                COUNT(*) AS maps_recorded,
                SUM(CASE WHEN team_score > opponent_score THEN 1 ELSE 0 END)
                    AS wins,
                SUM(CASE WHEN team_score < opponent_score THEN 1 ELSE 0 END)
                    AS losses,
                ROUND(
                    100.0 * SUM(
                        CASE WHEN team_score > opponent_score THEN 1 ELSE 0 END
                    ) / NULLIF(
                        SUM(
                            CASE WHEN team_score != opponent_score THEN 1 ELSE 0 END
                        ),
                        0
                    ),
                    2
                ) AS win_rate
            FROM team_results
            GROUP BY team_name
            HAVING COUNT(*) >= 3
            ORDER BY win_rate DESC, wins DESC
            LIMIT 15
        """

        try:
            team_data = run_query(team_query, FILTER_PARAMS)
        except Exception:
            team_data = pd.DataFrame()
    else:
        team_data = pd.DataFrame()
else:
    team_data = pd.DataFrame()

if not team_data.empty:
    team_left, team_right = st.columns([1.2, 1])

    with team_left:
        chart_data = team_data.sort_values("win_rate", ascending=True)

        fig = px.bar(
            chart_data,
            x="win_rate",
            y="team_name",
            orientation="h",
            color="win_rate",
            color_continuous_scale=["#6E202B", "#FF4655", "#FF8A93"],
            hover_data=["wins", "losses", "maps_recorded"],
        )

        fig.update_traces(
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Win rate: %{x:.2f}%<extra></extra>"
            )
        )

        fig.update_layout(
            coloraxis_showscale=False,
            xaxis_title="Win rate (%)",
            yaxis_title=None,
        )

        st.plotly_chart(
            plotly_dark(fig, 450),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with team_right:
        show_table(
            team_data.rename(
                columns={
                    "team_name": "Team",
                    "maps_recorded": "Maps",
                    "wins": "Wins",
                    "losses": "Losses",
                    "win_rate": "Win Rate %",
                }
            ),
            limit=15,
        )
else:
    empty_state(
        "Team performance cannot be calculated from the current selection "
        "or the required team and score columns are unavailable."
    )



# ============================================================
# TEAM COMPARISON
# ============================================================

st.markdown("")
section_heading(
    "Team Comparison",
    "Compare two teams using map-level scores from the filtered matches.",
)

team0_col_compare = find_column("fact_match", ["team0_id"], required=False)
team1_col_compare = find_column("fact_match", ["team1_id"], required=False)

if (
    team0_col_compare
    and team1_col_compare
    and TEAM_ID
    and TEAM_NAME
    and MAP_MATCH_ID
    and MAP_SCORE0
    and MAP_SCORE1
):
    team_comparison_query = f"""
        WITH filtered_matches AS (
            {FILTERED_MATCHES}
        ),
        map_results AS (
            SELECT
                t0.{safe_identifier(TEAM_ID)} AS team_id,
                t0.{safe_identifier(TEAM_NAME)} AS team_name,
                CAST(mp.{safe_identifier(MAP_SCORE0)} AS REAL) AS team_score,
                CAST(mp.{safe_identifier(MAP_SCORE1)} AS REAL) AS opponent_score
            FROM filtered_matches fm
            JOIN fact_map mp
              ON mp.{safe_identifier(MAP_MATCH_ID)} =
                 fm.{safe_identifier(MATCH_ID)}
            JOIN dim_team t0
              ON t0.{safe_identifier(TEAM_ID)} =
                 fm.{safe_identifier(team0_col_compare)}
            WHERE mp.{safe_identifier(MAP_SCORE0)} IS NOT NULL
              AND mp.{safe_identifier(MAP_SCORE1)} IS NOT NULL
              AND CAST(mp.{safe_identifier(MAP_SCORE0)} AS REAL)
                  != CAST(mp.{safe_identifier(MAP_SCORE1)} AS REAL)

            UNION ALL

            SELECT
                t1.{safe_identifier(TEAM_ID)} AS team_id,
                t1.{safe_identifier(TEAM_NAME)} AS team_name,
                CAST(mp.{safe_identifier(MAP_SCORE1)} AS REAL) AS team_score,
                CAST(mp.{safe_identifier(MAP_SCORE0)} AS REAL) AS opponent_score
            FROM filtered_matches fm
            JOIN fact_map mp
              ON mp.{safe_identifier(MAP_MATCH_ID)} =
                 fm.{safe_identifier(MATCH_ID)}
            JOIN dim_team t1
              ON t1.{safe_identifier(TEAM_ID)} =
                 fm.{safe_identifier(team1_col_compare)}
            WHERE mp.{safe_identifier(MAP_SCORE0)} IS NOT NULL
              AND mp.{safe_identifier(MAP_SCORE1)} IS NOT NULL
              AND CAST(mp.{safe_identifier(MAP_SCORE0)} AS REAL)
                  != CAST(mp.{safe_identifier(MAP_SCORE1)} AS REAL)
        )
        SELECT
            team_id,
            team_name,
            COUNT(*) AS maps_played,
            SUM(CASE WHEN team_score > opponent_score THEN 1 ELSE 0 END) AS wins,
            SUM(CASE WHEN team_score < opponent_score THEN 1 ELSE 0 END) AS losses,
            ROUND(
                100.0 * SUM(CASE WHEN team_score > opponent_score THEN 1 ELSE 0 END)
                / NULLIF(COUNT(*), 0),
                2
            ) AS win_rate,
            ROUND(AVG(team_score + opponent_score), 2) AS avg_total_rounds,
            ROUND(AVG(team_score), 2) AS avg_rounds_won,
            ROUND(AVG(opponent_score), 2) AS avg_rounds_lost_to_opponent
        FROM map_results
        GROUP BY team_id, team_name
        HAVING COUNT(*) >= 1
        ORDER BY win_rate DESC, wins DESC, team_name
    """

    try:
        comparison_data = run_query(team_comparison_query, FILTER_PARAMS)
    except Exception as error:
        comparison_data = pd.DataFrame()
        st.warning(f"Team comparison data could not be loaded: {error}")

    if not comparison_data.empty:
        comparison_data = comparison_data.dropna(subset=["team_name"])
        comparison_data["team_name"] = comparison_data["team_name"].astype(str)
        team_options = comparison_data["team_name"].drop_duplicates().tolist()

        if len(team_options) >= 2:
            default_a = team_options[0]
            default_b = team_options[1]
            compare_left, compare_right = st.columns(2)

            with compare_left:
                team_a_name = st.selectbox(
                    "SELECT TEAM A",
                    options=team_options,
                    index=team_options.index(default_a),
                    key="team_comparison_a",
                )

            available_b = [name for name in team_options if name != team_a_name]
            if not available_b:
                available_b = team_options

            default_b = default_b if default_b in available_b else available_b[0]

            with compare_right:
                team_b_name = st.selectbox(
                    "SELECT TEAM B",
                    options=available_b,
                    index=available_b.index(default_b),
                    key="team_comparison_b",
                )

            team_a = comparison_data[comparison_data["team_name"] == team_a_name].iloc[0]
            team_b = comparison_data[comparison_data["team_name"] == team_b_name].iloc[0]

            st.markdown("")
            metric_cols = st.columns(4)
            metric_cols[0].metric(
                f"{team_a_name} · WIN RATE",
                f"{team_a['win_rate']:.1f}%",
                delta=f"{team_a['wins']} wins / {team_a['losses']} losses",
            )
            metric_cols[1].metric(
                f"{team_b_name} · WIN RATE",
                f"{team_b['win_rate']:.1f}%",
                delta=f"{team_b['wins']} wins / {team_b['losses']} losses",
            )
            metric_cols[2].metric(
                f"{team_a_name} · MAPS",
                format_number(team_a["maps_played"]),
            )
            metric_cols[3].metric(
                f"{team_b_name} · MAPS",
                format_number(team_b["maps_played"]),
            )

            chart_rows = []
            for _, team_row in [(team_a_name, team_a), (team_b_name, team_b)]:
                chart_rows.extend([
                    {"Team": team_row["team_name"], "Metric": "Wins", "Value": int(team_row["wins"])},
                    {"Team": team_row["team_name"], "Metric": "Losses", "Value": int(team_row["losses"])},
                ])

            comparison_chart_data = pd.DataFrame(chart_rows)
            comp_left, comp_right = st.columns([1.15, 1])

            with comp_left:
                fig = px.bar(
                    comparison_chart_data,
                    x="Metric",
                    y="Value",
                    color="Team",
                    barmode="group",
                    color_discrete_sequence=["#FF4655", "#777783"],
                    text="Value",
                )
                fig.update_traces(textposition="outside")
                fig.update_layout(
                    xaxis_title=None,
                    yaxis_title="Map count",
                    legend_title=None,
                )
                st.plotly_chart(
                    plotly_dark(fig, 330),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )

            with comp_right:
                metric_compare = pd.DataFrame([
                    {
                        "Metric": "Win Rate (%)",
                        team_a_name: float(team_a["win_rate"] or 0),
                        team_b_name: float(team_b["win_rate"] or 0),
                    },
                    {
                        "Metric": "Average Total Rounds",
                        team_a_name: float(team_a["avg_total_rounds"] or 0),
                        team_b_name: float(team_b["avg_total_rounds"] or 0),
                    },
                    {
                        "Metric": "Average Rounds Won",
                        team_a_name: float(team_a["avg_rounds_won"] or 0),
                        team_b_name: float(team_b["avg_rounds_won"] or 0),
                    },
                ])
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name=team_a_name,
                    x=metric_compare["Metric"],
                    y=metric_compare[team_a_name],
                    marker_color="#FF4655",
                ))
                fig.add_trace(go.Bar(
                    name=team_b_name,
                    x=metric_compare["Metric"],
                    y=metric_compare[team_b_name],
                    marker_color="#777783",
                ))
                fig.update_layout(
                    barmode="group",
                    yaxis_title="Value",
                    xaxis_title=None,
                    legend_title=None,
                )
                st.plotly_chart(
                    plotly_dark(fig, 330),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )

            comparison_table = pd.DataFrame([
                {
                    "Team": team_a_name,
                    "Maps Played": int(team_a["maps_played"]),
                    "Wins": int(team_a["wins"]),
                    "Losses": int(team_a["losses"]),
                    "Win Rate (%)": float(team_a["win_rate"]),
                    "Avg Total Rounds": float(team_a["avg_total_rounds"]),
                    "Avg Rounds Won": float(team_a["avg_rounds_won"]),
                },
                {
                    "Team": team_b_name,
                    "Maps Played": int(team_b["maps_played"]),
                    "Wins": int(team_b["wins"]),
                    "Losses": int(team_b["losses"]),
                    "Win Rate (%)": float(team_b["win_rate"]),
                    "Avg Total Rounds": float(team_b["avg_total_rounds"]),
                    "Avg Rounds Won": float(team_b["avg_rounds_won"]),
                },
            ])
            show_table(comparison_table, limit=2)
        else:
            empty_state("At least two teams with recorded map scores are required.")
    else:
        empty_state("No team map-score data is available for the current filters.")
else:
    empty_state("Team comparison requires team IDs and map score columns in the warehouse.")


# ============================================================
# MAP CONTROL / BATTLEFIELD ANALYTICS
# ============================================================

st.markdown("")
section_heading(
    "Map Control",
    "Map frequency and average total rounds using the map dimension.",
)

map_filter = f"""
    m.{safe_identifier(MAP_MATCH_ID)} IN (
        SELECT f.{safe_identifier(MATCH_ID)}
        FROM fact_match f
        {MATCH_JOIN}
        WHERE {FILTER_SQL}
    )
"""

map_join = (
    f'FROM fact_map m '
    f'JOIN dim_map dm '
    f'ON dm.{safe_identifier(MAP_KEY)} = m.{safe_identifier(MAP_KEY)}'
)

map_left, map_right = st.columns(2)

with map_left:
    st.markdown(
        """
        <div class="panel-title">Most Played Maps</div>
        <div class="panel-subtitle">Map appearances in filtered matches</div>
        """,
        unsafe_allow_html=True,
    )

    map_play_query = f"""
        SELECT
            dm.{safe_identifier(MAP_NAME)} AS map_name,
            COUNT(*) AS maps_played
        {map_join}
        WHERE {map_filter}
          AND dm.{safe_identifier(MAP_NAME)} IS NOT NULL
          AND TRIM(dm.{safe_identifier(MAP_NAME)}) != ''
        GROUP BY dm.{safe_identifier(MAP_NAME)}
        ORDER BY maps_played DESC
    """

    try:
        map_play_data = run_query(map_play_query, FILTER_PARAMS)
    except Exception:
        map_play_data = pd.DataFrame()

    if not map_play_data.empty:
        fig = px.bar(
            map_play_data.sort_values("maps_played", ascending=True),
            x="maps_played",
            y="map_name",
            orientation="h",
            color="maps_played",
            color_continuous_scale=["#69202B", "#FF4655"],
        )

        fig.update_layout(
            coloraxis_showscale=False,
            xaxis_title="Maps played",
            yaxis_title=None,
        )

        st.plotly_chart(
            plotly_dark(fig, 350),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    else:
        empty_state("Map names are unavailable for the current filters.")

with map_right:
    st.markdown(
        """
        <div class="panel-title">Battlefield Breakdown</div>
        <div class="panel-subtitle">Average total rounds per map</div>
        """,
        unsafe_allow_html=True,
    )

    map_rounds_query = f"""
        SELECT
            dm.{safe_identifier(MAP_NAME)} AS map_name,
            ROUND(
                AVG(
                    CAST(m.{safe_identifier(MAP_SCORE0)} AS REAL)
                    + CAST(m.{safe_identifier(MAP_SCORE1)} AS REAL)
                ),
                2
            ) AS avg_total_rounds,
            COUNT(*) AS maps_with_scores
        {map_join}
        WHERE {map_filter}
          AND dm.{safe_identifier(MAP_NAME)} IS NOT NULL
          AND TRIM(dm.{safe_identifier(MAP_NAME)}) != ''
          AND m.{safe_identifier(MAP_SCORE0)} IS NOT NULL
          AND m.{safe_identifier(MAP_SCORE1)} IS NOT NULL
          AND m.{safe_identifier(MAP_SCORE0)} >= 0
          AND m.{safe_identifier(MAP_SCORE1)} >= 0
        GROUP BY dm.{safe_identifier(MAP_NAME)}
        ORDER BY avg_total_rounds DESC
    """

    try:
        map_rounds_data = run_query(map_rounds_query, FILTER_PARAMS)
    except Exception:
        map_rounds_data = pd.DataFrame()

    if not map_rounds_data.empty:
        fig = px.bar(
            map_rounds_data.sort_values("avg_total_rounds", ascending=True),
            x="avg_total_rounds",
            y="map_name",
            orientation="h",
            color="avg_total_rounds",
            color_continuous_scale=["#69202B", "#FF4655", "#FF9AA3"],
            hover_data=["maps_with_scores"],
        )

        fig.update_layout(
            coloraxis_showscale=False,
            xaxis_title="Average total rounds",
            yaxis_title=None,
        )

        st.plotly_chart(
            plotly_dark(fig, 350),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    else:
        empty_state("Map score columns are unavailable for this selection.")


# ============================================================
# PLAYER SPOTLIGHT
# ============================================================

st.markdown("")
section_heading(
    "Player Spotlight",
    "Individual impact based on available player-map performance metrics.",
)

player_metric_options = []

for column, label in [
    (PM_ACS, "Average Combat Score"),
    (PM_RATING, "Rating"),
    (PM_KILLS, "Kills"),
    (PM_HS, "Headshot Percentage"),
    (PM_ADR, "Average Damage per Round"),
]:
    if column:
        player_metric_options.append((column, label))

if player_metric_options:
    chosen_metric_column, chosen_metric_label = player_metric_options[0]

    player_metric_label = st.selectbox(
        "RANK PLAYERS BY",
        options=[label for _, label in player_metric_options],
        index=0,
    )

    chosen_metric_column = next(
        column
        for column, label in player_metric_options
        if label == player_metric_label
    )

    metric_aggregate = (
        "AVG"
        if chosen_metric_column in [PM_ACS, PM_RATING, PM_HS, PM_ADR]
        else "SUM"
    )

    player_filter = f"""
        pm.{safe_identifier(PM_MATCH_ID)} IN (
            SELECT f.{safe_identifier(MATCH_ID)}
            FROM fact_match f
            {MATCH_JOIN}
            WHERE {FILTER_SQL}
        )
    """

    player_join = (
        f'LEFT JOIN dim_player p '
        f'ON p.{safe_identifier(PLAYER_ID)} = '
        f'pm.{safe_identifier(PM_PLAYER_ID)}'
    )

    player_query = f"""
        SELECT
            p.{safe_identifier(PLAYER_NAME)} AS player_name,
            COUNT(*) AS maps_played,
            ROUND(
                {metric_aggregate}(
                    CAST(pm.{safe_identifier(chosen_metric_column)} AS REAL)
                ),
                2
            ) AS selected_metric
            {f', ROUND(AVG(CAST(pm.{safe_identifier(PM_RATING)} AS REAL)), 2) AS avg_rating' if PM_RATING else ''}
            {f', ROUND(AVG(CAST(pm.{safe_identifier(PM_ACS)} AS REAL)), 2) AS avg_acs' if PM_ACS else ''}
            {f', SUM(pm.{safe_identifier(PM_KILLS)}) AS total_kills' if PM_KILLS else ''}
            {f', SUM(pm.{safe_identifier(PM_DEATHS)}) AS total_deaths' if PM_DEATHS else ''}
            {f', ROUND(AVG(CAST(pm.{safe_identifier(PM_HS)} AS REAL)), 2) AS avg_headshot_pct' if PM_HS else ''}
        FROM fact_player_map pm
        {player_join}
        WHERE {player_filter}
          AND p.{safe_identifier(PLAYER_NAME)} IS NOT NULL
          AND pm.{safe_identifier(chosen_metric_column)} IS NOT NULL
        GROUP BY p.{safe_identifier(PLAYER_ID)}, p.{safe_identifier(PLAYER_NAME)}
        HAVING COUNT(*) >= 3
        ORDER BY selected_metric DESC
        LIMIT 20
    """

    try:
        player_data = run_query(player_query, FILTER_PARAMS)
    except Exception:
        player_data = pd.DataFrame()

    if not player_data.empty:
        player_left, player_right = st.columns([1.1, 1])

        with player_left:
            fig = px.bar(
                player_data.head(12).sort_values(
                    "selected_metric",
                    ascending=True,
                ),
                x="selected_metric",
                y="player_name",
                orientation="h",
                color="selected_metric",
                color_continuous_scale=["#69202B", "#FF4655"],
                hover_data=["maps_played"],
            )

            fig.update_layout(
                coloraxis_showscale=False,
                xaxis_title=player_metric_label,
                yaxis_title=None,
            )

            st.plotly_chart(
                plotly_dark(fig, 460),
                use_container_width=True,
                config={"displayModeBar": False},
            )

        with player_right:
            st.markdown(
                f"""
                <div class="panel-title">Top Players</div>
                <div class="panel-subtitle">
                    Ranked by {escape(player_metric_label.lower())}
                </div>
                """,
                unsafe_allow_html=True,
            )

            show_table(
                player_data.rename(
                    columns={
                        "player_name": "Player",
                        "maps_played": "Maps",
                        "selected_metric": player_metric_label,
                        "avg_rating": "Avg Rating",
                        "avg_acs": "Avg ACS",
                        "total_kills": "Kills",
                        "total_deaths": "Deaths",
                        "avg_headshot_pct": "Avg HS %",
                    }
                ),
                limit=20,
            )
    else:
        empty_state(
            "Player performance metrics are unavailable for this selection."
        )
else:
    empty_state(
        "Player performance metrics are unavailable in the warehouse."
    )


# ============================================================
# AGENT USAGE
# ============================================================

st.markdown("")
section_heading(
    "Agent Intelligence",
    "Explore recorded agent selections across player-map appearances.",
)

if PM_AGENTS:
    agent_query = f"""
        SELECT
            pm.{safe_identifier(PM_AGENTS)} AS agent,
            COUNT(*) AS appearances
        FROM fact_player_map pm
        WHERE pm.{safe_identifier(PM_MATCH_ID)} IN (
            SELECT f.{safe_identifier(MATCH_ID)}
            FROM fact_match f
            {MATCH_JOIN}
            WHERE {FILTER_SQL}
        )
          AND pm.{safe_identifier(PM_AGENTS)} IS NOT NULL
          AND TRIM(pm.{safe_identifier(PM_AGENTS)}) != ''
        GROUP BY pm.{safe_identifier(PM_AGENTS)}
        ORDER BY appearances DESC
    """

    try:
        agent_data = run_query(agent_query, FILTER_PARAMS)

        if not agent_data.empty:
            import json

            def clean_agent_name(value):
                try:
                    parsed = json.loads(value)

                    if isinstance(parsed, list):
                        names = parsed
                    else:
                        names = [parsed]
                except (json.JSONDecodeError, TypeError):
                    names = [value]

                return ", ".join(
                    str(name).strip().title()
                    for name in names
                    if name and str(name).strip()
                )

            agent_data["agent"] = agent_data["agent"].apply(
                clean_agent_name
            )

            # Combine appearances when different raw values resolve
            # to the same displayed agent name.
            agent_data = (
                agent_data.groupby("agent", as_index=False)["appearances"]
                .sum()
                .sort_values("appearances", ascending=False)
                .head(15)
            )

    except Exception as error:
        st.error(f"Could not load agent data: {error}")
        agent_data = pd.DataFrame()
else:
    agent_data = pd.DataFrame()

if not agent_data.empty:
    agent_left, agent_right = st.columns([1.1, 1])

    with agent_left:
        fig = px.bar(
            agent_data.sort_values("appearances", ascending=True),
            x="appearances",
            y="agent",
            orientation="h",
            color="appearances",
            color_continuous_scale=["#69202B", "#FF4655"],
            labels={
                "agent": "Agent",
                "appearances": "Appearances",
            },
        )

        fig.update_layout(
            coloraxis_showscale=False,
            xaxis_title="Recorded appearances",
            yaxis_title=None,
        )

        st.plotly_chart(
            plotly_dark(fig, 420),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with agent_right:
        st.markdown(
            """
            <div class="panel-title">Top Agents</div>
            <div class="panel-subtitle">
                Most frequently recorded agent selections
            </div>
            """,
            unsafe_allow_html=True,
        )

        show_table(
            agent_data.rename(
                columns={
                    "agent": "Agent",
                    "appearances": "Appearances",
                }
            ),
            limit=15,
        )
else:
    empty_state(
        "Agent usage data is unavailable or agent selections are not recorded."
    )


# ============================================================
# MATCH EXPLORER
# ============================================================

st.markdown("")
section_heading(
    "Match Explorer",
    "Review individual matches included in the current analysis.",
)

match_explorer_columns = [
    f'f.{safe_identifier(MATCH_ID)} AS match_id'
]

if MATCH_DATE_KEY and DATE_KEY and DATE_YEAR:
    match_explorer_columns.append(
        f'd.{safe_identifier(DATE_YEAR)} AS year'
    )

if MATCH_REGION:
    match_explorer_columns.append(
        f'f.{safe_identifier(MATCH_REGION)} AS region'
    )

if MATCH_SCORE0:
    match_explorer_columns.append(
        f'f.{safe_identifier(MATCH_SCORE0)} AS score0'
    )

if MATCH_SCORE1:
    match_explorer_columns.append(
        f'f.{safe_identifier(MATCH_SCORE1)} AS score1'
    )

if MATCH_STATUS:
    match_explorer_columns.append(
        f'f.{safe_identifier(MATCH_STATUS)} AS status'
    )

if MATCH_EVENT_ID and EVENT_ID and EVENT_NAME:
    match_explorer_columns.append(
        f'e.{safe_identifier(EVENT_NAME)} AS tournament'
    )

if (
    MATCH_DATE_KEY
    and DATE_KEY
    and DATE_YEAR
):
    match_explorer_join = MATCH_JOIN
else:
    match_explorer_join = MATCH_JOIN

match_explorer_query = f"""
    SELECT {", ".join(match_explorer_columns)}
    FROM fact_match f
    {match_explorer_join}
    WHERE {FILTER_SQL}
    ORDER BY f.{safe_identifier(MATCH_ID)} DESC
    LIMIT 500
"""

try:
    explorer_data = run_query(
        match_explorer_query,
        FILTER_PARAMS,
    )
except Exception:
    explorer_data = pd.DataFrame()

if not explorer_data.empty:
    explorer_rename = {
        "match_id": "Match ID",
        "year": "Year",
        "region": "Region",
        "score0": "Team 1 Score",
        "score1": "Team 2 Score",
        "status": "Status",
        "tournament": "Tournament",
    }

    explorer_display = explorer_data.rename(
        columns={
            key: value
            for key, value in explorer_rename.items()
            if key in explorer_data.columns
        }
    )

    search_text = st.text_input(
        "SEARCH MATCHES",
        placeholder="Search by match ID, region, tournament or status...",
    )

    if search_text.strip():
        mask = explorer_display.astype(str).apply(
            lambda column: column.str.contains(
                search_text.strip(),
                case=False,
                na=False,
                regex=False,
            )
        ).any(axis=1)

        explorer_display = explorer_display[mask]

    show_table(explorer_display, limit=100)
else:
    empty_state("No matches are available for the selected filters.")


# ============================================================
# DATA QUALITY NOTES
# ============================================================

with st.expander("DATA NOTES & INTERPRETATION"):
    st.markdown(
        """
        - **Source:** Valorant esports reference database loaded into a local SQLite warehouse.
        - **Filters:** Year, region and tournament filters are applied to match-based analyses.
        - **Map names:** Map labels are retrieved from `dim_map` using `map_key`.
        - **Average rounds:** Calculated by adding the two recorded map scores. Rows with missing or negative scores are excluded.
        - **Player statistics:** Metrics are calculated from available player-map records. Missing metric values are excluded from the corresponding calculation.
        - **Win rate:** The team chart uses recorded score comparisons. Tied scores are excluded from the win-rate denominator.
        - **Agent usage:** Agent appearances are based on the agent values recorded in the player-map table.
        - **Coverage:** Filters can reduce the number of records available for individual charts.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        VALORANT ESPORTSIQ &nbsp; | &nbsp; BUSINESS INTELLIGENCE DASHBOARD
        <br>
        COMPETITIVE DATA · PERFORMANCE ANALYTICS · DATA-DRIVEN INSIGHTS
    </div>
    """,
    unsafe_allow_html=True,
)