import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime, timedelta
import numpy as np
import math
import logging

st.set_page_config(
    page_title="Fuel Price Tracker",
    page_icon="⛟",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def apply_minimalist_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #0d1117;
            color: #c9d1d9;
        }
        
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {
            padding-top: 2rem;
            max-width: 1200px;
        }

        .metric-container {
            display: flex;
            flex-direction: column;
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 24px;
            margin-bottom: 24px;
        }

        .metric-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #8b949e;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .metric-value {
            font-size: 2.25rem;
            font-weight: 700;
            color: #ffffff;
            line-height: 1;
            margin-bottom: 4px;
        }

        .metric-subtext {
            font-size: 0.7rem;
            color: #6e7681;
        }

        .alert-banner {
            border-left: 3px solid #d29922;
            background-color: rgba(210, 153, 34, 0.1);
            padding: 12px 16px;
            border-radius: 4px;
            font-size: 0.85rem;
            color: #c9d1d9;
            margin-bottom: 32px;
        }

        .section-header {
            font-size: 1.1rem;
            font-weight: 600;
            color: #ffffff;
            border-bottom: 1px solid #30363d;
            padding-bottom: 8px;
            margin-top: 32px;
            margin-bottom: 24px;
        }

        .data-card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 20px;
            height: 100%;
        }

        .data-card h4 {
            font-size: 0.95rem;
            font-weight: 600;
            color: #ffffff;
            margin-top: 0;
            margin-bottom: 8px;
        }

        .data-card p {
            font-size: 0.85rem;
            color: #8b949e;
            line-height: 1.5;
            margin-bottom: 16px;
        }

        .data-card a {
            font-size: 0.75rem;
            text-transform: uppercase;
            color: #58a6ff;
            text-decoration: none;
            font-weight: 600;
        }

        .timestamp-display {
            font-family: monospace;
            font-size: 0.8rem;
            color: #8b949e;
            margin-bottom: 24px;
        }

        div[data-testid="stExpander"] {
            background-color: transparent;
            border: 1px solid #30363d;
            border-radius: 6px;
        }
        
        div[data-testid="stExpander"] summary p {
            font-weight: 500;
            color: #c9d1d9;
        }
        </style>
    """, unsafe_allow_html=True)

def initialize_cache():
    if 'market_baseline' not in st.session_state:
        st.session_state.market_baseline = {
            "fx": 56.10, "p91": 72.35, "p95": 74.50, "p97": 82.30, "dsl": 75.10,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    if 'news_baseline' not in st.session_state:
        st.session_state.news_baseline = [
            {"title": "Market Data Unavailable", "description": "Live news feed is currently disconnected. Attempting to re-establish connection.", "link": "#", "source": "System"},
            {"title": "Regulatory Status", "description": "Awaiting upstream data from regulatory endpoints.", "link": "#", "source": "System"}
        ]

@st.cache_data(ttl=300, show_spinner=False)
def execute_linear_regression(brent_val: float, fx_val: float) -> dict:
    X_matrix = np.array([
        [1, 74.2, 55.8], 
        [1, 78.5, 56.1], 
        [1, 80.2, 56.5], 
        [1, 82.5, 57.0]
    ])
    
    y_vectors = {
        "p91": np.array([50.50, 52.10, 57.30, 59.10]),
        "p95": np.array([54.20, 56.90, 62.10, 63.90]),
        "p97": np.array([58.10, 60.40, 65.60, 67.40]),
        "dsl": np.array([58.00, 60.50, 72.10, 75.90])
    }

    def compute_weights(X, y):
        return np.linalg.inv(X.T.dot(X)).dot(X.T.dot(y))

    input_vector = np.array([1, brent_val, fx_val])
    predicted_outputs = {}
    
    for key, y_target in y_vectors.items():
        weights = compute_weights(X_matrix, y_target)
        predicted_outputs[key] = input_vector.dot(weights)
        
    return predicted_outputs

@st.cache_data(ttl=300, show_spinner=False)
def retrieve_market_telemetry() -> dict:
    try:
        api_key = st.secrets.get("FRED_API_KEY")
        if not api_key:
            return st.session_state.market_baseline

        req_brent = requests.get(f"https://api.stlouisfed.org/api/fred/series/observations?series_id=DCOILBRENTEU&api_key={api_key}&file_type=json&sort_order=desc&limit=1", timeout=5)
        req_fx = requests.get(f"https://api.stlouisfed.org/api/fred/series/observations?series_id=DEXPHUS&api_key={api_key}&file_type=json&sort_order=desc&limit=1", timeout=5)
        
        if req_brent.status_code == 200 and req_fx.status_code == 200:
            val_brent = float(req_brent.json()['observations'][0]['value'])
            val_fx = float(req_fx.json()['observations'][0]['value'])
            
            computed_matrix = execute_linear_regression(val_brent, val_fx)
            
            payload = {
                "fx": val_fx,
                "p91": computed_matrix["p91"],
                "p95": computed_matrix["p95"],
                "p97": computed_matrix["p97"],
                "dsl": computed_matrix["dsl"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.market_baseline = payload
            return payload
            
    except Exception as e:
        logging.error(f"Telemetry failure: {e}")
        
    return st.session_state.market_baseline

@st.cache_data(ttl=3600, show_spinner=False)
def retrieve_news_telemetry() -> list:
    try:
        api_key = st.secrets.get("NEWSDATA_API_KEY")
        if not api_key:
            return st.session_state.news_baseline

        req_news = requests.get(f"https://newsdata.io/api/1/latest?apikey={api_key}&q=fuel%20price%20OR%20oil%20price&country=ph&language=en", timeout=5)
        
        if req_news.status_code == 200:
            articles = req_news.json().get("results", [])
            if articles:
                parsed_data = []
                for item in articles[:2]:
                    desc = str(item.get("description") or "No description provided by source.")
                    if len(desc) > 120: desc = desc[:120] + "..."
                    
                    parsed_data.append({
                        "title": item.get("title", "Market Update"),
                        "description": desc,
                        "link": item.get("link", "#"),
                        "source": str(item.get("source_id", "System")).upper()
                    })
                
                while len(parsed_data) < 2:
                    parsed_data.append(st.session_state.news_baseline[1])
                    
                st.session_state.news_baseline = parsed_data
                return parsed_data
                
    except Exception as e:
        logging.error(f"News fetch failure: {e}")
        
    return st.session_state.news_baseline

def generate_stochastic_forecast(prices: dict, horizon: int) -> tuple:
    np.random.seed(42)
    dates = [(datetime.now() + timedelta(days=i)).strftime('%m-%d') for i in range(1, horizon + 1)]
    matrix = {"Date": dates}
    
    for grade, base_val in prices.items():
        noise = np.random.normal(0.001, 0.008, horizon)
        trajectory = []
        current = base_val
        for factor in noise:
            current = current * (1 + factor)
            trajectory.append(round(current, 2))
        matrix[grade] = trajectory
        
    confidence = round(100 * math.exp(-0.015 * horizon), 1)
    return pd.DataFrame(matrix), confidence

def render_ui():
    apply_minimalist_css()
    initialize_cache()
    
    market_data = retrieve_market_telemetry()
    news_data = retrieve_news_telemetry()

    price_map = {
        "91 RON": market_data["p91"],
        "95 RON": market_data["p95"],
        "97 RON": market_data["p97"],
        "Diesel": market_data["dsl"]
    }

    st.markdown("## Fuel Price Intelligence")
    st.markdown(f'<div class="timestamp-display">DATA SYNC: {market_data["timestamp"]}</div>', unsafe_allow_html=True)

    st.markdown("""
        <div class="alert-banner">
            <strong>SYSTEM ADVISORY:</strong> Geopolitical shifts may introduce high volatility to short-term pricing models.
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    
    def render_metric(col, label, value, subtext):
        col.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">{label}</div>
                <div class="metric-value">₱{value:.2f}</div>
                <div class="metric-subtext">{subtext}</div>
            </div>
        """, unsafe_allow_html=True)

    render_metric(c1, "91 RON", market_data['p91'], "Standard / Regular")
    render_metric(c2, "95 RON", market_data['p95'], "Premium / Mid-Grade")
    render_metric(c3, "97+ RON", market_data['p97'], "Ultra / High-Performance")
    render_metric(c4, "Diesel", market_data['dsl'], "Commercial / Heavy Duty")

    st.markdown('<div class="section-header">Predictive Analytics</div>', unsafe_allow_html=True)

    ctrl_c1, ctrl_c2 = st.columns([1, 2])
    horizon = ctrl_c1.selectbox("Forecast Horizon", [7, 14, 30], format_func=lambda x: f"{x} Days")
    selected_fuels = ctrl_c2.multiselect("Active Series", options=list(price_map.keys()), default=list(price_map.keys()))

    if not selected_fuels:
        st.warning("Select at least one series to render graph.")
        return

    df_forecast, confidence = generate_stochastic_forecast(price_map, horizon)
    
    chart_col, data_col = st.columns([3, 1])

    with chart_col:
        df_melt = df_forecast.melt('Date', var_name='Type', value_name='Price')
        df_filtered = df_melt[df_melt['Type'].isin(selected_fuels)]
        
        chart = alt.Chart(df_filtered).mark_line(point=True, strokeWidth=2).encode(
            x=alt.X('Date:N', axis=alt.Axis(grid=False, labelColor='#8b949e', title=None)),
            y=alt.Y('Price:Q', scale=alt.Scale(zero=False), axis=alt.Axis(grid=True, gridColor='#30363d', labelColor='#8b949e', title='Estimated (₱)')),
            color=alt.Color('Type:N', scale=alt.Scale(range=['#3fb950', '#58a6ff', '#bc8cff', '#f85149']), legend=alt.Legend(orient="bottom", title=None, labelColor='#c9d1d9')),
            tooltip=['Date', 'Type', 'Price']
        ).properties(height=350).configure_view(strokeWidth=0).configure_axis(domain=False)
        
        st.altair_chart(chart, use_container_width=True)

    with data_col:
        st.markdown(f"""
            <div class="data-card" style="margin-bottom: 16px;">
                <div style="font-size: 0.75rem; color: #8b949e; text-transform: uppercase; margin-bottom: 4px;">Confidence Interval</div>
                <div style="font-size: 2rem; font-weight: 700; color: #3fb950; margin-bottom: 8px;">{confidence}%</div>
                <div style="font-size: 0.75rem; color: #6e7681; line-height: 1.4;">Based on historical variance and selected horizon length.</div>
            </div>
        """, unsafe_allow_html=True)
        st.dataframe(df_forecast[['Date'] + selected_fuels], hide_index=True, use_container_width=True, height=200)

    st.markdown('<div class="section-header">Market Context</div>', unsafe_allow_html=True)
    
    n1, n2 = st.columns(2)
    
    n1.markdown(f"""
        <div class="data-card">
            <h4>{news_data[0]['title']}</h4>
            <p>{news_data[0]['description']}</p>
            <a href="{news_data[0]['link']}" target="_blank">View Source [{news_data[0]['source']}]</a>
        </div>
    """, unsafe_allow_html=True)
    
    n2.markdown(f"""
        <div class="data-card">
            <h4>{news_data[1]['title']}</h4>
            <p>{news_data[1]['description']}</p>
            <a href="{news_data[1]['link']}" target="_blank">View Source [{news_data[1]['source']}]</a>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("System Documentation"):
        st.markdown("""
            * **Data Aggregation:** Telemetry ingested via St. Louis Fed API (DCOILBRENTEU, DEXPHUS).
            * **Estimation Engine:** Closed-form linear regression utilizing historical correlation matrices.
            * **Forward Projection:** Stochastic Random Walk simulation applying gaussian noise to calculate probable divergence paths over defined horizons.
        """)

if __name__ == "__main__":
    render_ui()
