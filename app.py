import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from bs4 import BeautifulSoup
import io
import html as html_lib

# ══════════════════════════════════════════════════════════════════════════════
# Page Config
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Connection Accelerator Analysis",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
# Minimal Streamlit overrides (only things st.markdown CAN handle)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Force light mode everywhere */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"],
.main, .stApp, [data-testid="stAppViewBlockContainer"] {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
}

/* Hide default Streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}
div[data-testid="stToolbar"] {display: none;}
div[data-testid="stDecoration"] {display: none;}
.viewerBadge_container__r5tak {display: none;}

/* Force all iframes to have white background */
iframe {
    background: #FFFFFF !important;
}

.main .block-container {
    padding-top: 0 !important;
    padding-bottom: 1rem;
    max-width: 1400px;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #F8F9FC;
    border-radius: 12px;
    padding: 5px;
    border: 1px solid #E2E8F0;
}
.stTabs [data-baseweb="tab"] {
    padding: 10px 24px;
    border-radius: 9px;
    font-size: 0.88rem;
    font-weight: 500;
    color: #64748B;
    background: none;
    border: none;
}
.stTabs [aria-selected="true"] {
    background: #FFFFFF !important;
    color: #4F4CF3 !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.stTabs [data-baseweb="tab-highlight"] { display: none; }
.stTabs [data-baseweb="tab-border"] { display: none; }

/* Download buttons */
.stDownloadButton > button {
    width: 100%;
    border-radius: 10px;
    font-weight: 600;
}

/* Fix ALL buttons to be visible on white background */
button[kind="secondary"],
.stButton > button[kind="secondary"],
.stDownloadButton > button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #E2E8F0 !important;
}
button[kind="secondary"]:hover,
.stButton > button[kind="secondary"]:hover,
.stDownloadButton > button[kind="secondary"]:hover {
    background-color: #F8F9FC !important;
    border-color: #4F4CF3 !important;
    color: #4F4CF3 !important;
}

