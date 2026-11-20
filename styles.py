import streamlit as st
from config import BUCKET_LABELS, BUCKET_COLORS

TEAM_MO_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700;800&display=swap');

:root {
    --brand-navy: #10243e;
    --brand-blue: #1e4e8c;
    --brand-red: #c82427;
    --yes-3: #2e7d47;
    --yes-4: #1f6336;
    --no-3: #b8442a;
    --no-4: #8f2d18;
}

html, body, [class*="css"] {
    font-family: 'Figtree', -apple-system, BlinkMacSystemFont, sans-serif;
}

.block-container {
    max-width: 1280px;
}

/* Top Navy Masthead */
.team-mo-banner {
    background-color: var(--brand-navy);
    color: #ffffff;
    padding: 1.1rem 1.5rem;
    border-radius: 8px;
    border-bottom: 3px solid var(--brand-red);
    margin-bottom: 1rem;
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

/* High-Contrast Selector Pills (Light & Dark Mode Safe) */
div[data-testid="stRadio"] > label {
    font-size: 0.72rem !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
    opacity: 0.85;
}
div[data-testid="stRadio"] div[role="radiogroup"] {
    background-color: rgba(30, 78, 140, 0.10);
    border: 1px solid rgba(148, 163, 184, 0.45);
    border-radius: 8px;
    padding: 0.4rem 0.85rem;
    gap: 1.25rem;
}
div[data-testid="stRadio"] div[role="radiogroup"] label p {
    font-size: 0.96rem !important;
    font-weight: 700 !important;
}

/* Editorial Headers & Dividers */
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

/* Measure & KPI Scorecards */
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
.status-badge-win, .status-badge-loss {
    color: #ffffff;
    font-size: 0.66rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    padding: 0.2rem 0.5rem;
    border-radius: 3px;
    white-space: nowrap;
}
.status-badge-win { background-color: var(--yes-4); }
.status-badge-loss { background-color: var(--no-4); }

.split-bar-wrap {
    display: flex;
    height: 11px;
    border-radius: 3px;
    overflow: hidden;
    background-color: rgba(148, 163, 184, 0.25);
    margin: 0.55rem 0;
}
.split-bar-our { background-color: var(--yes-3); height: 100%; }
.split-bar-other { background-color: var(--no-3); border-left: 2px solid #ffffff; height: 100%; }
.split-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.74rem;
    opacity: 0.82;
    margin-bottom: 0.5rem;
    font-variant-numeric: tabular-nums;
}
.scorecard-margin { font-size: 0.85rem; font-variant-numeric: tabular-nums; }
.scorecard-foot { font-size: 0.78rem; opacity: 0.72; margin-top: 0.2rem; }
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
"""


def inject_styles():
    st.markdown(TEAM_MO_CSS, unsafe_allow_html=True)


def render_masthead(year_short: str, date_str: str, county_count: int):
    st.markdown(f"""
    <div class="team-mo-banner">
        <div>
            <span class="brand-title">Team MO</span>
            <span class="brand-sub">Missouri {year_short} Precinct Election Results</span>
        </div>
        <div class="brand-meta">General Election · {date_str} · {county_count} Jurisdictions Loaded</div>
    </div>
    """, unsafe_allow_html=True)


def render_hero_header(date_str: str, title: str, subtitle: str | None = None):
    sub_html = (
        f'<div style="margin-bottom: 1.1rem;"><span class="badge-pill">Precinct Results</span>'
        f'<span style="font-size: 0.78rem; opacity: 0.72;">{subtitle}</span></div>'
        if subtitle else ""
    )
    st.markdown(f"""
    <div class="kicker">Missouri · {date_str}</div>
    <h1 class="hero-title">{title}</h1>
    {sub_html}
    """, unsafe_allow_html=True)


def render_section_divider(title: str, subtitle: str):
    st.markdown(f"""
    <div class="section-divider">
        <h2>{title}</h2>
        <span>{subtitle}</span>
    </div>
    """, unsafe_allow_html=True)


def render_measure_scorecard(
    title: str,
    subtitle: str,
    badge_text: str,
    is_win: bool,
    our_label: str,
    other_label: str,
    our_v: int,
    other_v: int,
    our_pct: float,
    other_pct: float,
    lead_side: str,
    diff_pts: float,
    foot_text: str,
):
    badge_cls = "status-badge-win" if is_win else "status-badge-loss"
    st.markdown(f"""
    <div class="scorecard">
        <div class="scorecard-top">
            <div>
                <div class="scorecard-title">{title}</div>
                <div class="scorecard-sub">{subtitle}</div>
            </div>
            <span class="{badge_cls}">{badge_text}</span>
        </div>
        <div class="split-bar-wrap">
            <div class="split-bar-our" style="width: {our_pct:.2f}%;"></div>
            <div class="split-bar-other" style="width: {other_pct:.2f}%;"></div>
        </div>
        <div class="split-labels">
            <span>{our_label} {our_pct:.2f}% ({our_v:,})</span>
            <span>{other_label} {other_pct:.2f}% ({other_v:,})</span>
        </div>
        <div class="scorecard-margin">
            <span style="opacity:0.72;">Margin: </span>
            <b>{lead_side} +{abs(diff_pts):.2f} pts</b>
            <span style="opacity:0.72;"> ({abs(our_v - other_v):,} votes)</span>
        </div>
        <div class="scorecard-foot">{foot_text}</div>
    </div>
    """, unsafe_allow_html=True)


def render_region_summary_panel(
    kicker: str,
    title: str,
    our_name: str,
    other_name: str,
    tot_v: int,
    tot_b: int,
    tot_r: int,
    pct_b: float,
    pct_r: float,
    won_p: int,
    tot_p: int,
    absentee_df,
    unmapped_note: str,
):
    spread = pct_b - pct_r
    win_side = our_name if spread >= 0 else other_name
    win_cls = "status-badge-win" if spread >= 0 else "status-badge-loss"

    st.markdown(f"""
    <div class="scorecard" style="height: auto; margin-bottom: 1rem;">
        <div class="scorecard-top">
            <div>
                <div class="kicker" style="margin-bottom:0;">{kicker}</div>
                <div class="scorecard-title" style="font-size:1.15rem;">{title}</div>
            </div>
            <span class="{win_cls}">{win_side} +{abs(spread):.2f} pts</span>
        </div>
        <div class="split-bar-wrap">
            <div class="split-bar-our" style="width: {pct_b:.2f}%;"></div>
            <div class="split-bar-other" style="width: {pct_r:.2f}%;"></div>
        </div>
        <div class="split-labels">
            <span><b>{our_name}:</b> {pct_b:.2f}% ({tot_b:,})</span>
            <span><b>{other_name}:</b> {pct_r:.2f}% ({tot_r:,})</span>
        </div>
        <div class="scorecard-foot">
            <b>{tot_v:,}</b> total ballots · {our_name} ahead in <b>{won_p} of {tot_p}</b> reporting units
        </div>
    </div>
    """, unsafe_allow_html=True)

    swatches = "".join(f'<span style="height:10px; background:{BUCKET_COLORS[b]};"></span>' for b in BUCKET_LABELS)
    st.markdown(f"""
    <div style="margin-bottom: 1rem;">
        <div style="display:flex; justify-content:space-between; font-size:0.75rem; opacity:0.75; margin-bottom:4px;">
            <span>← {other_name} ahead</span>
            <span>{our_name} ahead →</span>
        </div>
        <div style="display:grid; grid-template-columns: repeat(14, 1fr); gap:2px;">{swatches}</div>
        <div style="display:flex; justify-content:space-between; font-size:0.68rem; opacity:0.68; margin-top:3px; font-variant-numeric: tabular-nums;">
            <span>&lt;20%</span>
            <span>35%</span>
            <span>50%</span>
            <span>65%</span>
            <span>&gt;80%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not absentee_df.empty and int(absentee_df['total_votes'].sum()) > 0:
        a_v = int(absentee_df['total_votes'].sum())
        a_b = int(absentee_df['Unified_Blue'].sum())
        a_r = int(absentee_df['Unified_Red'].sum())
        st.markdown(f"""
        <div class="absentee-banner">
            <b>{unmapped_note}</b><br>
            {a_v:,} ballots · <b>{a_b:,}</b> {our_name} ({a_b / a_v * 100:.1f}%) · <b>{a_r:,}</b> {other_name} ({a_r / a_v * 100:.1f}%)
        </div>
        """, unsafe_allow_html=True)

    st.caption("Hover over any precinct polygon on the map for exact vote counts and shares. Use the table below to sort or download CSV results.")


def render_footer():
    st.markdown("""
    <div style="margin-top: 2.5rem; border-top: 1px solid rgba(148, 163, 184, 0.35); padding-top: 0.85rem; font-size: 0.76rem; opacity: 0.72;">
        Compiled by <b>Team MO</b> · Precinct outlines from US Census Bureau (TIGER/Line) &amp; county election authorities.
    </div>
    """, unsafe_allow_html=True)