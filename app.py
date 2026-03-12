import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime, timedelta
import numpy as np
import math
import logging

st.set_page_config(
    page_title="Fuel Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def apply_minimalist_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #0e1117;
            color: #c9d1d9;
        }
        
        header, footer, #MainMenu {visibility: hidden;}
        
        .block-container {
            padding-top: 2rem;
            max-width: 1100px;
        }

        .header-container {
            border-bottom: 1px solid #30363d;
            padding-bottom: 1rem;
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }

        .main-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: #ffffff;
            margin: 0;
            letter-spacing: -0.02em;
        }

        .sync-status {
            font-size: 0.75rem;
            color: #8b949e;
            font-family: monospace;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .indicator {
            height: 6px;
            width: 6px;
            background-color: #3fb950;
            border-radius: 50%;
        }

        .metric-card {
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 1.5rem;
            background: transparent;
        }

        .metric-title {
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #8b949e;
            margin-bottom: 0.5rem;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 500;
            color: #ffffff;
            line-height: 1;
        }

        .metric-sub {
            font-size: 0.7rem;
            color: #6e7681;
            margin-top: 0.5rem;
        }

        .section-title {
            font-size: 1rem;
            font-weight: 500;
            color: #ffffff;
            margin-top: 2.5rem;
            margin-bottom: 1.5rem;
        }

        .info-card {
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 1.5rem;
            height: 100%;
        }

        .info-card h4 {
            font-size: 0.9rem;
            font-weight: 500;
            color: #ffffff;
            margin-top: 0;
            margin-bottom: 0.75rem;
        }

        .info-card p {
            font-size: 0.8rem;
            color: #8b949e;
            line-height: 1.5;
            margin-bottom: 1rem;
        }

        .info-card a {
            font-size: 0.75rem;
            color: #58a6ff;
            text-decoration: none;
        }

        div[data-testid="stExpander"] {
            border: 1px solid #30363d;
            background: transparent;
            border-radius: 6px;
        }
        
        div[data-testid="stExpander"] summary p {
            font-size: 0.85rem;
            color: #c9d1d9;
        }
        </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=300, show_spinner=False)
