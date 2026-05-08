# 🔗 Connection Accelerator

Analyze p44 Connection Center HTML exports to consolidate and visualize carrier connection data.

## Features

- **Upload & Parse** — Drop one or more Connection Center HTML exports
- **KPI Dashboard** — Total, In-Network, and Out-of-Network carrier counts
- **Carrier Table** — Filter by network, connection status, or search by name
- **Pivot Analysis** — Status pivot and Network × Status cross-tab
- **Export** — Download Excel (3-sheet) or styled HTML report

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set **Main file path** to `app.py`
5. Click **Deploy**

## Tech Stack

- Python 3.9+
- Streamlit
- Pandas
- BeautifulSoup4
- XlsxWriter
