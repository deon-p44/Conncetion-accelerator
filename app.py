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
# Global CSS — force light theme on every Streamlit widget
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Force light mode on the entire app ────────────────── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"],
[data-testid="stAppViewBlockContainer"], .main, .stApp,
[data-testid="stMainBlockContainer"], [data-testid="stVerticalBlock"] {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Hide Streamlit chrome ─────────────────────────────── */
#MainMenu, footer, header, .stDeployButton,
div[data-testid="stToolbar"], div[data-testid="stDecoration"],
.viewerBadge_container__r5tak { display: none !important; }

.main .block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 1rem;
    max-width: 1400px;
}

/* ── iframes white bg ──────────────────────────────────── */
iframe { background: #FFFFFF !important; }

/* ── Selectbox / dropdown — FORCE white ────────────────── */
[data-baseweb="select"],
[data-baseweb="select"] > div,
[data-baseweb="popover"],
[data-baseweb="popover"] > div,
ul[role="listbox"],
ul[role="listbox"] li,
[data-baseweb="menu"],
[data-baseweb="menu"] li,
div[data-baseweb="select"] div[class*="option"],
div[data-baseweb="select"] div[class*="ValueContainer"],
div[data-baseweb="select"] div[class*="control"],
div[data-baseweb="select"] div[class*="menu"],
div[data-baseweb="select"] div[class*="singleValue"] {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
}
ul[role="listbox"] li:hover,
[data-baseweb="menu"] li:hover {
    background-color: #EEF2FF !important;
    color: #4F4CF3 !important;
}
[data-baseweb="select"] svg { fill: #64748B !important; }

/* ── Input fields ──────────────────────────────────────── */
input, textarea,
[data-baseweb="input"],
[data-baseweb="input"] input,
.stTextInput input {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border-color: #E2E8F0 !important;
}
input:focus, [data-baseweb="input"]:focus-within {
    border-color: #4F4CF3 !important;
    box-shadow: 0 0 0 3px rgba(79,76,243,0.1) !important;
}
input::placeholder { color: #94A3B8 !important; }

/* ── Labels ────────────────────────────────────────────── */
.stSelectbox label, .stTextInput label, label, .stFileUploader label {
    color: #0F172A !important;
    font-weight: 600 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
}

/* ── Tab styling ───────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #F8F9FC !important;
    border-radius: 12px;
    padding: 5px;
    border: 1px solid #E2E8F0;
}
.stTabs [data-baseweb="tab"] {
    padding: 10px 24px;
    border-radius: 9px;
    font-size: 0.88rem;
    font-weight: 500;
    color: #64748B !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: #FFFFFF !important;
    color: #4F4CF3 !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"] {
    background: #FFFFFF !important;
}

/* ── Primary button (Analyze, Download Excel) ──────────── */
button[kind="primary"],
.stButton > button[kind="primary"],
.stDownloadButton > button[kind="primary"] {
    background: linear-gradient(135deg, #021c6b, #4F4CF3) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(2,28,107,0.25) !important;
}
button[kind="primary"]:hover,
.stButton > button[kind="primary"]:hover,
.stDownloadButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 20px rgba(2,28,107,0.35) !important;
    transform: translateY(-1px);
}

/* ── Secondary button (Upload More, Download HTML) ─────── */
button[kind="secondary"],
.stButton > button[kind="secondary"],
.stDownloadButton > button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #021c6b !important;
    border: 2px solid #4F4CF3 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}
button[kind="secondary"]:hover,
.stButton > button[kind="secondary"]:hover,
.stDownloadButton > button[kind="secondary"]:hover {
    background-color: #EEF2FF !important;
    color: #4F4CF3 !important;
}

/* ── File uploader ─────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: #FFFFFF !important;
}
[data-testid="stFileUploader"] section {
    background: #FFFFFF !important;
    border: 2px dashed #C7D2FE !important;
    border-radius: 16px !important;
}
[data-testid="stFileUploader"] section:hover {
    border-color: #4F4CF3 !important;
    background: #F8F9FC !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: #FFFFFF !important;
}
[data-testid="stFileUploader"] button {
    background: #4F4CF3 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] span {
    color: #64748B !important;
}

/* ── Download buttons full width ───────────────────────── */
.stDownloadButton { width: 100%; }
.stDownloadButton > button { width: 100% !important; }

/* ── Divider ───────────────────────────────────────────── */
hr { border-color: #E2E8F0 !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Base CSS for components.html() blocks
# ══════════════════════════════════════════════════════════════════════════════
BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: #FFFFFF !important;
    color: #0F172A;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
}
.badge {
    display: inline-block; padding: 4px 12px; border-radius: 20px;
    font-size: 0.73rem; font-weight: 600; letter-spacing: 0.02em; white-space: nowrap;
}
.badge-in       { background: #DBEAFE; color: #1E40AF; }
.badge-out      { background: #FFF1F2; color: #9F1239; }
.badge-active   { background: #D1FAE5; color: #065F46; }
.badge-instant  { background: #C7D2FE; color: #3730A3; }
.badge-dev      { background: #FEF3C7; color: #92400E; }
.badge-inactive { background: #FEE2E2; color: #991B1B; }
.badge-new      { background: #FCE7F3; color: #9D174D; }
.badge-unknown  { background: #F1F5F9; color: #64748B; }
.section-title {
    font-size: 1.05rem; font-weight: 700; color: #0F172A;
    margin: 0.5rem 0 1rem; display: flex; align-items: center; gap: 10px;
}
.section-title .dot {
    width: 8px; height: 8px; background: #4F4CF3; border-radius: 50%;
}
.sub { color: #64748B; font-size: 0.88rem; margin-bottom: 1rem; }
"""

TABLE_CSS = """
table.data-table {
    width: 100%; border-collapse: separate; border-spacing: 0;
    border-radius: 14px; overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05); border: 1px solid #E2E8F0;
    font-size: 0.85rem;
}
table.data-table thead th {
    background: #021c6b; color: #fff; padding: 13px 16px; text-align: left;
    font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.05em; white-space: nowrap; position: sticky; top: 0; z-index: 1;
}
table.data-table tbody td {
    padding: 11px 16px; border-bottom: 1px solid #F1F5F9; color: #0F172A;
    background: #FFFFFF;
}
table.data-table tbody tr:hover td { background: #F8F9FC; }
table.data-table tbody tr:last-child td { border-bottom: none; }
"""

PIVOT_CSS = """
table.pivot-table {
    border-collapse: separate; border-spacing: 0; border-radius: 14px;
    overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    border: 1px solid #E2E8F0; font-size: 0.85rem; width: 100%;
}
table.pivot-table thead th {
    background: #021c6b; color: #fff; padding: 13px 20px; text-align: center;
    font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;
}
table.pivot-table thead th:first-child { text-align: left; }
table.pivot-table tbody td {
    padding: 11px 20px; border-bottom: 1px solid #F1F5F9;
    text-align: center; color: #0F172A; background: #FFFFFF;
}
table.pivot-table tbody td:first-child { text-align: left; font-weight: 600; color: #4F4CF3; }
table.pivot-table tbody tr:hover td { background: #F8F9FC; }
table.pivot-table tr.total-row td {
    font-weight: 700; background: #EEF2FF !important;
    border-top: 2px solid #4F4CF3; color: #021c6b;
}
"""


# ══════════════════════════════════════════════════════════════════════════════
# Status detection & helpers
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
    if 'Instant' in s: return 'badge-instant'
    if 'Active' in s: return 'badge-active'
    if 'Development' in s: return 'badge-dev'
    if 'Inactive' in s: return 'badge-inactive'
    if 'New' in s: return 'badge-new'
    return 'badge-unknown'

def network_badge_class(n):
    return 'badge-in' if n == 'In-network' else 'badge-out'

def esc(s):
    return html_lib.escape(str(s)) if s else ''


# ══════════════════════════════════════════════════════════════════════════════
# Parse HTML
# ══════════════════════════════════════════════════════════════════════════════
def parse_html(html_content, source_name):
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    carriers = []
    for ti, table in enumerate(tables):
        network = 'In-network' if ti == 0 else 'Out-of-network'
        for ri, row in enumerate(table.find_all('tr')):
            if ri == 0: continue
            cells = row.find_all('td')
            if len(cells) < 3: continue
            name = cells[1].get_text(strip=True)
            if not name: continue
            func_text = cells[2].get_text(strip=True)
            paths = [p.get('d','') for svg in cells[2].find_all('svg') for p in svg.find_all('path') if p.get('d')]
            carriers.append({
                'Carrier Name': name, 'P44 Network': network,
                'Connection Status': detect_status(paths),
                'Function': func_text, 'Source File': source_name,
            })
    return carriers


# ══════════════════════════════════════════════════════════════════════════════
# Export generators
# ══════════════════════════════════════════════════════════════════════════════
def generate_html_report(df):
    in_n = len(df[df['P44 Network'] == 'In-network'])
    rows = "".join(
        f"<tr><td>{i+1}</td><td>{esc(r['Carrier Name'])}</td><td>{esc(r['P44 Network'])}</td><td>{esc(r['Connection Status'])}</td><td>{esc(r['Function'])}</td></tr>"
        for i, (_, r) in enumerate(df.iterrows())
    )
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Connection Accelerator Report</title>
<style>*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:'Segoe UI',sans-serif;background:#fff;color:#1E293B;padding:2rem 3rem}}
h1{{color:#021c6b;font-size:1.6rem;border-bottom:3px solid #4F4CF3;padding-bottom:.5rem;margin-bottom:.5rem}}
.meta{{color:#64748B;font-size:.9rem;margin-bottom:2rem}}h2{{color:#4F4CF3;font-size:1.15rem;margin:2rem 0 .75rem}}
table{{border-collapse:collapse;width:100%;margin-bottom:1.5rem}}th{{background:#021c6b;color:#fff;padding:10px 14px;text-align:left;font-size:.82rem;text-transform:uppercase}}
td{{padding:8px 14px;border-bottom:1px solid #F1F5F9;font-size:.88rem}}tr:hover{{background:#F8FAFC}}</style></head><body>
<h1>🔗 Connection Accelerator Report</h1>
<p class="meta">{len(df)} carriers | In-network: {in_n} | Out-of-network: {len(df)-in_n}</p>
<h2>Carrier List</h2><table><thead><tr><th>#</th><th>Carrier Name</th><th>P44 Network</th><th>Connection Status</th><th>Function</th></tr></thead><tbody>{rows}</tbody></table></body></html>"""

def generate_excel_report(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        cdf = df.copy(); cdf.insert(0, '#', range(1, len(cdf)+1))
        cdf.to_excel(writer, sheet_name='Carrier List', index=False)
        pc = df['Connection Status'].value_counts().reset_index()
        pc.columns = ['Connection Status', 'Carrier Count']
        pd.concat([pc, pd.DataFrame([{'Connection Status':'Total','Carrier Count':len(df)}])], ignore_index=True).to_excel(writer, sheet_name='Status Pivot', index=False)
        ct = pd.crosstab(df['Connection Status'], df['P44 Network'], margins=True, margins_name='Total')
        cols = [c for c in ['In-network','Out-of-network','Total'] if c in ct.columns]
        ct[cols].to_excel(writer, sheet_name='Network × Status')
    output.seek(0)
    return output


# ══════════════════════════════════════════════════════════════════════════════
# Component renderers (all use components.html for perfect CSS)
# ══════════════════════════════════════════════════════════════════════════════

def render_topbar(n_files, total):
    components.html(f"""<html><head><style>
    {BASE_CSS}
    .topbar {{
        background: #021c6b; padding: 0 2.5rem; height: 56px;
        display: flex; align-items: center; gap: 14px;
    }}
    .topbar-logo {{
        width: 32px; height: 32px;
        background: linear-gradient(135deg, #4F4CF3, #0072ec);
        border-radius: 8px; display: flex; align-items: center; justify-content: center;
        font-size: 0.95rem;
    }}
    .topbar-title {{ color: #fff; font-weight: 600; font-size: 0.95rem; flex: 1; }}
    .topbar-files {{ color: rgba(255,255,255,0.5); font-size: 0.8rem; }}
    </style></head><body>
    <div class="topbar">
        <div class="topbar-logo">🔗</div>
        <div class="topbar-title">Connection Accelerator Analysis</div>
        <div class="topbar-files">{n_files} file(s) · {total} carriers</div>
    </div></body></html>""", height=58)


def render_kpis(total, in_net, out_net):
    components.html(f"""<html><head><style>
    {BASE_CSS}
    .kpis {{ display: flex; gap: 20px; padding: 4px 2px; }}
    .kpi {{
        flex: 1; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px;
        padding: 1.4rem 1.6rem; position: relative; overflow: hidden;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }}
    .kpi::before {{
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
    }}
    .kpi-total::before {{ background: linear-gradient(90deg, #021c6b, #4F4CF3); }}
    .kpi-in::before    {{ background: linear-gradient(90deg, #059669, #34D399); }}
    .kpi-out::before   {{ background: linear-gradient(90deg, #DC2626, #FB923C); }}
    .kpi-value {{
        font-size: 2.6rem; font-weight: 800; line-height: 1.1; letter-spacing: -0.03em;
    }}
    .kpi-total .kpi-value {{ color: #021c6b; }}
    .kpi-in .kpi-value    {{ color: #059669; }}
    .kpi-out .kpi-value   {{ color: #DC2626; }}
    .kpi-label {{
        font-size: 0.75rem; font-weight: 600; color: #64748B;
        text-transform: uppercase; letter-spacing: 0.05em; margin-top: 6px;
    }}
    .kpi-icon {{
        position: absolute; top: 1rem; right: 1.3rem; font-size: 1.6rem; opacity: 0.12;
    }}
    </style></head><body>
    <div class="kpis">
        <div class="kpi kpi-total"><div class="kpi-value">{total}</div><div class="kpi-label">Total Carriers</div><div class="kpi-icon">📦</div></div>
        <div class="kpi kpi-in"><div class="kpi-value">{in_net}</div><div class="kpi-label">In-Network</div><div class="kpi-icon">✅</div></div>
        <div class="kpi kpi-out"><div class="kpi-value">{out_net}</div><div class="kpi-label">Out-of-Network</div><div class="kpi-icon">⚠️</div></div>
    </div></body></html>""", height=130)


def render_legend():
    components.html(f"""<html><head><style>
    {BASE_CSS}
    .legend {{
        display: flex; gap: 12px; flex-wrap: wrap; padding: 10px 16px;
        background: #F8F9FC; border-radius: 10px; border: 1px solid #E2E8F0;
    }}
    </style></head><body>
    <div class="legend">
        <span class="badge badge-instant">Instant Live</span>
        <span class="badge badge-active">Active</span>
        <span class="badge badge-dev">In Development</span>
        <span class="badge badge-inactive">Inactive</span>
        <span class="badge badge-new">New Integration Required</span>
    </div></body></html>""", height=50)


def render_carrier_table(df, total):
    if df.empty:
        components.html(f"""<html><head><style>{BASE_CSS}</style></head><body>
        <p style="color:#64748B;padding:2rem;text-align:center;">No carriers match the current filters.</p>
        </body></html>""", height=80)
        return

    rows = ""
    for i, (_, c) in enumerate(df.iterrows()):
        rows += f"""<tr>
            <td>{i+1}</td>
            <td style="font-weight:500;">{esc(c['Carrier Name'])}</td>
            <td><span class="badge {network_badge_class(c['P44 Network'])}">{esc(c['P44 Network'])}</span></td>
            <td><span class="badge {status_badge_class(c['Connection Status'])}">{esc(c['Connection Status'])}</span></td>
            <td>{esc(c['Function'])}</td>
        </tr>"""

    h = min(46 + len(df) * 44 + 40, 750)
    components.html(f"""<html><head><style>
    {BASE_CSS} {TABLE_CSS}
    .wrap {{ overflow: auto; max-height: 680px; }}
    .caption {{ font-size: 0.8rem; color: #64748B; margin-top: 0.6rem; }}
    </style></head><body>
    <div class="wrap">
    <table class="data-table"><thead><tr>
        <th>#</th><th>Carrier Name</th><th>P44 Network</th><th>Connection Status</th><th>Function</th>
    </tr></thead><tbody>{rows}</tbody></table></div>
    <div class="caption">Showing {len(df)} of {total} carriers</div>
    </body></html>""", height=h, scrolling=True)


def render_pivot(df):
    counts = df['Connection Status'].value_counts().sort_values(ascending=False)
    rows = "".join(f"<tr><td>{esc(s)}</td><td>{c}</td></tr>" for s, c in counts.items())
    rows += f'<tr class="total-row"><td>Total</td><td>{counts.sum()}</td></tr>'
    h = 80 + (len(counts) + 1) * 42 + 20

    components.html(f"""<html><head><style>
    {BASE_CSS} {PIVOT_CSS}
    </style></head><body>
    <div class="section-title"><span class="dot"></span> Connection Status Pivot</div>
    <p class="sub">Carrier count by Connection Status</p>
    <table class="pivot-table"><thead><tr><th>Connection Status</th><th>Carrier Count</th></tr></thead>
    <tbody>{rows}</tbody></table>
    </body></html>""", height=h)


def render_crosstab(df):
    statuses = sorted(df['Connection Status'].unique())
    nets = ['In-network', 'Out-of-network']
    header = "<th>Connection Status</th>" + "".join(f"<th>{esc(n)}</th>" for n in nets) + "<th>Total</th>"
    rows = ""
    ct = {n: 0 for n in nets}; gt = 0
    for s in statuses:
        rt = 0; cells = f"<td>{esc(s)}</td>"
        for n in nets:
            v = len(df[(df['Connection Status']==s) & (df['P44 Network']==n)])
            cells += f"<td>{v}</td>"; rt += v; ct[n] += v
        gt += rt; cells += f"<td>{rt}</td>"
        rows += f"<tr>{cells}</tr>"
    rows += f'<tr class="total-row"><td>Total</td>{"".join(f"<td>{ct[n]}</td>" for n in nets)}<td>{gt}</td></tr>'
    h = 80 + (len(statuses) + 1) * 42 + 20

    components.html(f"""<html><head><style>
    {BASE_CSS} {PIVOT_CSS}
    </style></head><body>
    <div class="section-title"><span class="dot"></span> Network × Status Cross-Tab</div>
    <p class="sub">Carrier count by Connection Status and P44 Network</p>
    <table class="pivot-table"><thead><tr>{header}</tr></thead>
    <tbody>{rows}</tbody></table>
    </body></html>""", height=h)


def render_export_cards():
    components.html(f"""<html><head><style>
    {BASE_CSS}
    .cards {{ display: flex; gap: 20px; }}
    .card {{
        flex: 1; border: 1px solid #E2E8F0; border-radius: 16px; padding: 1.8rem;
        background: #FFFFFF; box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }}
    .card-icon {{
        width: 48px; height: 48px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.3rem; margin-bottom: 1rem;
    }}
    .card h4 {{ color: #0F172A; font-size: 1rem; margin-bottom: 0.3rem; }}
    .card p {{ color: #64748B; font-size: 0.85rem; line-height: 1.5; }}
    </style></head><body>
    <div class="section-title"><span class="dot"></span> Export Consolidated Report</div>
    <div class="cards">
        <div class="card">
            <div class="card-icon" style="background:#D1FAE5;">📗</div>
            <h4>Excel Report</h4>
            <p>Three sheets: Carrier List, Status Pivot, and Network × Status cross-tab.</p>
        </div>
        <div class="card">
            <div class="card-icon" style="background:#EEF2FF;">🌐</div>
            <h4>HTML Report</h4>
            <p>Styled standalone HTML report with carrier table and pivot summaries.</p>
        </div>
    </div></body></html>""", height=210)


def render_landing():
    components.html(f"""<html><head><style>
    {BASE_CSS}
    body {{
        background:
            radial-gradient(ellipse at 20% 50%, rgba(79,76,243,0.06) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 50%, rgba(0,114,236,0.06) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 0%, rgba(2,28,107,0.04) 0%, transparent 60%),
            #FFFFFF !important;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        min-height: 320px; padding: 2rem; text-align: center;
    }}
    .logo {{
        width: 80px; height: 80px;
        background: linear-gradient(135deg, #021c6b, #4F4CF3);
        border-radius: 20px; display: flex; align-items: center; justify-content: center;
        font-size: 2.2rem; margin-bottom: 2rem;
        box-shadow: 0 12px 40px rgba(2,28,107,0.2);
    }}
    h1 {{ font-size: 2.4rem; font-weight: 800; color: #021c6b; letter-spacing: -0.03em; margin-bottom: 0.5rem; }}
    .sub {{ font-size: 1.05rem; color: #64748B; margin-bottom: 1.5rem; }}
    .tags {{ display: flex; gap: 6px; justify-content: center; }}
    .tag {{
        background: rgba(79,76,243,0.1); color: #4F4CF3;
        font-size: 0.72rem; font-weight: 600; padding: 3px 10px;
        border-radius: 20px; letter-spacing: 0.03em;
    }}
    .features {{ display: flex; gap: 2.5rem; margin-top: 2rem; }}
    .feat {{ text-align: center; }}
    .feat-icon {{ font-size: 1.4rem; margin-bottom: 0.3rem; }}
    .feat-label {{ font-size: 0.78rem; color: #64748B; font-weight: 500; }}
    </style></head><body>
    <div class="logo">🔗</div>
    <h1>Connection Accelerator</h1>
    <p class="sub">Upload p44 Connection Center HTML exports to analyze carrier connections</p>
    <div class="tags">
        <span class="tag">.HTML</span><span class="tag">.HTM</span><span class="tag">MULTIPLE FILES</span>
    </div>
    <div class="features">
        <div class="feat"><div class="feat-icon">📊</div><div class="feat-label">Extract & Consolidate</div></div>
        <div class="feat"><div class="feat-icon">🔍</div><div class="feat-label">Pivot Analysis</div></div>
        <div class="feat"><div class="feat-icon">💾</div><div class="feat-label">Export Excel & HTML</div></div>
    </div></body></html>""", height=380)


def render_file_chips(files_info):
    chips = "".join(
        f'<div class="chip"><span class="ci">📄</span><span class="cn">{esc(f)}</span><span class="cc">{c} carriers</span></div>'
        for f, c in files_info
    )
    components.html(f"""<html><head><style>
    {BASE_CSS}
    .chip {{
        display: flex; align-items: center; gap: 10px;
        background: #F8F9FC; border: 1px solid #E2E8F0; border-radius: 10px;
        padding: 10px 14px; margin-bottom: 8px;
    }}
    .ci {{ font-size: 1.1rem; }}
    .cn {{ flex: 1; font-weight: 500; color: #0F172A; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .cc {{ background: #EEF2FF; color: #4F4CF3; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 12px; }}
    </style></head><body>{chips}</body></html>""", height=len(files_info)*50+10)


# ══════════════════════════════════════════════════════════════════════════════
# Session State
# ══════════════════════════════════════════════════════════════════════════════
if 'carriers' not in st.session_state: st.session_state.carriers = []
if 'files' not in st.session_state: st.session_state.files = {}
if 'page' not in st.session_state: st.session_state.page = 'landing'


# ══════════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == 'landing':
    render_landing()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded_files = st.file_uploader(
            "Upload HTML files", type=['html', 'htm'],
            accept_multiple_files=True, help="p44 Movement → Network → Connection Center",
        )
        if uploaded_files:
            for uf in uploaded_files:
                if uf.name not in st.session_state.files:
                    st.session_state.files[uf.name] = uf.read().decode('utf-8', errors='ignore')
            fi = [(f, len(parse_html(c, f))) for f, c in st.session_state.files.items()]
            if fi: render_file_chips(fi)
            n = len(st.session_state.files)
            if st.button(f"🔍 Analyze {n} File{'s' if n > 1 else ''}", type="primary", use_container_width=True):
                st.session_state.carriers = [
                    c for f, html in st.session_state.files.items() for c in parse_html(html, f)
                ]
                st.session_state.page = 'dashboard'
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == 'dashboard':
    df = pd.DataFrame(st.session_state.carriers)
    total = len(df)
    in_net = len(df[df['P44 Network']=='In-network']) if not df.empty else 0
    out_net = total - in_net

    render_topbar(len(st.session_state.files), total)

    if st.button("← Upload More"):
        st.session_state.page = 'landing'
        st.session_state.files = {}
        st.session_state.carriers = []
        st.rerun()

    render_kpis(total, in_net, out_net)

    tab1, tab2, tab3 = st.tabs(["📋 Carrier Table", "📊 Pivot Analysis", "💾 Export"])

    with tab1:
        render_legend()
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            nf = st.selectbox("P44 NETWORK", ["All", "In-network", "Out-of-network"])
        with c2:
            opts = ["All"] + sorted(df['Connection Status'].unique().tolist()) if not df.empty else ["All"]
            sf = st.selectbox("CONNECTION STATUS", opts)
        with c3:
            sq = st.text_input("SEARCH CARRIER", placeholder="Type to search...")
        filt = df.copy()
        if nf != "All": filt = filt[filt['P44 Network']==nf]
        if sf != "All": filt = filt[filt['Connection Status']==sf]
        if sq: filt = filt[filt['Carrier Name'].str.lower().str.contains(sq.lower(), na=False)]
        render_carrier_table(filt, total)

    with tab2:
        render_pivot(df)
        render_crosstab(df)

    with tab3:
        render_export_cards()
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("⬇ Download Excel Report", generate_excel_report(df),
                "connection_accelerator_report.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True, type="primary")
        with c2:
            st.download_button("⬇ Download HTML Report", generate_html_report(df),
                "connection_accelerator_report.html", "text/html",
                use_container_width=True, type="secondary")
