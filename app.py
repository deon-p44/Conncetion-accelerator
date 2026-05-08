import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from bs4 import BeautifulSoup
import io
import html as html_lib

# ═════════════════════════════════════════════════════════════════════════
# CONFIG
# ═════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Connection Accelerator Analysis",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═════════════════════════════════════════════════════════════════════════
# GLOBAL STREAMLIT CSS  — force every native widget to light mode
# ═════════════════════════════════════════════════════════════════════════
st.markdown(
    """
<style>
/* ── 1. Root: force white everywhere ──────────────────── */
:root {
  color-scheme: light !important;
}
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
[data-testid="stMainBlockContainer"],
[data-testid="stVerticalBlock"],
[data-testid="stMain"],
.main, .stApp, section[data-testid="stSidebar"] {
  background-color: #FFFFFF !important;
  color: #0F172A !important;
}

/* ── 2. Hide chrome ───────────────────────────────────── */
#MainMenu, footer, header, .stDeployButton,
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
div[data-testid="stStatusWidget"],
.viewerBadge_container__r5tak {
  display: none !important;
}

.main .block-container {
  padding-top: 0.5rem !important;
  max-width: 1400px;
}

/* ── 3. iframes ───────────────────────────────────────── */
iframe { background: #FFFFFF !important; }

/* ── 4. Selectbox & dropdowns — FULL white override ──── */
/* Container */
[data-baseweb="select"] > div {
  background: #FFFFFF !important;
  border-color: #E2E8F0 !important;
  color: #0F172A !important;
  border-radius: 10px !important;
}
/* Value text */
[data-baseweb="select"] span,
[data-baseweb="select"] div[class*="singleValue"],
[data-baseweb="select"] div[class*="ValueContainer"],
[data-baseweb="select"] div[class*="placeholder"] {
  color: #0F172A !important;
}
/* Arrow icon */
[data-baseweb="select"] svg {
  fill: #64748B !important;
}
/* Dropdown menu */
[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="popover"] ul,
[data-baseweb="menu"],
ul[role="listbox"] {
  background-color: #FFFFFF !important;
  border: 1px solid #E2E8F0 !important;
  border-radius: 10px !important;
  box-shadow: 0 8px 24px rgba(0,0,0,0.1) !important;
}
/* Dropdown items */
ul[role="listbox"] li,
[data-baseweb="menu"] li,
[data-baseweb="menu"] ul li {
  background-color: #FFFFFF !important;
  color: #0F172A !important;
}
ul[role="listbox"] li:hover,
ul[role="listbox"] li[aria-selected="true"],
[data-baseweb="menu"] li:hover {
  background-color: #EEF2FF !important;
  color: #4F4CF3 !important;
}
/* Focus ring */
[data-baseweb="select"] > div:focus-within {
  border-color: #4F4CF3 !important;
  box-shadow: 0 0 0 3px rgba(79,76,243,0.12) !important;
}

/* ── 5. Text input ────────────────────────────────────── */
.stTextInput > div > div {
  background: #FFFFFF !important;
  border-color: #E2E8F0 !important;
  border-radius: 10px !important;
}
.stTextInput input {
  background: #FFFFFF !important;
  color: #0F172A !important;
}
.stTextInput input::placeholder { color: #94A3B8 !important; }
.stTextInput > div > div:focus-within {
  border-color: #4F4CF3 !important;
  box-shadow: 0 0 0 3px rgba(79,76,243,0.12) !important;
}

/* ── 6. Labels ────────────────────────────────────────── */
.stSelectbox label,
.stTextInput label,
.stFileUploader label {
  color: #334155 !important;
  font-weight: 600 !important;
  font-size: 0.75rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.04em !important;
}

/* ── 7. Tabs ──────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: #F1F5F9 !important;
  border-radius: 12px !important;
  padding: 4px !important;
  gap: 4px !important;
  border: 1px solid #E2E8F0 !important;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 8px !important;
  color: #64748B !important;
  font-weight: 500 !important;
  background: transparent !important;
  padding: 8px 20px !important;
}
.stTabs [aria-selected="true"] {
  background: #FFFFFF !important;
  color: #021c6b !important;
  font-weight: 600 !important;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08) !important;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"] { background: #FFFFFF !important; }

/* ── 8. ALL buttons — consistent styling ──────────────── */
/* Primary: navy gradient */
.stButton > button[kind="primary"],
.stDownloadButton > button[kind="primary"],
.stFormSubmitButton > button {
  background: linear-gradient(135deg, #021c6b 0%, #4F4CF3 100%) !important;
  color: #FFFFFF !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  padding: 0.6rem 1.5rem !important;
  box-shadow: 0 4px 14px rgba(2,28,107,0.25) !important;
  transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"]:hover,
.stDownloadButton > button[kind="primary"]:hover {
  box-shadow: 0 6px 20px rgba(2,28,107,0.35) !important;
}
/* Secondary: white with indigo border */
.stButton > button[kind="secondary"],
.stDownloadButton > button[kind="secondary"],
.stButton > button:not([kind]) {
  background: #FFFFFF !important;
  color: #021c6b !important;
  border: 1.5px solid #C7D2FE !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  padding: 0.6rem 1.5rem !important;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
  transition: all 0.2s ease !important;
}
.stButton > button[kind="secondary"]:hover,
.stDownloadButton > button[kind="secondary"]:hover,
.stButton > button:not([kind]):hover {
  background: #EEF2FF !important;
  border-color: #4F4CF3 !important;
  color: #4F4CF3 !important;
}
/* Download button width */
.stDownloadButton { width: 100% !important; }
.stDownloadButton > button { width: 100% !important; }

/* ── 9. File uploader ─────────────────────────────────── */
[data-testid="stFileUploader"] section {
  background: #FAFBFF !important;
  border: 2px dashed #C7D2FE !important;
  border-radius: 14px !important;
  padding: 1.5rem !important;
}
[data-testid="stFileUploader"] section:hover {
  border-color: #4F4CF3 !important;
  background: #F0F2FF !important;
}
[data-testid="stFileUploader"] button {
  background: #4F4CF3 !important;
  color: #FFF !important;
  border: none !important;
  border-radius: 8px !important;
}
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] p {
  color: #64748B !important;
}
[data-testid="stFileUploaderDropzone"] {
  background: transparent !important;
}

/* ── 10. Column gaps ──────────────────────────────────── */
[data-testid="stHorizontalBlock"] { gap: 1rem !important; }
</style>
""",
    unsafe_allow_html=True,
)


