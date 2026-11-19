import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely import wkt
import plotly.express as px
import plotly.graph_objects as go
import math
import numpy as np
import re
import os

# ==========================================
# PAGE CONFIG & TEAM MO EDITORIAL CSS
# ==========================================
st.set_page_config(page_title="Team MO · Missouri 2026 Results", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700;800&display=swap');

:root {
    --brand-navy: #10243e;
    --brand-blue: #1e4e8c;
    --brand-pale: #dbeafe;
    --brand-red: #c82427;
    --yes-3: #2e7d47;
    --yes-4: #1f6336;
    --no-3: #b8442a;
    --no-4: #8f2d18;
    --border-subtle: #e2e8f0;
    --muted-bg: #f4f6f9;
}

html, body, [class*="css"] {
    font-family: 'Figtree', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Hide default Streamlit top padding & menu clutter */
.block-container {
    padding-top: 1.25rem !important;
    padding-bottom: 3rem !important;
    max-width: 1280px;
}

/* Top Navy Masthead */
.team-mo-banner {
    background-color: var(--brand-navy);
    color: #ffffff;
    padding: 1.1rem 1.5rem;
    border-radius: 8px;
    border-bottom: 3px solid var(--brand-red);
    margin-bottom: 1.25rem;
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: baseline;
    gap: 0.75rem;
}
.team-mo-banner .brand-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.45rem;
    font-weight: 800;
    letter-spacing: -0.01em;
    color: #ffffff;
}
.team-mo-banner .brand-sub {
    font-family: 'Figtree', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #cbd5e1;
    margin-left: 0.65rem;
}
.team-mo-banner .brand-meta {
    font-size: 0.78rem;
    color: #cbd5e1;
    font-weight: 500;
}

/* Editorial Section Header */
.kicker {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: var(--brand-blue);
    margin-bottom: 0.2rem;
}
.hero-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2.15rem;
    font-weight: 700;
    line-height: 1.15;
    letter-spacing: -0.02em;
    margin: 0 0 0.45rem 0;
}
.badge-pill {
    display: inline-block;
    background-color: var(--brand-navy);
    color: #ffffff;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 0.2rem 0.55rem;
    border-radius: 3px;
    margin-right: 0.5rem;
}
.section-divider {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    border-bottom: 2px solid currentColor;
    padding-bottom: 0.35rem;
    margin-top: 2rem;
    margin-bottom: 1rem;
}
.section-divider h2 {
    font-family: 'Figtree', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 800 !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 0 !important;
    padding: 0 !important;
}
.section-divider span {
    font-size: 0.82rem;
    opacity: 0.72;
}

