import geopandas as gpd
import streamlit as st

from config import ELECTION_CYCLES, MEASURE_META_BY_YEAR
from styles import (
    inject_styles,
    render_masthead,
    render_hero_header,
    render_section_divider,
    render_measure_scorecard,
    render_region_summary_panel,
    render_footer,
)
from data_loader import (
    get_shapefile,
    get_election_data,
    natural_sort_key,
    filter_races_by_chamber,
    prepare_precinct_results,
    prepare_scatter_comparison,
)
from charts import render_choropleth_map, render_precinct_table, render_measure_scatter

st.set_page_config(page_title="Team MO · Missouri Election Results", layout="wide")
inject_styles()

# ==========================================
# 1. TOP NAVIGATION & DATA LOAD
# ==========================================
nav1, nav2 = st.columns([1.0, 1.3])
with nav1:
    election_year = st.radio("Election Cycle:", list(ELECTION_CYCLES.keys()), horizontal=True)

cycle_cfg = ELECTION_CYCLES[election_year]
year_short = cycle_cfg["year_short"]

with nav2:
    dataset_type = st.radio(
        "Results Section:",
        ["Ballot Initiatives", cycle_cfg["race_section_label"]],
        horizontal=True,
    )

with st.spinner(f"Loading {election_year} precinct election data..."):
    leg_df = get_election_data(cycle_cfg["races_table"])
    bal_df = get_election_data(cycle_cfg["ballot_table"])
    shapes_df = get_shapefile(cycle_cfg["shapes_table"])

loaded_counties = (
    sorted(set(leg_df['County'].dropna()).union(set(bal_df['County'].dropna())))
    if ('County' in leg_df.columns or 'County' in bal_df.columns)
    else []
)
render_masthead(year_short, cycle_cfg["date_str"], len(loaded_counties))

full_df = bal_df if dataset_type == "Ballot Initiatives" else leg_df
if full_df.empty:
    st.error(f"No data file found for {election_year} — {dataset_type}.")
    st.stop()

county_col = 'County' if 'County' in full_df.columns else 'county' if 'county' in full_df.columns else None

# ==========================================
# 2. HERO HEADER & BALLOT SCORECARDS
# ==========================================
if dataset_type == "Ballot Initiatives":
    render_hero_header(cycle_cfg["date_str"], f"{year_short} Ballot Initiative Results", cycle_cfg["ballot_note"])
    cards = MEASURE_META_BY_YEAR[election_year]
    cols = st.columns(len(cards))
    for idx, (m_key, meta) in enumerate(cards.items()):
        m_df = bal_df[bal_df['race'].str.upper() == m_key]
        if not m_df.empty:
            yes_tot, no_tot = int(m_df['YES'].sum()), int(m_df['NO'].sum())
            tot_v = yes_tot + no_tot
            our_v = yes_tot if meta['our_side'] == "YES" else no_tot
            other_v = no_tot if meta['our_side'] == "YES" else yes_tot
            our_pct = (our_v / tot_v * 100) if tot_v > 0 else 0.0
            other_pct = (other_v / tot_v * 100) if tot_v > 0 else 0.0
            diff_pts = our_pct - other_pct

            c_grp = m_df.groupby(county_col)[['YES', 'NO']].sum()
            won_cnt = int(((c_grp['YES'] > c_grp['NO']) if meta['our_side'] == "YES" else (c_grp['NO'] > c_grp['YES'])).sum())

            our_lbl = f"{'Our side · ' if cycle_cfg['is_team_mo_framed'] else ''}{meta['our_side'].title()}"
            other_lbl = f"{'Other · ' if cycle_cfg['is_team_mo_framed'] else ''}{meta['other_side'].title()}"
            foot_prefix = "Our side won" if cycle_cfg["is_team_mo_framed"] else "Yes led in"

            with cols[idx]:
                render_measure_scorecard(
                    title=meta['title'],
                    subtitle=meta['subtitle'],
                    badge_text=f"{'Passed' if yes_tot > no_tot else 'Failed'} {'✓' if diff_pts > 0 else ''}",
                    is_win=diff_pts > 0,
                    our_label=our_lbl,
                    other_label=other_lbl,
                    our_v=our_v,
                    other_v=other_v,
                    our_pct=our_pct,
                    other_pct=other_pct,
                    lead_side=meta['our_side'].title() if diff_pts >= 0 else meta['other_side'].title(),
                    diff_pts=diff_pts,
                    foot_text=f"{foot_prefix} {won_cnt} of {len(c_grp)} loaded jurisdictions",
                )
else:
    render_hero_header(cycle_cfg["date_str"], cycle_cfg["race_hero_title"], cycle_cfg["race_hero_sub"])

# ==========================================
# 3. FILTERS, CHOROPLETH MAP & SUMMARY
# ==========================================
render_section_divider(
    "Results by Precinct",
    f"Select jurisdiction and {'measure' if dataset_type == 'Ballot Initiatives' else 'office / district'}",
)