button[kind="primary"],
.stButton > button[kind="primary"],
.stDownloadButton > button[kind="primary"] {
    background: linear-gradient(135deg, #021c6b, #4F4CF3) !important;
    color: #FFFFFF !important;
    border: none !important;
}

/* Force all text to be dark on white */
.stSelectbox label, .stTextInput label {
    color: #0F172A !important;
}
p, span, label, div {
    color: #0F172A;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Shared CSS for all st.components.v1.html() blocks
# ══════════════════════════════════════════════════════════════════════════════
SHARED_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: #FFFFFF !important;
    color: #0F172A !important;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
}
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.73rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    white-space: nowrap;
}
.badge-in       { background: #DBEAFE; color: #1E40AF; }
.badge-out      { background: #FFF1F2; color: #9F1239; }
.badge-active   { background: #D1FAE5; color: #065F46; }
.badge-instant  { background: #C7D2FE; color: #3730A3; }
.badge-dev      { background: #FEF3C7; color: #92400E; }
.badge-inactive { background: #FEE2E2; color: #991B1B; }
.badge-new      { background: #FCE7F3; color: #9D174D; }
.badge-unknown  { background: #F1F5F9; color: #64748B; }
"""


# ══════════════════════════════════════════════════════════════════════════════
# SVG Path → Status mapping
# ══════════════════════════════════════════════════════════════════════════════
STATUS_MAP = [
    ('M9 16.17',   'Active Connection'),
    ('M9 16',      'Active Connection'),
    ('M17.3 6.3',  'Inactive Connection'),
    ('M11 15h2v2', 'New Integration Required'),
    ('M11 7h2v2',  'In Development Connection'),
    ('M12 2C6.48', 'Instant Live Connection'),
]

def detect_status(paths):
    for d in paths:
        for prefix, status in STATUS_MAP:
            if d.startswith(prefix):
                return status
    return 'Unknown'

def status_badge_class(s):
    if 'Instant' in s:     return 'badge-instant'
    if 'Active' in s:      return 'badge-active'
    if 'Development' in s: return 'badge-dev'
    if 'Inactive' in s:    return 'badge-inactive'
    if 'New' in s:         return 'badge-new'
    return 'badge-unknown'

def network_badge_class(n):
    return 'badge-in' if n == 'In-network' else 'badge-out'

def esc(s):
    return html_lib.escape(str(s)) if s else ''


# ══════════════════════════════════════════════════════════════════════════════
# Parse HTML file
# ══════════════════════════════════════════════════════════════════════════════
def parse_html(html_content, source_name):
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    carriers = []
    for ti, table in enumerate(tables):
        network = 'In-network' if ti == 0 else 'Out-of-network'
        rows = table.find_all('tr')
        for ri, row in enumerate(rows):
            if ri == 0:
                continue
            cells = row.find_all('td')
            if len(cells) < 3:
                continue
            name = cells[1].get_text(strip=True)
            if not name:
                continue
            func_text = cells[2].get_text(strip=True)
            paths = []
            for svg in cells[2].find_all('svg'):
                for path in svg.find_all('path'):
                    d = path.get('d', '')
                    if d:
                        paths.append(d)
            carriers.append({
                'Carrier Name': name,
                'P44 Network': network,
                'Connection Status': detect_status(paths),
                'Function': func_text,
                'Source File': source_name,
            })
    return carriers


# ══════════════════════════════════════════════════════════════════════════════
# Generate reports
# ══════════════════════════════════════════════════════════════════════════════
def generate_html_report(df):
    in_n = len(df[df['P44 Network'] == 'In-network'])
    rows_html = ""
    for i, (_, c) in enumerate(df.iterrows()):
        rows_html += f"<tr><td>{i+1}</td><td>{esc(c['Carrier Name'])}</td><td>{esc(c['P44 Network'])}</td><td>{esc(c['Connection Status'])}</td><td>{esc(c['Function'])}</td></tr>"
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Connection Accelerator Report</title>
<style>*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:'Segoe UI',sans-serif;background:#fff;color:#1E293B;padding:2rem 3rem}}
h1{{color:#021c6b;font-size:1.6rem;border-bottom:3px solid #4F4CF3;padding-bottom:.5rem;margin-bottom:.5rem}}
.meta{{color:#64748B;font-size:.9rem;margin-bottom:2rem}}h2{{color:#4F4CF3;font-size:1.15rem;margin:2rem 0 .75rem}}
table{{border-collapse:collapse;width:100%;margin-bottom:1.5rem}}th{{background:#021c6b;color:#fff;padding:10px 14px;text-align:left;font-size:.82rem;text-transform:uppercase}}
td{{padding:8px 14px;border-bottom:1px solid #F1F5F9;font-size:.88rem}}tr:hover{{background:#F8FAFC}}</style></head><body>
<h1>🔗 Connection Accelerator Report</h1>
<p class="meta">{len(df)} carriers | In-network: {in_n} | Out-of-network: {len(df)-in_n}</p>
<h2>Carrier List</h2><table><thead><tr><th>#</th><th>Carrier Name</th><th>P44 Network</th><th>Connection Status</th><th>Function</th></tr></thead><tbody>{rows_html}</tbody></table></body></html>"""


def generate_excel_report(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        carrier_df = df.copy()
        carrier_df.insert(0, '#', range(1, len(carrier_df) + 1))
        carrier_df.to_excel(writer, sheet_name='Carrier List', index=False)

        pivot_counts = df['Connection Status'].value_counts().reset_index()
        pivot_counts.columns = ['Connection Status', 'Carrier Count']
        pivot_counts = pivot_counts.sort_values('Carrier Count', ascending=False)
        total_row = pd.DataFrame([{'Connection Status': 'Total', 'Carrier Count': len(df)}])
        pivot_df = pd.concat([pivot_counts, total_row], ignore_index=True)
        pivot_df.to_excel(writer, sheet_name='Status Pivot', index=False)

        cross = pd.crosstab(df['Connection Status'], df['P44 Network'], margins=True, margins_name='Total')
        cols = [c for c in ['In-network', 'Out-of-network', 'Total'] if c in cross.columns]
        cross = cross[cols]
        cross.index.name = 'Connection Status'
        cross.to_excel(writer, sheet_name='Network × Status')
    output.seek(0)
    return output


# ══════════════════════════════════════════════════════════════════════════════
# Render components using st.components.v1.html (preserves ALL CSS)
# ══════════════════════════════════════════════════════════════════════════════
def render_topbar(n_files, total):
    components.html(f"""
    <html><head><style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: #FFFFFF !important; }}
    .topbar {{
        background: #021c6b;
        padding: 0 2.5rem;
        height: 56px;
        display: flex;
        align-items: center;
        gap: 14px;
        border-radius: 0;
        font-family: 'Inter', sans-serif;
    }}
    .topbar-logo {{
        width: 32px; height: 32px;
        background: linear-gradient(135deg, #4F4CF3, #0072ec);
        border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.95rem;
    }}
    .topbar-title {{ color: #fff; font-weight: 600; font-size: 0.95rem; flex: 1; }}
    .topbar-files {{ color: rgba(255,255,255,0.5); font-size: 0.8rem; }}
    </style></head><body>
    <div class="topbar">
        <div class="topbar-logo">🔗</div>
        <div class="topbar-title">Connection Accelerator Analysis</div>
        <div class="topbar-files">{n_files} file(s) · {total} carriers</div>
    </div>
    </body></html>
    """, height=58)


def render_kpis(total, in_network, out_network):
    components.html(f"""
    <html><head><style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: #FFFFFF !important; font-family: 'Inter', sans-serif; }}
    .kpis {{ display: flex; gap: 20px; padding: 4px; }}
    .kpi {{
        flex: 1;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.5rem 1.8rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        transition: box-shadow 0.2s;
    }}
    .kpi:hover {{ box-shadow: 0 6px 20px rgba(0,0,0,0.07); }}
    .kpi::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
    }}
    .kpi-total::before  {{ background: linear-gradient(90deg, #021c6b, #4F4CF3); }}
    .kpi-in::before     {{ background: linear-gradient(90deg, #059669, #34D399); }}
    .kpi-out::before    {{ background: linear-gradient(90deg, #DC2626, #FB923C); }}
    .kpi-value {{
        font-size: 2.8rem;
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -0.03em;
    }}
    .kpi-total .kpi-value  {{ color: #021c6b; }}
    .kpi-in .kpi-value     {{ color: #059669; }}
    .kpi-out .kpi-value    {{ color: #DC2626; }}
    .kpi-label {{
        font-size: 0.78rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 6px;
    }}
    .kpi-icon {{
        position: absolute;
        top: 1.2rem; right: 1.5rem;
        font-size: 1.8rem;
        opacity: 0.15;
    }}
    </style></head><body>
    <div class="kpis">
        <div class="kpi kpi-total">
            <div class="kpi-value">{total}</div>
            <div class="kpi-label">Total Carriers</div>
            <div class="kpi-icon">📦</div>
        </div>
        <div class="kpi kpi-in">
            <div class="kpi-value">{in_network}</div>
            <div class="kpi-label">In-Network</div>
            <div class="kpi-icon">✅</div>
        </div>
        <div class="kpi kpi-out">
            <div class="kpi-value">{out_network}</div>
            <div class="kpi-label">Out-of-Network</div>
            <div class="kpi-icon">⚠️</div>
        </div>
    </div>
    </body></html>
    """, height=140)


def render_legend():
    components.html(f"""
    <html><head><style>
    {SHARED_CSS}
    .legend {{
        display: flex; gap: 12px; flex-wrap: wrap;
        padding: 10px 16px;
        background: #F8F9FC;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
    }}
    </style></head><body>
    <div class="legend">
        <span class="badge badge-instant">Instant Live</span>
        <span class="badge badge-active">Active</span>
        <span class="badge badge-dev">In Development</span>
        <span class="badge badge-inactive">Inactive</span>
        <span class="badge badge-new">New Integration Required</span>
    </div>
    </body></html>
    """, height=52)


def render_carrier_table_component(df, total):
    if df.empty:
        components.html("""<html><body><p style="color:#64748B;padding:2.5rem;text-align:center;font-family:Inter,sans-serif;">
        No carriers match the current filters.</p></body></html>""", height=80)
        return

    rows = ""
    for i, (_, c) in enumerate(df.iterrows()):
        net_cls = network_badge_class(c['P44 Network'])
        stat_cls = status_badge_class(c['Connection Status'])
        rows += f"""<tr>
            <td>{i+1}</td>
            <td style="font-weight:500;">{esc(c['Carrier Name'])}</td>
            <td><span class="badge {net_cls}">{esc(c['P44 Network'])}</span></td>
            <td><span class="badge {stat_cls}">{esc(c['Connection Status'])}</span></td>
            <td>{esc(c['Function'])}</td>
        </tr>"""

    # Calculate height: header(46) + rows(45 each) + caption(30) + padding(20), max 800
    height = min(46 + len(df) * 45 + 50, 800)

    components.html(f"""
    <html><head><style>
    {SHARED_CSS}
    .table-wrap {{ overflow-x: auto; overflow-y: auto; max-height: 700px; }}
    table.data-table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0;
        font-size: 0.88rem;
    }}
    table.data-table thead th {{
        background: #021c6b;
        color: #fff;
        padding: 13px 18px;
        text-align: left;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        white-space: nowrap;
        position: sticky;
        top: 0;
        z-index: 1;
    }}
    table.data-table tbody td {{
        padding: 12px 18px;
        border-bottom: 1px solid #F1F5F9;
        color: #0F172A;
    }}
    table.data-table tbody tr:hover {{ background: #FAFBFF; }}
    table.data-table tbody tr:last-child td {{ border-bottom: none; }}
    .table-caption {{
        font-size: 0.8rem;
        color: #64748B;
        margin-top: 0.75rem;
    }}
    </style></head><body>
    <div class="table-wrap">
    <table class="data-table"><thead><tr>
        <th>#</th><th>Carrier Name</th><th>P44 Network</th><th>Connection Status</th><th>Function</th>
    </tr></thead><tbody>{rows}</tbody></table>
    </div>
    <div class="table-caption">Showing {len(df)} of {total} carriers</div>
    </body></html>
    """, height=height, scrolling=True)


def render_pivot_component(df):
    counts = df['Connection Status'].value_counts().sort_values(ascending=False)
    total_count = counts.sum()
    rows = ""
    for status, count in counts.items():
        rows += f"<tr><td>{esc(status)}</td><td>{count}</td></tr>"
    rows += f'<tr class="total-row"><td>Total</td><td>{total_count}</td></tr>'

    height = 46 + (len(counts) + 1) * 42 + 20

    components.html(f"""
    <html><head><style>
    {SHARED_CSS}
    .section-title {{
        font-size: 1.05rem; font-weight: 700; color: #0F172A;
        margin: 0.5rem 0 1rem 0; display: flex; align-items: center; gap: 10px;
    }}
    .section-title .dot {{ width: 8px; height: 8px; background: #4F4CF3; border-radius: 50%; }}
    .sub {{ color: #64748B; font-size: 0.88rem; margin-bottom: 1rem; }}
    table.pivot-table {{
        border-collapse: separate; border-spacing: 0; border-radius: 14px;
        overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0; font-size: 0.88rem; min-width: 350px;
    }}
    table.pivot-table thead th {{
        background: #021c6b; color: #fff; padding: 13px 22px;
        text-align: center; font-size: 0.78rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.05em;
    }}
    table.pivot-table thead th:first-child {{ text-align: left; }}
    table.pivot-table tbody td {{
        padding: 11px 22px; border-bottom: 1px solid #F1F5F9;
        text-align: center; color: #0F172A;
    }}
    table.pivot-table tbody td:first-child {{ text-align: left; font-weight: 600; color: #4F4CF3; }}
    table.pivot-table tbody tr:hover {{ background: #FAFBFF; }}
    table.pivot-table tr.total-row td {{
        font-weight: 700; background: #EEF2FF;
        border-top: 2px solid #4F4CF3; color: #021c6b;
    }}
    </style></head><body>
    <div class="section-title"><span class="dot"></span> Connection Status Pivot</div>
    <p class="sub">Carrier count by Connection Status</p>
    <table class="pivot-table"><thead><tr><th>Connection Status</th><th>Carrier Count</th></tr></thead>
    <tbody>{rows}</tbody></table>
    </body></html>
    """, height=height)


def render_crosstab_component(df):
    statuses = sorted(df['Connection Status'].unique())
    nets = ['In-network', 'Out-of-network']
    header = "<th>Connection Status</th>" + "".join(f"<th>{esc(n)}</th>" for n in nets) + "<th>Total</th>"
    rows = ""
    col_totals = {n: 0 for n in nets}
    grand_total = 0
    for s in statuses:
        row_total = 0
        cells = f"<td>{esc(s)}</td>"
        for n in nets:
            v = len(df[(df['Connection Status'] == s) & (df['P44 Network'] == n)])
            cells += f"<td>{v}</td>"
            row_total += v
            col_totals[n] += v
        grand_total += row_total
        cells += f"<td>{row_total}</td>"
        rows += f"<tr>{cells}</tr>"
    total_cells = "<td>Total</td>" + "".join(f"<td>{col_totals[n]}</td>" for n in nets) + f"<td>{grand_total}</td>"
    rows += f'<tr class="total-row">{total_cells}</tr>'

    height = 46 + (len(statuses) + 1) * 42 + 80

    components.html(f"""
    <html><head><style>
    {SHARED_CSS}
    .section-title {{
        font-size: 1.05rem; font-weight: 700; color: #0F172A;
        margin: 1.5rem 0 1rem 0; display: flex; align-items: center; gap: 10px;
    }}
    .section-title .dot {{ width: 8px; height: 8px; background: #4F4CF3; border-radius: 50%; }}
    .sub {{ color: #64748B; font-size: 0.88rem; margin-bottom: 1rem; }}
    table.pivot-table {{
        border-collapse: separate; border-spacing: 0; border-radius: 14px;
        overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0; font-size: 0.88rem; min-width: 350px;
    }}
    table.pivot-table thead th {{
        background: #021c6b; color: #fff; padding: 13px 22px;
        text-align: center; font-size: 0.78rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.05em;
    }}
    table.pivot-table thead th:first-child {{ text-align: left; }}
    table.pivot-table tbody td {{
        padding: 11px 22px; border-bottom: 1px solid #F1F5F9;
        text-align: center; color: #0F172A;
    }}
    table.pivot-table tbody td:first-child {{ text-align: left; font-weight: 600; color: #4F4CF3; }}
    table.pivot-table tbody tr:hover {{ background: #FAFBFF; }}
    table.pivot-table tr.total-row td {{
        font-weight: 700; background: #EEF2FF;
        border-top: 2px solid #4F4CF3; color: #021c6b;
    }}
    </style></head><body>
    <div class="section-title"><span class="dot"></span> Network × Status Cross-Tab</div>
    <p class="sub">Carrier count by Connection Status and P44 Network</p>
    <table class="pivot-table"><thead><tr>{header}</tr></thead>
    <tbody>{rows}</tbody></table>
    </body></html>
    """, height=height)


def render_export_cards():
    components.html("""
    <html><head><style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: #FFFFFF !important; font-family: 'Inter', sans-serif; }
    .section-title {
        font-size: 1.05rem; font-weight: 700; color: #0F172A;
        margin: 0.5rem 0 1.2rem 0; display: flex; align-items: center; gap: 10px;
    }
    .section-title .dot { width: 8px; height: 8px; background: #4F4CF3; border-radius: 50%; }
    .export-cards { display: flex; gap: 20px; flex-wrap: wrap; }
    .export-card {
        flex: 1; min-width: 280px;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 2rem;
        background: #fff;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }
    .export-card-icon {
        width: 48px; height: 48px;
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.3rem;
        margin-bottom: 1rem;
    }
    .export-card h4 { color: #0F172A; font-size: 1rem; margin-bottom: 0.4rem; }
    .export-card p { color: #64748B; font-size: 0.85rem; line-height: 1.5; }
    </style></head><body>
    <div class="section-title"><span class="dot"></span> Export Consolidated Report</div>
    <div class="export-cards">
        <div class="export-card">
            <div class="export-card-icon" style="background:#D1FAE5;">📗</div>
            <h4>Excel Report</h4>
            <p>Three sheets: Carrier List, Status Pivot, and Network × Status cross-tab.</p>
        </div>
        <div class="export-card">
            <div class="export-card-icon" style="background:#EEF2FF;">🌐</div>
            <h4>HTML Report</h4>
            <p>Styled standalone HTML report with carrier table and pivot summaries.</p>
        </div>
    </div>
    </body></html>
    """, height=220)


def render_landing():
    components.html("""
    <html><head><style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        font-family: 'Inter', sans-serif;
        background:
            radial-gradient(ellipse at 20% 50%, rgba(79,76,243,0.06) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 50%, rgba(0,114,236,0.06) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 0%, rgba(2,28,107,0.04) 0%, transparent 60%),
            #FFFFFF;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        min-height: 300px; padding: 2rem; text-align: center;
    }
    .landing-logo {
        width: 80px; height: 80px;
        background: linear-gradient(135deg, #021c6b 0%, #4F4CF3 100%);
        border-radius: 20px;
        display: flex; align-items: center; justify-content: center;
        font-size: 2.2rem;
        margin-bottom: 2rem;
        box-shadow: 0 12px 40px rgba(2,28,107,0.2);
    }
    .landing-title {
        font-size: 2.4rem; font-weight: 800; color: #021c6b;
        letter-spacing: -0.03em; margin-bottom: 0.5rem;
    }
    .landing-subtitle {
        font-size: 1.05rem; color: #64748B; margin-bottom: 1rem; font-weight: 400;
    }
    .landing-features {
        display: flex; gap: 2rem; margin-top: 1.5rem;
    }
    .landing-feature { text-align: center; }
    .landing-feature-icon { font-size: 1.4rem; margin-bottom: 0.4rem; }
    .landing-feature-label { font-size: 0.78rem; color: #64748B; font-weight: 500; }
    .upload-formats { display: inline-flex; gap: 6px; margin-top: 1rem; }
    .format-tag {
        background: rgba(79,76,243,0.1); color: #4F4CF3;
        font-size: 0.72rem; font-weight: 600; padding: 3px 10px;
        border-radius: 20px; letter-spacing: 0.03em;
    }
    </style></head><body>
    <div class="landing-logo">🔗</div>
    <h1 class="landing-title">Connection Accelerator</h1>
    <p class="landing-subtitle">Upload p44 Connection Center HTML exports to analyze carrier connections</p>
    <div class="upload-formats">
        <span class="format-tag">.HTML</span>
        <span class="format-tag">.HTM</span>
        <span class="format-tag">MULTIPLE FILES</span>
    </div>
    <div class="landing-features">
        <div class="landing-feature">
            <div class="landing-feature-icon">📊</div>
            <div class="landing-feature-label">Extract & Consolidate</div>
        </div>
        <div class="landing-feature">
            <div class="landing-feature-icon">🔍</div>
            <div class="landing-feature-label">Pivot Analysis</div>
        </div>
        <div class="landing-feature">
            <div class="landing-feature-icon">💾</div>
            <div class="landing-feature-label">Export Excel & HTML</div>
        </div>
    </div>
    </body></html>
    """, height=380)


def render_file_chips(files_info):
    """files_info: list of (name, count) tuples"""
    chips = ""
    for fname, count in files_info:
        chips += f"""<div class="file-chip">
            <span class="file-chip-icon">📄</span>
            <span class="file-chip-name">{esc(fname)}</span>
            <span class="file-chip-count">{count} carriers</span>
        </div>"""
    height = len(files_info) * 50 + 10
    components.html(f"""
    <html><head><style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: #FFFFFF !important; font-family: 'Inter', sans-serif; }}
    .file-chip {{
        display: flex; align-items: center; gap: 10px;
        background: #F8F9FC; border: 1px solid #E2E8F0;
        border-radius: 10px; padding: 10px 14px; font-size: 0.85rem;
        margin-bottom: 8px;
    }}
    .file-chip-icon {{ font-size: 1.1rem; }}
    .file-chip-name {{ flex: 1; font-weight: 500; color: #0F172A; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .file-chip-count {{ background: #EEF2FF; color: #4F4CF3; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 12px; }}
    </style></head><body>{chips}</body></html>
    """, height=height)


# ══════════════════════════════════════════════════════════════════════════════
# Session State
# ══════════════════════════════════════════════════════════════════════════════
if 'carriers' not in st.session_state:
    st.session_state.carriers = []
if 'files' not in st.session_state:
    st.session_state.files = {}
if 'page' not in st.session_state:
    st.session_state.page = 'landing'


# ══════════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == 'landing':
    render_landing()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded_files = st.file_uploader(
            "Drop HTML files here or click to browse",
            type=['html', 'htm'],
            accept_multiple_files=True,
            help="p44 Movement → Network → Connection Center",
            key="file_uploader"
        )

        if uploaded_files:
            for uf in uploaded_files:
                if uf.name not in st.session_state.files:
                    content = uf.read().decode('utf-8', errors='ignore')
                    st.session_state.files[uf.name] = content

            # Show file chips
            files_info = []
            for fname, content in st.session_state.files.items():
                count = len(parse_html(content, fname))
                files_info.append((fname, count))

            if files_info:
                render_file_chips(files_info)

            total_files = len(st.session_state.files)
            if st.button(
                f"🔍 Analyze {total_files} File{'s' if total_files > 1 else ''}",
                type="primary",
                use_container_width=True
            ):
                all_carriers = []
                for fname, content in st.session_state.files.items():
                    all_carriers.extend(parse_html(content, fname))
                st.session_state.carriers = all_carriers
                st.session_state.page = 'dashboard'
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == 'dashboard':
    df = pd.DataFrame(st.session_state.carriers)
    total = len(df)
    in_network = len(df[df['P44 Network'] == 'In-network']) if not df.empty else 0
    out_network = total - in_network
    n_files = len(st.session_state.files)

    # Top bar
    render_topbar(n_files, total)

    # Back button
    if st.button("← Upload More", key="back_btn"):
        st.session_state.page = 'landing'
        st.session_state.files = {}
        st.session_state.carriers = []
        st.rerun()

    # KPI Cards
    render_kpis(total, in_network, out_network)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Carrier Table", "📊 Pivot Analysis", "💾 Export"])

    # ── Tab 1: Carrier Table ────────────────────────────────────────────
    with tab1:
        render_legend()

        fcol1, fcol2, fcol3 = st.columns([1, 1, 2])
        with fcol1:
            network_filter = st.selectbox(
                "P44 NETWORK",
                ["All", "In-network", "Out-of-network"],
                key="filter_network"
            )
        with fcol2:
            status_options = ["All"] + sorted(df['Connection Status'].unique().tolist()) if not df.empty else ["All"]
            status_filter = st.selectbox(
                "CONNECTION STATUS",
                status_options,
                key="filter_status"
            )
        with fcol3:
            search_filter = st.text_input(
                "SEARCH CARRIER",
                placeholder="Type to search...",
                key="filter_search"
            )

        filtered = df.copy()
        if network_filter != "All":
            filtered = filtered[filtered['P44 Network'] == network_filter]
        if status_filter != "All":
            filtered = filtered[filtered['Connection Status'] == status_filter]
        if search_filter:
            filtered = filtered[filtered['Carrier Name'].str.lower().str.contains(search_filter.lower(), na=False)]

        render_carrier_table_component(filtered, total)

    # ── Tab 2: Pivot Analysis ───────────────────────────────────────────
    with tab2:
        render_pivot_component(df)
        render_crosstab_component(df)

    # ── Tab 3: Export ───────────────────────────────────────────────────
    with tab3:
        render_export_cards()

        ecol1, ecol2 = st.columns(2)
        with ecol1:
            excel_data = generate_excel_report(df)
            st.download_button(
                label="⬇ Download Excel Report",
                data=excel_data,
                file_name="connection_accelerator_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )
        with ecol2:
            html_report = generate_html_report(df)
            st.download_button(
                label="⬇ Download HTML Report",
                data=html_report,
                file_name="connection_accelerator_report.html",
                mime="text/html",
                use_container_width=True,
                type="secondary"
            )