/* Measure & KPI Scorecard */
.scorecard {
    border: 1px solid rgba(148, 163, 184, 0.35);
    border-radius: 8px;
    padding: 1rem 1.1rem;
    height: 100%;
    transition: border-color 0.15s ease;
}
.scorecard:hover {
    border-color: var(--brand-blue);
}
.scorecard-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.5rem;
    margin-bottom: 0.65rem;
}
.scorecard-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.2rem;
    font-weight: 700;
    line-height: 1.2;
}
.scorecard-sub {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--brand-red);
    margin-top: 0.15rem;
}
.status-badge-win {
    background-color: var(--yes-4);
    color: #ffffff;
    font-size: 0.66rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    padding: 0.2rem 0.5rem;
    border-radius: 3px;
    white-space: nowrap;
}
.status-badge-loss {
    background-color: var(--no-4);
    color: #ffffff;
    font-size: 0.66rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    padding: 0.2rem 0.5rem;
    border-radius: 3px;
    white-space: nowrap;
}
.split-bar-wrap {
    display: flex;
    height: 11px;
    border-radius: 3px;
    overflow: hidden;
    background-color: #e2e8f0;
    margin: 0.55rem 0;
}
.split-bar-our {
    background-color: var(--yes-3);
    height: 100%;
}
.split-bar-other {
    background-color: var(--no-3);
    border-left: 2px solid #ffffff;
    height: 100%;
}
.split-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.74rem;
    opacity: 0.82;
    margin-bottom: 0.5rem;
    font-variant-numeric: tabular-nums;
}
.scorecard-margin {
    font-size: 0.85rem;
    font-variant-numeric: tabular-nums;
}
.scorecard-foot {
    font-size: 0.78rem;
    opacity: 0.72;
    margin-top: 0.2rem;
}
.absentee-banner {
    border-left: 3px solid var(--brand-blue);
    background-color: rgba(30, 78, 140, 0.08);
    padding: 0.6rem 0.9rem;
    border-radius: 4px;
    font-size: 0.84rem;
    margin-bottom: 0.85rem;
    font-variant-numeric: tabular-nums;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. FETCH SHAPES & ELECTION DATA (CACHED)
# ==========================================
@st.cache_data
def get_shapefile():
    file_path = "precincts_shape_2026.csv" if os.path.exists("precincts_shape_2026.csv") else "processed_data/precincts_shape_2026.csv"
    df = pd.read_csv(file_path)
    if 'shape_geometry' in df.columns and 'geometry' not in df.columns:
        df = df.rename(columns={'shape_geometry': 'geometry'})
    df['geometry'] = df['geometry'].apply(lambda x: wkt.loads(x) if pd.notnull(x) else None)
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
    gdf['geometry'] = gdf['geometry'].simplify(0.001)
    gdf['mapping_precinct_code'] = gdf['mapping_precinct_code'].astype(str).str.upper()
    return gdf

@st.cache_data
def get_election_data(table_name):
    file_path = f"{table_name}.csv" if os.path.exists(f"{table_name}.csv") else f"processed_data/{table_name}.csv"
    df = pd.read_csv(file_path)
    if not df.empty:
        df['mapping_precinct_code'] = df['mapping_precinct_code'].astype(str).str.upper()
        if 'race' in df.columns:
            df['race'] = df['race'].astype(str).str.replace('CONSTITUTIONAL ', '', regex=False)
            df['race'] = df['race'].str.replace('NO. ', '', regex=False)
            df['race'] = df['race'].str.strip()
        df['total_votes'] = pd.to_numeric(df.get('total_votes', 0), errors='coerce').fillna(0)
    return df

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]

# Measure campaign metadata matching Team MO framing
MEASURE_META = {
    "AMENDMENT 3": {
        "title": "Amendment 3",
        "subtitle": "Stop the Ban",
        "our_side": "NO",
        "other_side": "YES",
        "outcome_pass": "Passed",
        "outcome_fail": "Failed",
    },
    "AMENDMENT 6": {
        "title": "Amendment 6",
        "subtitle": "Respect Missouri Voters",
        "our_side": "YES",
        "other_side": "NO",
        "outcome_pass": "Passed",
        "outcome_fail": "Failed",
    },
    "PROPOSITION A": {
        "title": "Proposition A",
        "subtitle": "People Not Politicians",
        "our_side": "NO",
        "other_side": "YES",
        "outcome_pass": "Passed",
        "outcome_fail": "Failed",
    },
}

# ==========================================
# TOP MASTHEAD & CATEGORY NAVIGATION
# ==========================================
with st.spinner("Loading precinct election data..."):
    leg_full_df = get_election_data("legislative_races")
    bal_full_df = get_election_data("ballot_measures")
    shapes_df = get_shapefile()

loaded_counties = sorted(
    set(leg_full_df['County'].dropna().unique()).union(set(bal_full_df['County'].dropna().unique()))
) if ('County' in leg_full_df.columns or 'County' in bal_full_df.columns) else []

st.markdown(f"""
<div class="team-mo-banner">
    <div>
        <span class="brand-title">Team MO</span>
        <span class="brand-sub">Missouri 2026 Precinct Election Results</span>
    </div>
    <div class="brand-meta">General Election · November 3, 2026 · {len(loaded_counties)} Jurisdictions Loaded</div>
</div>
""", unsafe_allow_html=True)

dataset_type = st.radio(
    "View Section:",
    ["Ballot Initiatives", "State Legislature"],
    horizontal=True,
    label_visibility="collapsed",
)

full_election_df = bal_full_df if dataset_type == "Ballot Initiatives" else leg_full_df
if full_election_df.empty:
    st.error(f"No data found for {dataset_type}.")
    st.stop()

