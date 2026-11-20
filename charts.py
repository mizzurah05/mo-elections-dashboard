import math
import pandas as pd
import geopandas as gpd
import plotly.express as px
import streamlit as st
from config import BUCKET_LABELS, GRAY_LABEL, BUCKET_COLORS, VIEWPORTS


def render_choropleth_map(
    gdf: gpd.GeoDataFrame,
    zoom_preset: str,
    precinct_col: str,
    county_col: str | None,
    labels: tuple[str, str, str, str, str],
):
    if gdf.empty:
        st.warning("No mappable precinct polygons found for this selection.")
        return

    blue_lbl, red_lbl, pct_lbl, _, _ = labels

    if zoom_preset in VIEWPORTS:
        center_lat, center_lon, zoom_level = VIEWPORTS[zoom_preset]
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
        color_discrete_map=BUCKET_COLORS,
        category_orders={"Margin": BUCKET_LABELS + [GRAY_LABEL]},
        hover_name=precinct_col,
        hover_data=hover_dict,
        map_style="carto-positron",
        opacity=0.82,
        zoom=zoom_level,
        center={"lat": center_lat, "lon": center_lon},
        labels={
            'Blue_Percent': pct_lbl,
            'Unified_Blue': blue_lbl,
            'Unified_Red': red_lbl,
            'race': 'Race',
            'total_votes': 'Total Votes',
        },
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=680, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def render_precinct_table(
    master_df: pd.DataFrame,
    precinct_col: str,
    county_col: str | None,
    labels: tuple[str, str, str, str, str],
    year_short: str,
    selected_county: str,
    selected_race: str,
):
    blue_lbl, red_lbl, pct_lbl, our_name, other_name = labels
    disp_cols = (
        [county_col, precinct_col, 'total_votes', 'Unified_Blue', 'Unified_Red', 'Blue_Percent', 'Margin_Pts']
        if county_col
        else [precinct_col, 'total_votes', 'Unified_Blue', 'Unified_Red', 'Blue_Percent', 'Margin_Pts']
    )
    table_df = master_df[disp_cols].copy()
    table_df['Margin'] = table_df['Margin_Pts'].apply(
        lambda v: "—" if pd.isna(v) else f"{our_name.split()[0] if v >= 0 else other_name.split()[0]} +{abs(v):.2f}"
    )
    table_df = table_df.drop(columns=['Margin_Pts'])

    rename_map = {
        precinct_col: 'Precinct',
        'total_votes': 'Total Votes',
        'Unified_Blue': blue_lbl,
        'Unified_Red': red_lbl,
        'Blue_Percent': pct_lbl,
    }
    if county_col:
        rename_map[county_col] = 'County'
    table_df = table_df.rename(columns=rename_map)

    sort_by = ['County', 'Precinct'] if 'County' in table_df.columns else ['Precinct']
    table_df = table_df.sort_values(by=sort_by)

    st.download_button(
        label="Download Precinct Table (CSV)",
        data=table_df.to_csv(index=False).encode('utf-8'),
        file_name=f"mo_{year_short}_{selected_county}_{selected_race}.csv".replace(" ", "_").lower(),
        mime="text/csv",
    )

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Total Votes': st.column_config.NumberColumn(format="%d"),
            blue_lbl: st.column_config.NumberColumn(format="%d"),
            red_lbl: st.column_config.NumberColumn(format="%d"),
            pct_lbl: st.column_config.NumberColumn(format="%.2f%%"),
        },
    )


def render_measure_scatter(
    merged_sc: pd.DataFrame,
    m_x: str,
    m_y: str,
    precinct_col: str,
    county_col: str | None,
):
    if merged_sc.empty:
        st.info("Not enough overlapping precincts with 5+ ballots to plot a comparison.")
        return

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
            'X_Pct': f"{m_x} (%)",
            'Y_Pct': f"{m_y} (%)",
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