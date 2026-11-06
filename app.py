import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely import wkt
import plotly.express as px
import math
import numpy as np
import re
import os

# Set up the webpage
st.set_page_config(page_title="MO Elections Master", layout="wide")
st.title("Missouri 2026 Elections Dashboard")

# ==========================================
# 1. Fetch Shapes from Local CSV
# ==========================================
@st.cache_data
def get_shapefile():
    # Checks current folder or processed_data folder
    file_path = "precincts_shape_2026.csv" if os.path.exists("precincts_shape_2026.csv") else "processed_data/precincts_shape_2026.csv"
    
    df = pd.read_csv(file_path)
    
    # Parse the heavy geometry strings once
    df['geometry'] = df['geometry'].apply(lambda x: wkt.loads(x) if pd.notnull(x) else None)
    
    # 🚀 SIMPLIFY POLYGONS: Removes microscopic detail to speed up browser rendering
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
    gdf['geometry'] = gdf['geometry'].simplify(0.001)
    
    # Ensure uppercase for joining later
    gdf['mapping_precinct_code'] = gdf['mapping_precinct_code'].astype(str).str.upper()
    
    return gdf

# ==========================================
# 2. Fetch Election Data from Local CSVs
# ==========================================
@st.cache_data
def get_election_data(table_name):
    # Matches the files downloaded by your download_all_data.py script
    file_path = f"{table_name}.csv" if os.path.exists(f"{table_name}.csv") else f"processed_data/{table_name}.csv"
    
    df = pd.read_csv(file_path)
    
    if not df.empty:
        df['mapping_precinct_code'] = df['mapping_precinct_code'].astype(str).str.upper()
    return df

# ==========================================
# DASHBOARD UI
# ==========================================

dataset_type = st.radio("Select Election Category:", ["Legislative Races", "Ballot Measures"], horizontal=True)
col1, col2, col3 = st.columns([1, 1, 1])

# Determine which CSV to load based on the toggle
table_name = "legislative_races" if dataset_type == "Legislative Races" else "ballot_measures"

# Load the full datasets into memory instantly from cache
with st.spinner("Loading offline CSV data..."):
    full_election_df = get_election_data(table_name)
    shapes_df = get_shapefile()

if full_election_df.empty:
    st.error(f"Error fetching data from {table_name}.csv.")
    st.stop()

# Ensure total_votes is numeric so we can sum it to find "ghost" races
full_election_df['total_votes'] = pd.to_numeric(full_election_df.get('total_votes', 0), errors='coerce').fillna(0)

# ==========================================
# CASCADING DROPDOWNS: County -> Chamber -> Race
# ==========================================

# 1. Select County (Col 1)
county_col = 'County' if 'County' in full_election_df.columns else 'county' if 'county' in full_election_df.columns else None
if county_col:
    county_list = ["ALL"] + sorted(full_election_df[county_col].dropna().unique().tolist())
    with col1:
        selected_county = st.selectbox("Filter by County:", county_list)
else:
    selected_county = "ALL"

# Filter data to the selected county so we can accurately check for votes
if selected_county != "ALL":
    county_df = full_election_df[full_election_df[county_col] == selected_county].copy()
else:
    county_df = full_election_df.copy()

# Strip "Ghost Races": Group by race and only keep races with > 0 total votes in this specific county
race_totals = county_df.groupby('race')['total_votes'].sum()
valid_races = race_totals[race_totals > 0].index.tolist()

def natural_sort_key(s):
    # Extracts numbers so 'District 2' comes before 'District 10'
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]

# 2. Select Chamber (Col 2) & Filter Races
if dataset_type == "Legislative Races":
    with col2:
        chamber = st.selectbox("Select Chamber:", ["State House (HD)", "State Senate (SD)", "Other"])
        
    if chamber == "State House (HD)": 
        chamber_races = [r for r in valid_races if 'REP' in r.upper() or 'HOUSE' in r.upper()]
    elif chamber == "State Senate (SD)": 
        chamber_races = [r for r in valid_races if 'SEN' in r.upper()]
    else: 
        chamber_races = [r for r in valid_races if 'REP' not in r.upper() and 'HOUSE' not in r.upper() and 'SEN' not in r.upper()]
        
    sorted_races = sorted(chamber_races, key=natural_sort_key)
else:
    with col2:
        st.info("Mapping NO votes to Blue and YES votes to Red.")
    sorted_races = sorted(valid_races, key=natural_sort_key)