county_col = 'County' if 'County' in full_election_df.columns else 'county' if 'county' in full_election_df.columns else None

# ==========================================
# EDITORIAL HERO HEADER & SCORE CARDS
# ==========================================
if dataset_type == "Ballot Initiatives":
    st.markdown("""
    <div class="kicker">Missouri · November 3, 2026</div>
    <h1 class="hero-title">Ballot Initiative Results</h1>
    <div style="margin-bottom: 1.1rem;">
        <span class="badge-pill">Precinct Results</span>
        <span style="font-size: 0.78rem; opacity: 0.72;">Our side = NO on Amendment 3 &amp; Prop A · YES on Amendment 6</span>
    </div>
    """, unsafe_allow_html=True)

    # Render the 3-column GPS Impact Hero Cards across all loaded jurisdictions
    card_cols = st.columns(3)
    for idx, m_key in enumerate(["AMENDMENT 3", "AMENDMENT 6", "PROPOSITION A"]):
        meta = MEASURE_META[m_key]
        m_df = bal_full_df[bal_full_df['race'].str.upper() == m_key].copy()
        if not m_df.empty:
            m_df['YES'] = pd.to_numeric(m_df['YES'], errors='coerce').fillna(0)
            m_df['NO'] = pd.to_numeric(m_df['NO'], errors='coerce').fillna(0)
            yes_tot = int(m_df['YES'].sum())
            no_tot = int(m_df['NO'].sum())
            tot_v = yes_tot + no_tot

            our_v = yes_tot if meta['our_side'] == "YES" else no_tot
            other_v = no_tot if meta['our_side'] == "YES" else yes_tot
            our_pct = (our_v / tot_v * 100) if tot_v > 0 else 0.0
            other_pct = (other_v / tot_v * 100) if tot_v > 0 else 0.0
            diff_pts = our_pct - other_pct
            diff_votes = abs(our_v - other_v)

            # Yes > No determines whether measure Passed or Failed
            passed = yes_tot > no_tot
            status_text = f"{'Passed' if passed else 'Failed'} {'✓' if diff_pts > 0 else ''}"
            badge_cls = "status-badge-win" if diff_pts > 0 else "status-badge-loss"

            # Count jurisdictions won by our side
            if county_col:
                c_grp = m_df.groupby(county_col)[['YES', 'NO']].sum()
                if meta['our_side'] == "YES":
                    won_cnt = int((c_grp['YES'] > c_grp['NO']).sum())
                else:
                    won_cnt = int((c_grp['NO'] > c_grp['YES']).sum())
                tot_cnt = len(c_grp)
            else:
                won_cnt, tot_cnt = 0, 0

            lead_side = meta['our_side'].title() if diff_pts >= 0 else meta['other_side'].title()
            with card_cols[idx]:
                st.markdown(f"""
                <div class="scorecard">
                    <div class="scorecard-top">
                        <div>
                            <div class="scorecard-title">{meta['title']}</div>
                            <div class="scorecard-sub">{meta['subtitle']}</div>
                        </div>
                        <span class="{badge_cls}">{status_text}</span>
                    </div>
                    <div class="split-bar-wrap">
                        <div class="split-bar-our" style="width: {our_pct:.2f}%;"></div>
                        <div class="split-bar-other" style="width: {other_pct:.2f}%;"></div>
                    </div>
                    <div class="split-labels">
                        <span>Our side · {meta['our_side'].title()} {our_pct:.2f}% ({our_v:,})</span>
                        <span>Other · {meta['other_side'].title()} {other_pct:.2f}% ({other_v:,})</span>
                    </div>
                    <div class="scorecard-margin">
                        <span style="opacity:0.72;">Margin: </span>
                        <b>{lead_side} +{abs(diff_pts):.2f} pts</b>
                        <span style="opacity:0.72;"> ({diff_votes:,} votes)</span>
                    </div>
                    <div class="scorecard-foot">Our side won {won_cnt} of {tot_cnt} loaded jurisdictions</div>
                </div>
                """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="kicker">Missouri · November 3, 2026</div>
    <h1 class="hero-title">State Legislature Precinct Results</h1>
    <div style="margin-bottom: 0.75rem;">
        <span class="badge-pill">Precinct Results</span>
        <span style="font-size: 0.78rem; opacity: 0.72;">Missouri House &amp; Even-Numbered State Senate Districts</span>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# SECTION 1: PRECINCT CHOROPLETH & BREAKDOWN
# ==========================================
st.markdown(f"""
<div class="section-divider">
    <h2>Results by Precinct</h2>
    <span>Select jurisdiction and {'measure' if dataset_type == 'Ballot Initiatives' else 'chamber / district'}</span>
</div>
""", unsafe_allow_html=True)

f_col1, f_col2, f_col3 = st.columns([1.1, 1.1, 1.3])

if county_col:
    county_list = ["ALL"] + sorted(full_election_df[county_col].dropna().unique().tolist())
    with f_col1:
        selected_county = st.selectbox("Jurisdiction / County:", county_list)
else:
    selected_county = "ALL"

county_df = full_election_df[full_election_df[county_col] == selected_county].copy() if selected_county != "ALL" else full_election_df.copy()

race_totals = county_df.groupby('race')['total_votes'].sum()
valid_races = race_totals[race_totals > 0].index.tolist()

if dataset_type == "State Legislature":
    with f_col2:
        chamber = st.selectbox("Chamber:", ["State House (HD)", "State Senate (SD)", "All Legislative"])
    if chamber == "State House (HD)":
        chamber_races = [r for r in valid_races if 'REP' in r.upper() or 'HOUSE' in r.upper()]
    elif chamber == "State Senate (SD)":
        chamber_races = [r for r in valid_races if 'SENAT' in r.upper()]
    else:
        chamber_races = valid_races
    sorted_races = sorted(chamber_races, key=natural_sort_key)
    with f_col3:
        if not sorted_races:
            st.warning("No districts with reported votes in this jurisdiction.")
            st.stop()
        selected_race = st.selectbox("District:", ["ALL"] + sorted_races)
else:
    sorted_races = sorted(valid_races, key=natural_sort_key)
    with f_col2:
        if not sorted_races:
            st.warning("No ballot measures found for this selection.")
            st.stop()
        selected_race = st.selectbox("2026 Measure:", sorted_races)
    with f_col3:
        st.caption("Color scale: Green = Our side ahead · Rust/Terracotta = Other side ahead")

election_df = county_df[county_df['race'].isin(sorted_races)].copy() if selected_race == "ALL" else county_df[county_df['race'] == selected_race].copy()

if not election_df.empty:
    raw_df = pd.merge(election_df, shapes_df[['mapping_precinct_code', 'geometry']], on='mapping_precinct_code', how='left')

    if dataset_type == "State Legislature":
        dem_cols = [c for c in raw_df.columns if 'DEM' in c.upper()]
        rep_cols = [c for c in raw_df.columns if 'REP' in c.upper()]
        raw_df['Unified_Blue'] = raw_df[dem_cols].apply(pd.to_numeric, errors='coerce').fillna(0).sum(axis=1) if dem_cols else 0
        raw_df['Unified_Red'] = raw_df[rep_cols].apply(pd.to_numeric, errors='coerce').fillna(0).sum(axis=1) if rep_cols else 0
        blue_label, red_label, pct_label = 'Dem Votes', 'Rep Votes', 'Dem %'
        our_side_name, other_side_name = 'Democrat', 'Republican'
    else:
        raw_df['YES'] = pd.to_numeric(raw_df.get('YES', 0), errors='coerce').fillna(0)
        raw_df['NO'] = pd.to_numeric(raw_df.get('NO', 0), errors='coerce').fillna(0)
        if "AMENDMENT 6" in str(selected_race).upper():
            raw_df['Unified_Blue'] = raw_df['YES']
            raw_df['Unified_Red'] = raw_df['NO']
            blue_label, red_label, pct_label = 'YES Votes (Our side)', 'NO Votes (Other side)', 'YES %'
            our_side_name, other_side_name = 'Yes (Our side)', 'No (Other side)'
        else:
            raw_df['Unified_Blue'] = raw_df['NO']
            raw_df['Unified_Red'] = raw_df['YES']
            blue_label, red_label, pct_label = 'NO Votes (Our side)', 'YES Votes (Other side)', 'NO %'
            our_side_name, other_side_name = 'No (Our side)', 'Yes (Other side)'

    agg_dict = {
        'Unified_Blue': 'sum',
        'Unified_Red': 'sum',
        'total_votes': 'sum',
        'geometry': 'first',
    }
    precinct_col = 'precinct' if 'precinct' in raw_df.columns else 'precinctname' if 'precinctname' in raw_df.columns else 'mapping_precinct_code'
    if precinct_col != 'mapping_precinct_code':
        agg_dict[precinct_col] = 'first'
    if county_col:
        agg_dict[county_col] = 'first'
    if 'race' in raw_df.columns:
        agg_dict['race'] = 'first'

    master_df = raw_df.groupby('mapping_precinct_code').agg(agg_dict).reset_index()
    master_df['precinct_id'] = master_df.index.astype(str)
    master_df['Blue_Percent'] = (master_df['Unified_Blue'] / master_df['total_votes'] * 100).fillna(0).clip(0, 100)
    master_df['Red_Percent'] = (master_df['Unified_Red'] / master_df['total_votes'] * 100).fillna(0).clip(0, 100)
    master_df['Margin_Pts'] = master_df['Blue_Percent'] - master_df['Red_Percent']

    bins = [-1, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 101]
    bucket_labels = [
        '< 20%', '20–25%', '25–30%', '30–35%', '35–40%',
        '40–45%', '45–50%', '50–55%', '55–60%', '60–65%',
        '65–70%', '70–75%', '75–80%', '> 80%'
    ]
    master_df['Margin'] = pd.cut(master_df['Blue_Percent'], bins=bins, labels=bucket_labels)
    gray_label = '< 5 Votes (Gray)'
    master_df['Margin'] = master_df['Margin'].cat.add_categories([gray_label])
    master_df.loc[master_df['total_votes'] < 5, 'Margin'] = gray_label
    bucket_labels_full = bucket_labels + [gray_label]

    # Split mapped vs unmapped/absentee
    absentee_df = master_df[master_df['geometry'].isna()].copy()
    gdf = gpd.GeoDataFrame(master_df.dropna(subset=['geometry']).copy(), geometry='geometry', crs="EPSG:4326")

    # Region totals
    tot_reg_votes = int(master_df['total_votes'].sum())
    tot_reg_blue = int(master_df['Unified_Blue'].sum())
    tot_reg_red = int(master_df['Unified_Red'].sum())
    pct_reg_blue = (tot_reg_blue / tot_reg_votes * 100) if tot_reg_votes > 0 else 0.0
    pct_reg_red = (tot_reg_red / tot_reg_votes * 100) if tot_reg_votes > 0 else 0.0
    reg_spread = pct_reg_blue - pct_reg_red

    # Quick Zoom Presets matching Team MO
    zoom_preset = st.radio(
        "Map Viewport:",
        ["Whole Selection", "St. Louis Metro", "Kansas City Metro", "Springfield / SW MO"],
        horizontal=True,
    )

    # GPS Impact 1.45fr : 1fr Split Layout (Map on Left, Summary & Discrete Legend on Right)
    map_col, info_col = st.columns([1.5, 1.0])

    bucket_colors = {
        '< 20%': '#642b1a',
        '20–25%': '#8b3d23',
        '25–30%': '#a75235',
        '30–35%': '#c87659',
        '35–40%': '#e49b80',
        '40–45%': '#f3c4b5',
        '45–50%': '#fbe2dc',
        '50–55%': '#dceadc',
        '55–60%': '#b8d5b8',
        '60–65%': '#95c095',
        '65–70%': '#6cac6c',
        '70–75%': '#469146',
        '75–80%': '#2d762d',
        '> 80%': '#1b4d1b',
        gray_label: '#475569'
    }

    with map_col:
        if not gdf.empty:
            if zoom_preset == "St. Louis Metro":
                center_lat, center_lon, zoom_level = 38.63, -90.28, 9.6
            elif zoom_preset == "Kansas City Metro":
                center_lat, center_lon, zoom_level = 39.05, -94.45, 9.4
            elif zoom_preset == "Springfield / SW MO":
                center_lat, center_lon, zoom_level = 37.18, -93.29, 9.4
            else:
                bounds = gdf.total_bounds
                center_lon = (bounds[0] + bounds[2]) / 2
                center_lat = (bounds[1] + bounds[3]) / 2
                max_span = max(bounds[2] - bounds[0], bounds[3] - bounds[1])
                zoom_level = max(5.2, math.log2(360 / max_span) - 1.1) if max_span > 0 else 8.0

            hover_dict = {
                precinct_col: False,
                'race': True,
                'total_votes': True,
                'Unified_Blue': True,
                'Unified_Red': True,
                'Blue_Percent': ':.1f',
            }
            if county_col:
                hover_dict[county_col] = True

            fig = px.choropleth_map(
                gdf,
                geojson=gdf.geometry,
                locations='precinct_id',
                color='Margin',
                color_discrete_map=bucket_colors,
                category_orders={"Margin": bucket_labels_full},
                hover_name=precinct_col,
                hover_data=hover_dict,
                map_style="carto-positron",
                opacity=0.82,
                zoom=zoom_level,
                center={"lat": center_lat, "lon": center_lon},
                labels={
                    'Blue_Percent': pct_label,
                    'Unified_Blue': blue_label,
                    'Unified_Red': red_label,
                    'race': 'Race',
                    'total_votes': 'Total Votes',
                },
            )
            fig.update_layout(
                margin={"r": 0, "t": 0, "l": 0, "b": 0},
                height=680,
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No mappable precinct polygons found for this selection.")

    with info_col:
        # Region Summary Scorecard
        win_side = our_side_name if reg_spread >= 0 else other_side_name
        win_cls = "status-badge-win" if reg_spread >= 0 else "status-badge-loss"
        prec_won = int((master_df[master_df['total_votes'] > 0]['Unified_Blue'] > master_df[master_df['total_votes'] > 0]['Unified_Red']).sum())
        prec_tot = int((master_df['total_votes'] > 0).sum())

        st.markdown(f"""
        <div class="scorecard" style="height: auto; margin-bottom: 1rem;">
            <div class="scorecard-top">
                <div>
                    <div class="kicker" style="margin-bottom:0;">{selected_county}</div>
                    <div class="scorecard-title" style="font-size:1.15rem;">{selected_race}</div>
                </div>
                <span class="{win_cls}">{win_side} +{abs(reg_spread):.2f} pts</span>
            </div>
            <div class="split-bar-wrap">
                <div class="split-bar-our" style="width: {pct_reg_blue:.2f}%;"></div>
                <div class="split-bar-other" style="width: {pct_reg_red:.2f}%;"></div>
            </div>
            <div class="split-labels">
                <span><b>{our_side_name}:</b> {pct_reg_blue:.2f}% ({tot_reg_blue:,})</span>
                <span><b>{other_side_name}:</b> {pct_reg_red:.2f}% ({tot_reg_red:,})</span>
            </div>
            <div class="scorecard-foot">
                <b>{tot_reg_votes:,}</b> total ballots · {our_side_name} ahead in <b>{prec_won} of {prec_tot}</b> reporting units
            </div>
        </div>
        """, unsafe_allow_html=True)

        # GPS Impact 14-Step Horizontal Color Strip Legend
        st.markdown(f"""
        <div style="margin-bottom: 1rem;">
            <div style="display:flex; justify-content:space-between; font-size:0.75rem; opacity:0.75; margin-bottom:4px;">
                <span>← {other_side_name} ahead</span>
                <span>{our_side_name} ahead →</span>
            </div>
            <div style="display:grid; grid-template-columns: repeat(14, 1fr); gap:2px;">
                <span style="height:10px; background:#642b1a;"></span>
                <span style="height:10px; background:#8b3d23;"></span>
                <span style="height:10px; background:#a75235;"></span>
                <span style="height:10px; background:#c87659;"></span>
                <span style="height:10px; background:#e49b80;"></span>
                <span style="height:10px; background:#f3c4b5;"></span>
                <span style="height:10px; background:#fbe2dc;"></span>
                <span style="height:10px; background:#dceadc;"></span>
                <span style="height:10px; background:#b8d5b8;"></span>
                <span style="height:10px; background:#95c095;"></span>
                <span style="height:10px; background:#6cac6c;"></span>
                <span style="height:10px; background:#469146;"></span>
                <span style="height:10px; background:#2d762d;"></span>
                <span style="height:10px; background:#1b4d1b;"></span>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:0.68rem; opacity:0.68; margin-top:3px; font-variant-numeric: tabular-nums;">
                <span>&lt;20%</span>
                <span>35%</span>
                <span>50%</span>
                <span>65%</span>
                <span>&gt;80%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Absentee / Unmapped Callout
        if not absentee_df.empty:
            tot_abs = int(absentee_df['total_votes'].sum())
            tot_blue_abs = int(absentee_df['Unified_Blue'].sum())
            tot_red_abs = int(absentee_df['Unified_Red'].sum())
            if tot_abs > 0:
                abs_b_pct = tot_blue_abs / tot_abs * 100
                abs_r_pct = tot_red_abs / tot_abs * 100
                st.markdown(f"""
                <div class="absentee-banner">
                    <b>Absentee / Central Count (Unmapped Polygons):</b><br>
                    {tot_abs:,} ballots · <b>{tot_blue_abs:,}</b> {our_side_name} ({abs_b_pct:.1f}%) · <b>{tot_red_abs:,}</b> {other_side_name} ({abs_r_pct:.1f}%)
                </div>
                """, unsafe_allow_html=True)

        st.caption("Hover over any precinct polygon on the map for exact vote counts and shares. Use the table below to sort or download CSV results.")

    # ==========================================
    # SECTION 2: PRECINCT RESULTS TABLE + CSV EXPORT
    # ==========================================
    st.markdown(f"""
    <div class="section-divider">
        <h2>Precinct-Level Breakdown · {len(master_df)} Reporting Units</h2>
        <span>Click any column header to sort</span>
    </div>
    """, unsafe_allow_html=True)

    disp_cols = [county_col, precinct_col, 'total_votes', 'Unified_Blue', 'Unified_Red', 'Blue_Percent', 'Margin_Pts'] if county_col else [precinct_col, 'total_votes', 'Unified_Blue', 'Unified_Red', 'Blue_Percent', 'Margin_Pts']
    table_df = master_df[disp_cols].copy()

    def fmt_margin(val):
        if pd.isna(val):
            return "—"
        prefix = our_side_name.split()[0] if val >= 0 else other_side_name.split()[0]
        return f"{prefix} +{abs(val):.2f}"

    table_df['Margin'] = table_df['Margin_Pts'].apply(fmt_margin)
    table_df = table_df.drop(columns=['Margin_Pts'])

    rename_map = {
        precinct_col: 'Precinct',
        'total_votes': 'Total Votes',
        'Unified_Blue': blue_label,
        'Unified_Red': red_label,
        'Blue_Percent': pct_label,
    }
    if county_col:
        rename_map[county_col] = 'County'
    table_df = table_df.rename(columns=rename_map)

    sort_by = ['County', 'Precinct'] if 'County' in table_df.columns else ['Precinct']
    table_df = table_df.sort_values(by=sort_by)

    csv_bytes = table_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Precinct Table (CSV)",
        data=csv_bytes,
        file_name=f"mo_2026_{selected_county}_{selected_race}.csv".replace(" ", "_").lower(),
        mime="text/csv",
    )

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Total Votes': st.column_config.NumberColumn(format="%d"),
            blue_label: st.column_config.NumberColumn(format="%d"),
            red_label: st.column_config.NumberColumn(format="%d"),
            pct_label: st.column_config.NumberColumn(format="%.2f%%"),
        },
    )

    # ==========================================
    # SECTION 3: MEASURE VS. MEASURE / CROSS-RACE SCATTER (BALLOT VIEW)
    # ==========================================
    if dataset_type == "Ballot Initiatives" and len(sorted_races) >= 2:
        st.markdown("""
        <div class="section-divider">
            <h2>Ballot Measure vs. Ballot Measure (Precinct Scatter)</h2>
            <span>Compare our side's vote share across two 2026 measures</span>
        </div>
        """, unsafe_allow_html=True)

        sc1, sc2 = st.columns(2)
        with sc1:
            m_x = st.selectbox("Horizontal Axis (Baseline Measure):", sorted_races, index=0, key="scatter_x")
        with sc2:
            default_y = min(2, len(sorted_races) - 1)
            m_y = st.selectbox("Vertical Axis (Comparison Measure):", sorted_races, index=default_y, key="scatter_y")

        def get_our_share_df(measure_name):
            sub = county_df[county_df['race'] == measure_name].copy()
            sub['YES'] = pd.to_numeric(sub['YES'], errors='coerce').fillna(0)
            sub['NO'] = pd.to_numeric(sub['NO'], errors='coerce').fillna(0)
            grp_cols = ['mapping_precinct_code', precinct_col] + ([county_col] if county_col else [])
            g = sub.groupby(grp_cols)[['YES', 'NO', 'total_votes']].sum().reset_index()
            g = g[g['total_votes'] >= 5]
            if "AMENDMENT 6" in measure_name.upper():
                g['our_pct'] = g['YES'] / (g['YES'] + g['NO']) * 100
            else:
                g['our_pct'] = g['NO'] / (g['YES'] + g['NO']) * 100
            return g

        df_x = get_our_share_df(m_x).rename(columns={'our_pct': 'X_Pct', 'total_votes': 'Votes_X'})
        df_y = get_our_share_df(m_y).rename(columns={'our_pct': 'Y_Pct', 'total_votes': 'Votes_Y'})
        merged_sc = pd.merge(df_x, df_y[['mapping_precinct_code', 'Y_Pct']], on='mapping_precinct_code')

        if not merged_sc.empty:
            merged_sc['Diff_Pts'] = merged_sc['Y_Pct'] - merged_sc['X_Pct']
            merged_sc['Status'] = np.where(merged_sc['Diff_Pts'] >= 0, f"{m_y} ran ahead", f"{m_y} ran behind")
            ahead_cnt = int((merged_sc['Diff_Pts'] >= 0).sum())

            st.markdown(
                f"**{m_y}** ran ahead of **{m_x}** in **{ahead_cnt} of {len(merged_sc)}** precincts "
                f"(average precinct shift: **{merged_sc['Diff_Pts'].mean():+.2f} pts**)."
            )

            sc_fig = px.scatter(
                merged_sc,
                x='X_Pct',
                y='Y_Pct',
                size='Votes_X',
                color='Status',
                color_discrete_map={
                    f"{m_y} ran ahead": "#2e7d47",
                    f"{m_y} ran behind": "#b8442a",
                },
                hover_name=precinct_col,
                hover_data={
                    county_col: True if county_col else False,
                    'X_Pct': ':.1f',
                    'Y_Pct': ':.1f',
                    'Diff_Pts': ':+.1f',
                    'Votes_X': True,
                    'Status': False,
                },
                labels={
                    'X_Pct': f"Our side on {m_x} (%)",
                    'Y_Pct': f"Our side on {m_y} (%)",
                    'Diff_Pts': 'Difference (pts)',
                    'Votes_X': 'Ballots Cast',
                },
            )
            sc_fig.add_shape(
                type="line", x0=0, y0=0, x1=100, y1=100,
                line=dict(color="rgba(100, 116, 139, 0.65)", width=1.5, dash="dash"),
            )
            sc_fig.update_layout(
                xaxis=dict(range=[0, 100]),
                yaxis=dict(range=[0, 100]),
                height=520,
                margin=dict(l=10, r=10, t=20, b=10),
            )
            st.plotly_chart(sc_fig, use_container_width=True)
else:
    st.warning("No data found for this selection.")

st.markdown("""
<div style="margin-top: 2.5rem; border-top: 1px solid rgba(148, 163, 184, 0.35); padding-top: 0.85rem; font-size: 0.76rem; opacity: 0.72;">
    Compiled by <b>Team MO</b> · Precinct outlines from US Census Bureau (TIGER/Line) &amp; county election authorities.
</div>
""", unsafe_allow_html=True)
