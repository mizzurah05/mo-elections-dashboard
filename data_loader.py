import os
import re
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import wkt
import streamlit as st
from config import MEASURE_META_BY_YEAR, BUCKET_BINS, BUCKET_LABELS, GRAY_LABEL


def _resolve_csv_path(table_name: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, f"{table_name}.csv"),
        os.path.join(base_dir, "processed_data", f"{table_name}.csv"),
        os.path.join(base_dir, "..", "..", "mo-election-dashboard", f"{table_name}.csv"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return f"{table_name}.csv"


@st.cache_data
def get_shapefile(shape_table: str = "precincts_shape_2026") -> gpd.GeoDataFrame:
    file_path = _resolve_csv_path(shape_table)
    df = pd.read_csv(file_path)
    if 'shape_geometry' in df.columns and 'geometry' not in df.columns:
        df = df.rename(columns={'shape_geometry': 'geometry'})
    df['geometry'] = df['geometry'].apply(lambda x: wkt.loads(x) if pd.notnull(x) else None)
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
    gdf['geometry'] = gdf['geometry'].simplify(0.001)
    gdf['mapping_precinct_code'] = gdf['mapping_precinct_code'].astype(str).str.upper()
    return gdf


@st.cache_data
def get_election_data(table_name: str) -> pd.DataFrame:
    file_path = _resolve_csv_path(table_name)
    if not os.path.exists(file_path):
        return pd.DataFrame()
    df = pd.read_csv(file_path)
    if not df.empty:
        df['mapping_precinct_code'] = df['mapping_precinct_code'].astype(str).str.upper()
        if 'race' in df.columns:
            df['race'] = (
                df['race'].astype(str)
                .str.replace('CONSTITUTIONAL ', '', regex=False)
                .str.replace('NO. ', '', regex=False)
                .str.strip()
            )
        df['total_votes'] = pd.to_numeric(df.get('total_votes', 0), errors='coerce').fillna(0)
    return df


def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]


def get_measure_our_side(year_label: str, race_name: str) -> str:
    return (
        MEASURE_META_BY_YEAR
        .get(year_label, {})
        .get(str(race_name).upper().strip(), {})
        .get("our_side", "YES")
    )


def filter_races_by_chamber(valid_races: list[str], chamber: str) -> list[str]:
    if chamber == "Federal & Statewide":
        races = [
            r for r in valid_races
            if r.upper() in ["U.S. SENATOR", "STATE AUDITOR"] or r.upper().startswith("U.S. REPRESENTATIVE")
        ]
    elif chamber == "State House (HD)":
        races = [r for r in valid_races if 'STATE REPRESENTATIVE' in r.upper() or 'HOUSE' in r.upper()]
    elif chamber == "State Senate (SD)":
        races = [r for r in valid_races if 'STATE SENAT' in r.upper()]
    else:
        races = valid_races
    return sorted(races, key=natural_sort_key)