f1, f2, f3 = st.columns([1.1, 1.1, 1.3])
with f1:
    selected_county = st.selectbox(
        "Jurisdiction / County:",
        ["ALL"] + sorted(full_df[county_col].dropna().unique()),
        key=f"county_{year_short}_{dataset_type}",
    )

county_df = full_df if selected_county == "ALL" else full_df[full_df[county_col] == selected_county]
valid_races = county_df.groupby('race')['total_votes'].sum()
valid_races = valid_races[valid_races > 0].index.tolist()

if dataset_type != "Ballot Initiatives":
    with f2:
        chamber = st.selectbox("Office / Chamber:", cycle_cfg["chambers"], key=f"chamber_{year_short}")
    sorted_races = filter_races_by_chamber(valid_races, chamber)
    with f3:
        if not sorted_races:
            st.warning("No districts with reported votes in this jurisdiction.")
            st.stop()
        race_choices = sorted_races if chamber == "Federal & Statewide" else ["ALL"] + sorted_races
        selected_race = st.selectbox("Race / District:", race_choices, key=f"race_{year_short}_{chamber}")
else:
    sorted_races = sorted(valid_races, key=natural_sort_key)
    with f2:
        if not sorted_races:
            st.warning("No ballot measures found for this selection.")
            st.stop()
        selected_race = st.selectbox(f"{year_short} Measure:", sorted_races, key=f"bal_{year_short}")
    with f3:
        st.caption("Color scale: Green = Our side / Yes ahead · Rust/Terracotta = Other side / No ahead")

election_df = (
    county_df[county_df['race'].isin(sorted_races)]
    if selected_race == "ALL"
    else county_df[county_df['race'] == selected_race]
)

if not election_df.empty:
    master_df, labels, precinct_col, county_col = prepare_precinct_results(
        election_df, shapes_df, election_year, dataset_type, selected_race
    )
    _, _, _, our_name, other_name = labels

    absentee_df = master_df[master_df['geometry'].isna()]
    gdf = gpd.GeoDataFrame(master_df.dropna(subset=['geometry']), geometry='geometry', crs="EPSG:4326")

    zoom_preset = st.radio(
        "Map Viewport:",
        ["Whole Selection", "St. Louis Metro", "Kansas City Metro", "Springfield / SW MO"],
        horizontal=True,
    )

    map_col, info_col = st.columns([1.5, 1.0])
    with map_col:
        render_choropleth_map(gdf, zoom_preset, precinct_col, county_col, labels)

    with info_col:
        tot_v = int(master_df['total_votes'].sum())
        tot_b = int(master_df['Unified_Blue'].sum())
        tot_r = int(master_df['Unified_Red'].sum())
        pct_b = (tot_b / tot_v * 100) if tot_v > 0 else 0.0
        pct_r = (tot_r / tot_v * 100) if tot_v > 0 else 0.0
        won_p = int((master_df[master_df['total_votes'] > 0]['Unified_Blue'] > master_df[master_df['total_votes'] > 0]['Unified_Red']).sum())
        tot_p = int((master_df['total_votes'] > 0).sum())

        render_region_summary_panel(
            kicker=f"{selected_county} · {year_short}",
            title=selected_race,
            our_name=our_name,
            other_name=other_name,
            tot_v=tot_v,
            tot_b=tot_b,
            tot_r=tot_r,
            pct_b=pct_b,
            pct_r=pct_r,
            won_p=won_p,
            tot_p=tot_p,
            absentee_df=absentee_df,
            unmapped_note=cycle_cfg["unmapped_note"],
        )

    # ==========================================
    # 4. PRECINCT TABLE & MEASURE SCATTER
    # ==========================================
    render_section_divider(f"Precinct-Level Breakdown · {len(master_df)} Reporting Units", "Click any column header to sort")
    render_precinct_table(master_df, precinct_col, county_col, labels, year_short, selected_county, selected_race)

    if dataset_type == "Ballot Initiatives" and len(sorted_races) >= 2:
        render_section_divider(
            "Ballot Measure vs. Ballot Measure (Precinct Scatter)",
            f"Compare vote share across two {year_short} measures",
        )
        sc1, sc2 = st.columns(2)
        with sc1:
            m_x = st.selectbox("Horizontal Axis (Baseline Measure):", sorted_races, index=0, key=f"sc_x_{year_short}")
        with sc2:
            m_y = st.selectbox("Vertical Axis (Comparison Measure):", sorted_races, index=min(2, len(sorted_races) - 1), key=f"sc_y_{year_short}")

        merged_sc = prepare_scatter_comparison(county_df, election_year, m_x, m_y, precinct_col, county_col)
        render_measure_scatter(merged_sc, m_x, m_y, precinct_col, county_col)
else:
    st.warning("No data found for this selection.")

render_footer()