# ═════════════════════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════════════════════
STATUS_MAP = [
    ("M9 16.17", "Active Connection"),
    ("M9 16", "Active Connection"),
    ("M17.3 6.3", "Inactive Connection"),
    ("M11 15h2v2", "New Integration Required"),
    ("M11 7h2v2", "In Development Connection"),
    ("M12 2C6.48", "Instant Live Connection"),
]

def detect_status(paths):
    for d in paths:
        for prefix, status in STATUS_MAP:
            if d.startswith(prefix):
                return status
    return "Unknown"

def stat_cls(s):
    if "Instant" in s: return "badge-instant"
    if "Active" in s: return "badge-active"
    if "Development" in s: return "badge-dev"
    if "Inactive" in s: return "badge-inactive"
    if "New" in s: return "badge-new"
    return "badge-unknown"

def net_cls(n):
    return "badge-in" if n == "In-network" else "badge-out"

def esc(s):
    return html_lib.escape(str(s)) if s else ""

def parse_html(raw, src):
    soup = BeautifulSoup(raw, "html.parser")
    out = []
    for ti, tbl in enumerate(soup.find_all("table")):
        net = "In-network" if ti == 0 else "Out-of-network"
        for ri, row in enumerate(tbl.find_all("tr")):
            if ri == 0: continue
            td = row.find_all("td")
            if len(td) < 3: continue
            name = td[1].get_text(strip=True)
            if not name: continue
            paths = [p.get("d","") for svg in td[2].find_all("svg") for p in svg.find_all("path") if p.get("d")]
            out.append({"Carrier Name": name, "P44 Network": net,
                         "Connection Status": detect_status(paths),
                         "Function": td[2].get_text(strip=True), "Source File": src})
    return out