# 3. Select Race (Col 3)
with col3:
    if not sorted_races:
        st.warning(f"No valid races found for this selection.")
        st.stop()
    dropdown_options = ["ALL"] + sorted_races
    selected_race = st.selectbox("Select Race / Measure:", dropdown_options)

# 🚀 FILTER LOCALLY IN PANDAS 
if selected_race == "ALL":
    election_df = county_df[county_df['race'].isin(sorted_races)].copy()
else:
    election_df = county_df[county_df['race'] == selected_race].copy()

if not election_df.empty:
    
    # 🚀 MERGE IN PANDAS 
    raw_df = pd.merge(election_df, shapes_df, on='mapping_precinct_code', how='left')
            
    # 2. CALCULATE UNIFIED VOTES ON FULL DATASET
    if dataset_type == "Legislative Races":
        dem_cols = [c for c in raw_df.columns if 'DEM' in c.upper()]
        rep_cols = [c for c in raw_df.columns if 'REP' in c.upper()]
        
        raw_df['Unified_Blue'] = raw_df[dem_cols].apply(pd.to_numeric, errors='coerce').fillna(0).sum(axis=1) if dem_cols else 0
        raw_df['Unified_Red'] = raw_df[rep_cols].apply(pd.to_numeric, errors='coerce').fillna(0).sum(axis=1) if rep_cols else 0
        
        blue_label, red_label = 'Dem Votes', 'Rep Votes'
        pct_label = 'Dem %'
        bucket_labels = ['< 30% Dem', '30-40% Dem', '40-50% Dem', '50-60% Dem', '60-70% Dem', '> 70% Dem']
        
    else: 
        raw_df['YES'] = pd.to_numeric(raw_df.get('YES', 0), errors='coerce').fillna(0)
        raw_df['NO'] = pd.to_numeric(raw_df.get('NO', 0), errors='coerce').fillna(0)
        
        raw_df['Unified_Blue'] = raw_df['NO']  
        raw_df['Unified_Red'] = raw_df['YES']  
        
        blue_label, red_label = 'NO Votes', 'YES Votes'
        pct_label = 'NO %'
        bucket_labels = ['< 30% NO', '30-40% NO', '40-50% NO', '50-60% NO', '60-70% NO', '> 70% NO']

    # 3. AGGREGATE SPLIT PRECINCTS
    agg_dict = {
        'Unified_Blue': 'sum',
        'Unified_Red': 'sum',
        'total_votes': 'sum',
        'geometry': 'first'
    }
    
    precinct_col = 'precinct' if 'precinct' in raw_df.columns else 'precinctname' if 'precinctname' in raw_df.columns else 'mapping_precinct_code'
    agg_dict[precinct_col] = 'first'
    
    if county_col: agg_dict[county_col] = 'first'
    if 'race' in raw_df.columns: agg_dict['race'] = 'first'
    
    master_df = raw_df.groupby('mapping_precinct_code').agg(agg_dict).reset_index()
    master_df['precinct_id'] = master_df.index.astype(str)
    
    # 4. SHARED PERCENTAGE CALCULATION
    master_df['Blue_Percent'] = (master_df['Unified_Blue'] / master_df['total_votes'] * 100).fillna(0).clip(0, 100) 
    
    bins = [-1, 30, 40, 50, 60, 70, 101]
    master_df['Margin'] = pd.cut(master_df['Blue_Percent'], bins=bins, labels=bucket_labels)
    
    gray_label = '< 5 Votes (Gray)'
    master_df['Margin'] = master_df['Margin'].cat.add_categories([gray_label])
    master_df.loc[master_df['total_votes'] < 5, 'Margin'] = gray_label
    bucket_labels.append(gray_label)

    # =========================================================
    # 📊 SIDEBAR REGION SUMMARY
    # =========================================================
    st.sidebar.title("📊 Region Summary")
    st.sidebar.markdown(f"**Region:** {selected_county}")
    st.sidebar.markdown(f"**Race:** {selected_race}")
    st.sidebar.divider()
    
    total_region_votes = int(master_df['total_votes'].sum())
    total_region_blue = int(master_df['Unified_Blue'].sum())
    total_region_red = int(master_df['Unified_Red'].sum())
    
    if total_region_votes > 0:
        pct_region_blue = (total_region_blue / total_region_votes) * 100
        pct_region_red = (total_region_red / total_region_votes) * 100
    else:
        pct_region_blue, pct_region_red = 0, 0

    st.sidebar.metric("Total Votes Cast", f"{total_region_votes:,}")
    
    st.sidebar.markdown(
        f"""
        <div style="padding:10px; border-radius:5px; background-color:#f0f2f6; margin-bottom:10px;">
            <h4 style="margin:0; color:#2166ac;">🟦 {blue_label}</h4>
            <h2 style="margin:0; color:#2166ac;">{total_region_blue:,} <span style="font-size:16px;">({pct_region_blue:.1f}%)</span></h2>
        </div>
        <div style="padding:10px; border-radius:5px; background-color:#f0f2f6;">
            <h4 style="margin:0; color:#b2182b;">🟥 {red_label}</h4>
            <h2 style="margin:0; color:#b2182b;">{total_region_red:,} <span style="font-size:16px;">({pct_region_red:.1f}%)</span></h2>
        </div>
        """, unsafe_allow_html=True
    )

    # 5. SPLIT MAPPED VS UNMAPPED
    absentee_df = master_df[master_df['geometry'].isna()].copy()
    gdf = master_df.dropna(subset=['geometry']).copy()
    gdf = gpd.GeoDataFrame(gdf, geometry='geometry', crs="EPSG:4326")

    # 6. SHOW ABSENTEE KPI WITH SPLITS
    if not absentee_df.empty:
        tot_abs = int(absentee_df['total_votes'].sum())
        tot_blue = int(absentee_df['Unified_Blue'].sum())
        tot_red = int(absentee_df['Unified_Red'].sum())
        
        if tot_abs > 0:
            blue_pct = (tot_blue / tot_abs) * 100
            red_pct = (tot_red / tot_abs) * 100
            st.warning(
                f"📩 **Unmapped / Absentee Votes:** {tot_abs:,} Total Votes &nbsp;|&nbsp; "
                f"**{tot_blue:,}** {blue_label} ({blue_pct:.1f}%) &nbsp;|&nbsp; "
                f"**{tot_red:,}** {red_label} ({red_pct:.1f}%)"
            )

    # 7. RENDER MAP
    bucket_colors = {
        bucket_labels[0]: '#b2182b',
        bucket_labels[1]: '#d6604d',
        bucket_labels[2]: '#f4a582',
        bucket_labels[3]: '#92c5de',
        bucket_labels[4]: '#4393c3',
        bucket_labels[5]: '#2166ac',
        gray_label: '#d3d3d3'
    }

    if not gdf.empty:
        bounds = gdf.total_bounds  
        center_lon = (bounds[0] + bounds[2]) / 2
        center_lat = (bounds[1] + bounds[3]) / 2
        max_span = max(bounds[2] - bounds[0], bounds[3] - bounds[1])
        zoom_level = max(5.0, math.log2(360 / max_span) - 1.2) if max_span > 0 else 8.0

        hover_dict = {
            precinct_col: False, 
            'race': True,
            'total_votes': True,
            'Unified_Blue': True,
            'Unified_Red': True,
            'Blue_Percent': ':.1f'
        }
        if county_col: hover_dict[county_col] = True

        fig = px.choropleth_map(
            gdf,
            geojson=gdf.geometry,
            locations='precinct_id',  
            color='Margin',                            
            color_discrete_map=bucket_colors,          
            category_orders={"Margin": bucket_labels}, 
            hover_name=precinct_col,                                         
            hover_data=hover_dict,          
            map_style="carto-positron",                                
            opacity=0.8,
            zoom=zoom_level,                           
            center={"lat": center_lat, "lon": center_lon},
            labels={
                'Blue_Percent': pct_label,
                'Unified_Blue': blue_label,
                'Unified_Red': red_label,
                'race': 'Race',
                'total_votes': 'Total Votes'
            }
        )
        
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=1200)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No mappable precincts found for this county selection.")

    # 8. RENDER DATA TABLE BELOW MAP
    st.markdown("### 📊 Precinct Level Results")
    
    table_df = master_df[[precinct_col, 'total_votes', 'Unified_Blue', 'Unified_Red', 'Blue_Percent']].copy()
    table_df = table_df.rename(columns={
        precinct_col: 'Precinct',
        'total_votes': 'Total Votes',
        'Unified_Blue': blue_label,
        'Unified_Red': red_label,
        'Blue_Percent': pct_label
    })
    
    table_df = table_df.sort_values(by='Precinct')
    table_df[pct_label] = table_df[pct_label].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(table_df, use_container_width=True, hide_index=True)

else:
    st.warning("No data found for this selection.")