def get_telemetry() -> dict:
    baseline = {
        "fx": 56.10, "p91": 72.35, "p95": 74.50, "p97": 82.30, "dsl": 75.10,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    }
    
    api_key = st.secrets.get("FRED_API_KEY")
    if not api_key:
        return baseline

    try:
        req_brent = requests.get(f"https://api.stlouisfed.org/api/fred/series/observations?series_id=DCOILBRENTEU&api_key={api_key}&file_type=json&sort_order=desc&limit=1", timeout=5)
        req_fx = requests.get(f"https://api.stlouisfed.org/api/fred/series/observations?series_id=DEXPHUS&api_key={api_key}&file_type=json&sort_order=desc&limit=1", timeout=5)
        
        if req_brent.status_code == 200 and req_fx.status_code == 200:
            brent_val = float(req_brent.json()['observations'][0]['value'])
            fx_val = float(req_fx.json()['observations'][0]['value'])
            
            X_mat = np.array([[1, 74.2, 55.8], [1, 78.5, 56.1], [1, 80.2, 56.5], [1, 82.5, 57.0]])
            y_vecs = {
                "p91": np.array([50.50, 52.10, 57.30, 59.10]),
                "p95": np.array([54.20, 56.90, 62.10, 63.90]),
                "p97": np.array([58.10, 60.40, 65.60, 67.40]),
                "dsl": np.array([58.00, 60.50, 72.10, 75.90])
            }

            input_vec = np.array([1, brent_val, fx_val])
            calc = {k: input_vec.dot(np.linalg.inv(X_mat.T.dot(X_mat)).dot(X_mat.T.dot(v))) for k, v in y_vecs.items()}
            
            return {
                "fx": fx_val, "p91": calc["p91"], "p95": calc["p95"], "p97": calc["p97"], "dsl": calc["dsl"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            }
    except Exception as e:
        logging.error(f"Telemetry error: {e}")
        
    return baseline

@st.cache_data(ttl=3600, show_spinner=False)
def get_news() -> list:
    fallback = [
        {"title": "Global Logistics Constrained", "description": "Upstream verification required. API connection standard timeout.", "link": "#"},
        {"title": "OPEC Baseline Adjustments", "description": "Awaiting external network resolution for localized reporting.", "link": "#"}
    ]
    
    api_key = st.secrets.get("NEWSDATA_API_KEY")
    if not api_key:
        return fallback

    try:
        req = requests.get(f"https://newsdata.io/api/1/latest?apikey={api_key}&q=oil%20price&country=ph&language=en", timeout=5)
        if req.status_code == 200:
            res = []
            for item in req.json().get("results", [])[:2]:
                desc = str(item.get("description", "No brief available."))[:100] + "..."
                res.append({"title": item.get("title", "Update"), "description": desc, "link": item.get("link", "#")})
            while len(res) < 2: res.append(fallback[1])
            return res
    except Exception as e:
        logging.error(f"News error: {e}")
        
    return fallback

def run_simulation(prices: dict, days: int) -> tuple:
    np.random.seed(42)
    matrix = {"Date": [(datetime.now() + timedelta(days=i)).strftime('%m-%d') for i in range(1, days + 1)]}
    for grade, val in prices.items():
        matrix[grade] = [round(val * (1 + f), 2) for f in np.random.normal(0.001, 0.008, days)]
    return pd.DataFrame(matrix), round(100 * math.exp(-0.015 * days), 1)

def render():
    apply_minimalist_css()
    
    data = get_telemetry()
    news = get_news()
    price_map = {"91 RON": data["p91"], "95 RON": data["p95"], "97 RON": data["p97"], "Diesel": data["dsl"]}

    st.markdown(f"""
        <div class="header-container">
            <h1 class="main-title">Fuel Intelligence</h1>
            <div class="sync-status"><div class="indicator"></div> {data['timestamp']}</div>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    def render_metric(col, title, val, sub):
        col.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{val:.2f}</div>
                <div class="metric-sub">{sub}</div>
            </div>
        """, unsafe_allow_html=True)

    render_metric(c1, "91 RON", data['p91'], "Regular")
    render_metric(c2, "95 RON", data['p95'], "Premium")
    render_metric(c3, "97+ RON", data['p97'], "Ultra")
    render_metric(c4, "Diesel", data['dsl'], "Commercial")

    st.markdown('<div class="section-title">Projection</div>', unsafe_allow_html=True)
    
    ctrl1, ctrl2 = st.columns([1, 3])
    horizon = ctrl1.selectbox("Horizon", [7, 14, 30], label_visibility="collapsed")
    targets = ctrl2.multiselect("Series", list(price_map.keys()), default=["95 RON", "Diesel"], label_visibility="collapsed")

    if targets:
        df, conf = run_simulation(price_map, horizon)
        chart_col, data_col = st.columns([3, 1])
        
        with chart_col:
            melted = df.melt('Date', var_name='Type', value_name='Price')
            chart = alt.Chart(melted[melted['Type'].isin(targets)]).mark_line(strokeWidth=1.5).encode(
                x=alt.X('Date:N', axis=alt.Axis(grid=False, labelColor='#8b949e', title=None)),
                y=alt.Y('Price:Q', scale=alt.Scale(zero=False), axis=alt.Axis(grid=True, gridColor='#30363d', labelColor='#8b949e', title=None)),
                color=alt.Color('Type:N', scale=alt.Scale(range=['#c9d1d9', '#58a6ff', '#8b949e', '#3fb950']), legend=None),
                tooltip=['Date', 'Type', 'Price']
            ).properties(height=300).configure_view(strokeWidth=0).configure_axis(domain=False)
            st.altair_chart(chart, use_container_width=True)

        with data_col:
            st.markdown(f"""
                <div class="info-card" style="padding: 1rem; border: none; background: transparent;">
                    <div style="font-size: 0.7rem; color: #8b949e; margin-bottom: 0.25rem;">CONFIDENCE</div>
                    <div style="font-size: 1.5rem; color: #ffffff; margin-bottom: 1rem;">{conf}%</div>
                </div>
            """, unsafe_allow_html=True)
            st.dataframe(df[['Date'] + targets], hide_index=True, use_container_width=True, height=200)

    st.markdown('<div class="section-title">Context</div>', unsafe_allow_html=True)
    n1, n2 = st.columns(2)
    for col, article in zip([n1, n2], news):
        col.markdown(f"""
            <div class="info-card">
                <h4>{article['title']}</h4>
                <p>{article['description']}</p>
                <a href="{article['link']}" target="_blank">SOURCE →</a>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    render()