# ═════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═════════════════════════════════════════════════════════════════════════
def make_html_report(df):
    inn = len(df[df["P44 Network"]=="In-network"])
    rows = "".join(f"<tr><td>{i+1}</td><td>{esc(r['Carrier Name'])}</td><td>{esc(r['P44 Network'])}</td><td>{esc(r['Connection Status'])}</td><td>{esc(r['Function'])}</td></tr>" for i,(_,r) in enumerate(df.iterrows()))
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Connection Accelerator Report</title>
<style>*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:'Segoe UI',sans-serif;background:#fff;color:#1E293B;padding:2rem 3rem}}
h1{{color:#021c6b;font-size:1.6rem;border-bottom:3px solid #4F4CF3;padding-bottom:.5rem;margin-bottom:.5rem}}
.meta{{color:#64748B;font-size:.9rem;margin-bottom:2rem}}h2{{color:#4F4CF3;font-size:1.15rem;margin:2rem 0 .75rem}}
table{{border-collapse:collapse;width:100%;margin-bottom:1.5rem}}th{{background:#021c6b;color:#fff;padding:10px 14px;text-align:left;font-size:.82rem;text-transform:uppercase}}
td{{padding:8px 14px;border-bottom:1px solid #F1F5F9;font-size:.88rem}}tr:hover{{background:#F8FAFC}}</style></head><body>
<h1>🔗 Connection Accelerator Report</h1><p class="meta">{len(df)} carriers | In-network: {inn} | Out-of-network: {len(df)-inn}</p>
<h2>Carrier List</h2><table><thead><tr><th>#</th><th>Carrier Name</th><th>P44 Network</th><th>Connection Status</th><th>Function</th></tr></thead><tbody>{rows}</tbody></table></body></html>"""

def make_excel(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as w:
        cdf = df.copy(); cdf.insert(0,"#",range(1,len(cdf)+1))
        cdf.to_excel(w, sheet_name="Carrier List", index=False)
        pc = df["Connection Status"].value_counts().reset_index(); pc.columns=["Connection Status","Carrier Count"]
        pd.concat([pc,pd.DataFrame([{"Connection Status":"Total","Carrier Count":len(df)}])],ignore_index=True).to_excel(w,sheet_name="Status Pivot",index=False)
        ct = pd.crosstab(df["Connection Status"],df["P44 Network"],margins=True,margins_name="Total")
        ct[[c for c in ["In-network","Out-of-network","Total"] if c in ct.columns]].to_excel(w,sheet_name="Network × Status")
    buf.seek(0); return buf


# ═════════════════════════════════════════════════════════════════════════
# COMPONENT CSS (shared by every components.html call)
# ═════════════════════════════════════════════════════════════════════════
_FONT = "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');"
_RESET = "* {box-sizing:border-box;margin:0;padding:0;} html,body {font-family:'Inter',sans-serif;background:#fff!important;color:#0F172A;line-height:1.5;-webkit-font-smoothing:antialiased;}"
_BADGE = """.badge{display:inline-block;padding:4px 12px;border-radius:20px;font-size:.72rem;font-weight:600;letter-spacing:.02em;white-space:nowrap}
.badge-in{background:#DBEAFE;color:#1E40AF}.badge-out{background:#FFF1F2;color:#9F1239}
.badge-active{background:#D1FAE5;color:#065F46}.badge-instant{background:#C7D2FE;color:#3730A3}
.badge-dev{background:#FEF3C7;color:#92400E}.badge-inactive{background:#FEE2E2;color:#991B1B}
.badge-new{background:#FCE7F3;color:#9D174D}.badge-unknown{background:#F1F5F9;color:#64748B}"""

_HDR = """.sh{font-size:1.05rem;font-weight:700;color:#0F172A;display:flex;align-items:center;gap:10px;margin-bottom:.8rem}
.sh .dot{width:8px;height:8px;background:#4F4CF3;border-radius:50%}
.desc{color:#64748B;font-size:.85rem;margin-bottom:1rem}"""

_TBL = """table.dt{width:100%;border-collapse:separate;border-spacing:0;border-radius:14px;overflow:hidden;
box-shadow:0 1px 4px rgba(0,0,0,.05);border:1px solid #E2E8F0;font-size:.84rem}
table.dt thead th{background:#021c6b;color:#fff;padding:12px 16px;text-align:left;font-size:.73rem;font-weight:600;
text-transform:uppercase;letter-spacing:.06em;white-space:nowrap;position:sticky;top:0;z-index:1}
table.dt tbody td{padding:10px 16px;border-bottom:1px solid #F1F5F9;color:#0F172A;background:#fff}
table.dt tbody tr:hover td{background:#F8F9FC}
table.dt tbody tr:last-child td{border-bottom:none}"""

_PVT = """table.pt{border-collapse:separate;border-spacing:0;border-radius:14px;overflow:hidden;
box-shadow:0 1px 4px rgba(0,0,0,.05);border:1px solid #E2E8F0;font-size:.84rem;width:100%}
table.pt thead th{background:#021c6b;color:#fff;padding:12px 20px;text-align:center;font-size:.73rem;
font-weight:600;text-transform:uppercase;letter-spacing:.06em}
table.pt thead th:first-child{text-align:left}
table.pt tbody td{padding:10px 20px;border-bottom:1px solid #F1F5F9;text-align:center;color:#0F172A;background:#fff}
table.pt tbody td:first-child{text-align:left;font-weight:600;color:#4F4CF3}
table.pt tbody tr:hover td{background:#F8F9FC}
table.pt tr.tot td{font-weight:700;background:#EEF2FF!important;border-top:2px solid #4F4CF3;color:#021c6b}"""

def _css(*extras):
    return f"<style>{_FONT}{_RESET}{_BADGE}{_HDR}{''.join(extras)}</style>"


# ═════════════════════════════════════════════════════════════════════════
# VISUAL COMPONENTS
# ═════════════════════════════════════════════════════════════════════════

def ui_topbar(n_files, total):
    components.html(f"""<html><head>{_css()}<style>
    .bar{{background:#021c6b;padding:0 2.5rem;height:56px;display:flex;align-items:center;gap:14px}}
    .logo{{width:32px;height:32px;background:linear-gradient(135deg,#4F4CF3,#0072ec);border-radius:8px;
    display:flex;align-items:center;justify-content:center;font-size:.95rem}}
    .title{{color:#fff;font-weight:600;font-size:.95rem;flex:1}}
    .info{{color:rgba(255,255,255,.5);font-size:.8rem}}
    </style></head><body>
    <div class="bar"><div class="logo">🔗</div><div class="title">Connection Accelerator Analysis</div>
    <div class="info">{n_files} file(s) · {total} carriers</div></div></body></html>""", height=58)


def ui_kpis(total, inn, out):
    components.html(f"""<html><head>{_css()}<style>
    .row{{display:flex;gap:20px;padding:4px 2px}}
    .k{{flex:1;background:#fff;border:1px solid #E2E8F0;border-radius:16px;padding:1.3rem 1.5rem;
    position:relative;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.04)}}
    .k::before{{content:'';position:absolute;top:0;left:0;right:0;height:4px}}
    .k1::before{{background:linear-gradient(90deg,#021c6b,#4F4CF3)}}
    .k2::before{{background:linear-gradient(90deg,#059669,#34D399)}}
    .k3::before{{background:linear-gradient(90deg,#DC2626,#FB923C)}}
    .v{{font-size:2.5rem;font-weight:800;line-height:1.1;letter-spacing:-.03em}}
    .k1 .v{{color:#021c6b}}.k2 .v{{color:#059669}}.k3 .v{{color:#DC2626}}
    .l{{font-size:.73rem;font-weight:600;color:#64748B;text-transform:uppercase;letter-spacing:.05em;margin-top:6px}}
    .ic{{position:absolute;top:1rem;right:1.2rem;font-size:1.5rem;opacity:.12}}
    </style></head><body>
    <div class="row">
      <div class="k k1"><div class="v">{total}</div><div class="l">Total Carriers</div><div class="ic">📦</div></div>
      <div class="k k2"><div class="v">{inn}</div><div class="l">In-Network</div><div class="ic">✅</div></div>
      <div class="k k3"><div class="v">{out}</div><div class="l">Out-of-Network</div><div class="ic">⚠️</div></div>
    </div></body></html>""", height=125)


def ui_legend():
    components.html(f"""<html><head>{_css()}<style>
    .lg{{display:flex;gap:10px;flex-wrap:wrap;padding:10px 16px;background:#F8F9FC;border-radius:10px;border:1px solid #E2E8F0}}
    </style></head><body>
    <div class="lg">
      <span class="badge badge-instant">Instant Live</span>
      <span class="badge badge-active">Active</span>
      <span class="badge badge-dev">In Development</span>
      <span class="badge badge-inactive">Inactive</span>
      <span class="badge badge-new">New Integration Required</span>
    </div></body></html>""", height=48)


def ui_carrier_table(df, total):
    if df.empty:
        components.html(f"""<html><head>{_css()}</head><body>
        <p style="color:#94A3B8;padding:3rem;text-align:center;font-size:.95rem">No carriers match the current filters.</p>
        </body></html>""", height=100)
        return
    rows = "".join(f"""<tr><td>{i+1}</td><td style="font-weight:500">{esc(r['Carrier Name'])}</td>
        <td><span class="badge {net_cls(r['P44 Network'])}">{esc(r['P44 Network'])}</span></td>
        <td><span class="badge {stat_cls(r['Connection Status'])}">{esc(r['Connection Status'])}</span></td>
        <td style="color:#64748B">{esc(r['Function'])}</td></tr>""" for i,(_,r) in enumerate(df.iterrows()))
    h = min(48 + len(df)*43 + 40, 800)
    components.html(f"""<html><head>{_css(_TBL)}<style>
    .w{{overflow:auto;max-height:720px}} .cap{{font-size:.8rem;color:#94A3B8;margin-top:.6rem}}
    </style></head><body>
    <div class="w"><table class="dt"><thead><tr><th>#</th><th>Carrier Name</th><th>P44 Network</th><th>Connection Status</th><th>Function</th></tr></thead>
    <tbody>{rows}</tbody></table></div>
    <div class="cap">Showing {len(df)} of {total} carriers</div></body></html>""", height=h, scrolling=True)


def ui_pivot(df):
    counts = df["Connection Status"].value_counts().sort_values(ascending=False)
    rows = "".join(f"<tr><td>{esc(s)}</td><td>{c}</td></tr>" for s,c in counts.items())
    rows += f'<tr class="tot"><td>Total</td><td>{counts.sum()}</td></tr>'
    h = 90 + (len(counts)+1)*43 + 10
    components.html(f"""<html><head>{_css(_PVT,_HDR)}</head><body>
    <div class="sh"><span class="dot"></span>Connection Status Pivot</div>
    <p class="desc">Carrier count by Connection Status</p>
    <table class="pt"><thead><tr><th>Connection Status</th><th>Carrier Count</th></tr></thead>
    <tbody>{rows}</tbody></table></body></html>""", height=h)


def ui_crosstab(df):
    sts = sorted(df["Connection Status"].unique())
    nets = ["In-network","Out-of-network"]
    hdr = "<th>Connection Status</th>"+"".join(f"<th>{esc(n)}</th>" for n in nets)+"<th>Total</th>"
    rows = ""; ct={n:0 for n in nets}; gt=0
    for s in sts:
        rt=0; c=f"<td>{esc(s)}</td>"
        for n in nets:
            v=len(df[(df["Connection Status"]==s)&(df["P44 Network"]==n)]); c+=f"<td>{v}"; rt+=v; ct[n]+=v
        gt+=rt; c+=f"<td>{rt}</td>"; rows+=f"<tr>{c}</tr>"
    rows+=f'<tr class="tot"><td>Total</td>{"".join(f"<td>{ct[n]}</td>" for n in nets)}<td>{gt}</td></tr>'
    h = 90 + (len(sts)+1)*43 + 10
    components.html(f"""<html><head>{_css(_PVT,_HDR)}</head><body>
    <div class="sh"><span class="dot"></span>Network × Status Cross-Tab</div>
    <p class="desc">Carrier count by Connection Status and P44 Network</p>
    <table class="pt"><thead><tr>{hdr}</tr></thead><tbody>{rows}</tbody></table></body></html>""", height=h)


def ui_export_cards():
    components.html(f"""<html><head>{_css(_HDR)}<style>
    .cards{{display:flex;gap:20px}}
    .cd{{flex:1;border:1px solid #E2E8F0;border-radius:16px;padding:1.8rem;background:#fff;box-shadow:0 1px 4px rgba(0,0,0,.04)}}
    .ci{{width:48px;height:48px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.3rem;margin-bottom:.8rem}}
    .cd h4{{color:#0F172A;font-size:1rem;margin-bottom:.3rem}}
    .cd p{{color:#64748B;font-size:.85rem;line-height:1.5}}
    </style></head><body>
    <div class="sh"><span class="dot"></span>Export Consolidated Report</div>
    <div class="cards">
      <div class="cd"><div class="ci" style="background:#D1FAE5">📗</div><h4>Excel Report</h4><p>Three sheets: Carrier List, Status Pivot, and Network × Status cross-tab.</p></div>
      <div class="cd"><div class="ci" style="background:#EEF2FF">🌐</div><h4>HTML Report</h4><p>Styled standalone HTML report with carrier table and pivot summaries.</p></div>
    </div></body></html>""", height=220)


def ui_landing():
    components.html(f"""<html><head>{_css()}<style>
    body{{background:radial-gradient(ellipse at 20% 50%,rgba(79,76,243,.06) 0%,transparent 50%),
    radial-gradient(ellipse at 80% 50%,rgba(0,114,236,.06) 0%,transparent 50%),
    radial-gradient(ellipse at 50% 0%,rgba(2,28,107,.04) 0%,transparent 60%),#fff!important;
    display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:340px;padding:2rem;text-align:center}}
    .logo{{width:80px;height:80px;background:linear-gradient(135deg,#021c6b,#4F4CF3);border-radius:20px;
    display:flex;align-items:center;justify-content:center;font-size:2.2rem;margin-bottom:1.8rem;box-shadow:0 12px 40px rgba(2,28,107,.2)}}
    h1{{font-size:2.4rem;font-weight:800;color:#021c6b;letter-spacing:-.03em;margin-bottom:.4rem}}
    .sub{{font-size:1.05rem;color:#64748B;margin-bottom:1.5rem}}
    .tags{{display:flex;gap:6px;justify-content:center}}
    .tag{{background:rgba(79,76,243,.1);color:#4F4CF3;font-size:.72rem;font-weight:600;padding:3px 10px;border-radius:20px}}
    .feats{{display:flex;gap:2.5rem;margin-top:2rem}}
    .f{{text-align:center}}.fi{{font-size:1.4rem;margin-bottom:.3rem}}.fl{{font-size:.78rem;color:#64748B;font-weight:500}}
    </style></head><body>
    <div class="logo">🔗</div><h1>Connection Accelerator</h1>
    <p class="sub">Upload p44 Connection Center HTML exports to analyze carrier connections</p>
    <div class="tags"><span class="tag">.HTML</span><span class="tag">.HTM</span><span class="tag">MULTIPLE FILES</span></div>
    <div class="feats">
      <div class="f"><div class="fi">📊</div><div class="fl">Extract & Consolidate</div></div>
      <div class="f"><div class="fi">🔍</div><div class="fl">Pivot Analysis</div></div>
      <div class="f"><div class="fi">💾</div><div class="fl">Export Excel & HTML</div></div>
    </div></body></html>""", height=400)


def ui_file_chips(info):
    chips = "".join(f'<div class="ch"><span class="chi">📄</span><span class="chn">{esc(f)}</span><span class="chc">{c} carriers</span></div>' for f,c in info)
    components.html(f"""<html><head>{_css()}<style>
    .ch{{display:flex;align-items:center;gap:10px;background:#F8F9FC;border:1px solid #E2E8F0;border-radius:10px;padding:10px 14px;margin-bottom:8px}}
    .chi{{font-size:1.1rem}}.chn{{flex:1;font-weight:500;color:#0F172A;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
    .chc{{background:#EEF2FF;color:#4F4CF3;font-size:.72rem;font-weight:700;padding:2px 8px;border-radius:12px}}
    </style></head><body>{chips}</body></html>""", height=len(info)*50+8)


# ═════════════════════════════════════════════════════════════════════════
# STATE
# ═════════════════════════════════════════════════════════════════════════
if "carriers" not in st.session_state: st.session_state.carriers = []
if "files" not in st.session_state: st.session_state.files = {}
if "page" not in st.session_state: st.session_state.page = "landing"


# ═════════════════════════════════════════════════════════════════════════
# LANDING
# ═════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":
    ui_landing()
    _,mid,_ = st.columns([1,2,1])
    with mid:
        ups = st.file_uploader("Upload HTML files", type=["html","htm"], accept_multiple_files=True,
                               help="p44 Movement → Network → Connection Center")
        if ups:
            for u in ups:
                if u.name not in st.session_state.files:
                    st.session_state.files[u.name] = u.read().decode("utf-8", errors="ignore")
            fi = [(f, len(parse_html(c,f))) for f,c in st.session_state.files.items()]
            if fi: ui_file_chips(fi)
            n = len(st.session_state.files)
            if st.button(f"🔍  Analyze {n} File{'s' if n>1 else ''}", type="primary", use_container_width=True):
                st.session_state.carriers = [c for f,h in st.session_state.files.items() for c in parse_html(h,f)]
                st.session_state.page = "dashboard"; st.rerun()


# ═════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "dashboard":
    df = pd.DataFrame(st.session_state.carriers)
    total = len(df)
    inn = len(df[df["P44 Network"]=="In-network"]) if not df.empty else 0
    out = total - inn

    ui_topbar(len(st.session_state.files), total)

    if st.button("← Upload More"):
        st.session_state.page = "landing"; st.session_state.files = {}; st.session_state.carriers = []; st.rerun()

    ui_kpis(total, inn, out)

    t1, t2, t3 = st.tabs(["📋 Carrier Table", "📊 Pivot Analysis", "💾 Export"])

    with t1:
        ui_legend()
        c1, c2, c3 = st.columns([1,1,2])
        with c1: nf = st.selectbox("P44 NETWORK", ["All","In-network","Out-of-network"])
        with c2:
            opts = (["All"]+sorted(df["Connection Status"].unique().tolist())) if not df.empty else ["All"]
            sf = st.selectbox("CONNECTION STATUS", opts)
        with c3: sq = st.text_input("SEARCH CARRIER", placeholder="Type to search…")
        filt = df.copy()
        if nf != "All": filt = filt[filt["P44 Network"]==nf]
        if sf != "All": filt = filt[filt["Connection Status"]==sf]
        if sq: filt = filt[filt["Carrier Name"].str.lower().str.contains(sq.lower(), na=False)]
        ui_carrier_table(filt, total)

    with t2:
        ui_pivot(df)
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        ui_crosstab(df)

    with t3:
        ui_export_cards()
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("⬇  Download Excel Report", make_excel(df),
                "connection_accelerator_report.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True, type="primary")
        with c2:
            st.download_button("⬇  Download HTML Report", make_html_report(df),
                "connection_accelerator_report.html", "text/html",
                use_container_width=True, type="primary")