def prepare_precinct_results(
    election_df: pd.DataFrame,
    shapes_df: gpd.GeoDataFrame,
    election_year: str,
    dataset_type: str,
    selected_race: str,
):
    raw_df = pd.merge(
        election_df,
        shapes_df[['mapping_precinct_code', 'geometry']],
        on='mapping_precinct_code',
        how='left',
    )

    if dataset_type != "Ballot Initiatives":
        dem_cols = [c for c in raw_df.columns if 'DEM' in c.upper()]
        rep_cols = [c for c in raw_df.columns if 'REP' in c.upper()]
        raw_df['Unified_Blue'] = raw_df[dem_cols].apply(pd.to_numeric, errors='coerce').fillna(0).sum(axis=1) if dem_cols else 0
        raw_df['Unified_Red'] = raw_df[rep_cols].apply(pd.to_numeric, errors='coerce').fillna(0).sum(axis=1) if rep_cols else 0
        labels = ('Dem Votes', 'Rep Votes', 'Dem %', 'Democrat', 'Republican')
    else:
        raw_df['YES'] = pd.to_numeric(raw_df.get('YES', 0), errors='coerce').fillna(0)
        raw_df['NO'] = pd.to_numeric(raw_df.get('NO', 0), errors='coerce').fillna(0)
        if get_measure_our_side(election_year, selected_race) == "YES":
            raw_df['Unified_Blue'] = raw_df['YES']
            raw_df['Unified_Red'] = raw_df['NO']
            labels = (
                'YES Votes (Our side)' if election_year == "2026 General" else 'YES Votes',
                'NO Votes (Other side)' if election_year == "2026 General" else 'NO Votes',
                'YES %',
                'Yes (Our side)' if election_year == "2026 General" else 'Yes',
                'No (Other side)' if election_year == "2026 General" else 'No',
            )
        else:
            raw_df['Unified_Blue'] = raw_df['NO']
            raw_df['Unified_Red'] = raw_df['YES']
            labels = ('NO Votes (Our side)', 'YES Votes (Other side)', 'NO %', 'No (Our side)', 'Yes (Other side)')

    precinct_col = 'precinct' if 'precinct' in raw_df.columns else 'precinctname' if 'precinctname' in raw_df.columns else 'mapping_precinct_code'
    county_col = 'County' if 'County' in raw_df.columns else 'county' if 'county' in raw_df.columns else None

    agg_dict = {
        'Unified_Blue': 'sum',
        'Unified_Red': 'sum',
        'total_votes': 'sum',
        'geometry': 'first',
        'race': 'first',
    }
    if precinct_col != 'mapping_precinct_code':
        agg_dict[precinct_col] = 'first'
    if county_col:
        agg_dict[county_col] = 'first'

    master_df = raw_df.groupby('mapping_precinct_code').agg(agg_dict).reset_index()
    master_df['precinct_id'] = master_df.index.astype(str)
    master_df['Blue_Percent'] = (master_df['Unified_Blue'] / master_df['total_votes'] * 100).fillna(0).clip(0, 100)
    master_df['Red_Percent'] = (master_df['Unified_Red'] / master_df['total_votes'] * 100).fillna(0).clip(0, 100)
    master_df['Margin_Pts'] = master_df['Blue_Percent'] - master_df['Red_Percent']

    master_df['Margin'] = (
        pd.cut(master_df['Blue_Percent'], bins=BUCKET_BINS, labels=BUCKET_LABELS)
        .cat.add_categories([GRAY_LABEL])
    )
    master_df.loc[master_df['total_votes'] < 5, 'Margin'] = GRAY_LABEL

    return master_df, labels, precinct_col, county_col


def prepare_scatter_comparison(
    county_df: pd.DataFrame,
    election_year: str,
    m_x: str,
    m_y: str,
    precinct_col: str,
    county_col: str | None,
) -> pd.DataFrame:
    def _share(measure_name: str) -> pd.DataFrame:
        sub = county_df[county_df['race'] == measure_name].copy()
        sub['YES'] = pd.to_numeric(sub['YES'], errors='coerce').fillna(0)
        sub['NO'] = pd.to_numeric(sub['NO'], errors='coerce').fillna(0)
        grp_cols = ['mapping_precinct_code', precinct_col] + ([county_col] if county_col else [])
        g = sub.groupby(grp_cols)[['YES', 'NO', 'total_votes']].sum().reset_index()
        g = g[g['total_votes'] >= 5]
        side = get_measure_our_side(election_year, measure_name)
        g['our_pct'] = (g['YES'] if side == "YES" else g['NO']) / (g['YES'] + g['NO']) * 100
        return g

    df_x = _share(m_x).rename(columns={'our_pct': 'X_Pct', 'total_votes': 'Votes_X'})
    df_y = _share(m_y).rename(columns={'our_pct': 'Y_Pct'})
    merged = pd.merge(df_x, df_y[['mapping_precinct_code', 'Y_Pct']], on='mapping_precinct_code')
    if not merged.empty:
        merged['Diff_Pts'] = merged['Y_Pct'] - merged['X_Pct']
        merged['Status'] = np.where(merged['Diff_Pts'] >= 0, f"{m_y} ran ahead", f"{m_y} ran behind")
    return merged