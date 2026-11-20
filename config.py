ELECTION_CYCLES = {
    "2026 General": {
        "year_short": "2026",
        "date_str": "November 3, 2026",
        "races_table": "legislative_races",
        "ballot_table": "ballot_measures",
        "shapes_table": "precincts_shape_2026",
        "race_section_label": "State Legislature",
        "race_hero_title": "State Legislature Precinct Results",
        "race_hero_sub": "Missouri House &amp; Even-Numbered State Senate Districts",
        "ballot_note": "Our side = NO on Amendment 3 &amp; Prop A · YES on Amendment 6",
        "chambers": ["State House (HD)", "State Senate (SD)", "All Legislative"],
        "is_team_mo_framed": True,
        "unmapped_note": "Absentee / Central Count (Unmapped Polygons):",
    },
    "2022 General": {
        "year_short": "2022",
        "date_str": "November 8, 2022",
        "races_table": "electoral_results_2022",
        "ballot_table": "ballot_measures_2022",
        "shapes_table": "precincts_shape_2026",
        "race_section_label": "Electoral Results",
        "race_hero_title": "2022 General Election Precinct Results",
        "race_hero_sub": "U.S. Senate, State Auditor, U.S. House, State Senate &amp; State House",
        "ballot_note": "Statewide General Election Ballot Questions · Green = Yes · Terracotta = No",
        "chambers": ["Federal & Statewide", "State Senate (SD)", "State House (HD)", "All Races"],
        "is_team_mo_framed": False,
        "unmapped_note": "Absentee / Unmapped Polygons (incl. STL City 2022 28-Ward Precincts):",
    },
}

MEASURE_META_BY_YEAR = {
    "2026 General": {
        "AMENDMENT 3": {
            "title": "Amendment 3",
            "subtitle": "Stop the Ban",
            "our_side": "NO",
            "other_side": "YES",
        },
        "AMENDMENT 6": {
            "title": "Amendment 6",
            "subtitle": "Respect Missouri Voters",
            "our_side": "YES",
            "other_side": "NO",
        },
        "PROPOSITION A": {
            "title": "Proposition A",
            "subtitle": "People Not Politicians",
            "our_side": "NO",
            "other_side": "YES",
        },
    },
    "2022 General": {
        "AMENDMENT 3": {
            "title": "Amendment 3",
            "subtitle": "Legal Marijuana Initiative",
            "our_side": "YES",
            "other_side": "NO",
        },
        "AMENDMENT 4": {
            "title": "Amendment 4",
            "subtitle": "KC Police Funding Mandate",
            "our_side": "YES",
            "other_side": "NO",
        },
        "CONVENTION QUESTION": {
            "title": "Convention Question",
            "subtitle": "Constitutional Convention",
            "our_side": "YES",
            "other_side": "NO",
        },
    },
}

BUCKET_BINS = [-1, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 101]

BUCKET_LABELS = [
    '< 20%', '20–25%', '25–30%', '30–35%', '35–40%',
    '40–45%', '45–50%', '50–55%', '55–60%', '60–65%',
    '65–70%', '70–75%', '75–80%', '> 80%'
]

GRAY_LABEL = '< 5 Votes (Gray)'

BUCKET_COLORS = {
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
    GRAY_LABEL: '#475569',
}

VIEWPORTS = {
    "St. Louis Metro": (38.63, -90.28, 9.6),
    "Kansas City Metro": (39.05, -94.45, 9.4),
    "Springfield / SW MO": (37.18, -93.29, 9.4),
}