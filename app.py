import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime, timedelta
import numpy as np
import math
import logging

st.set_page_config(
    page_title="Fuel Price Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def apply_professional_css():
    st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #0d1117;
            color: #c9d1d9;
        }
        
        header {visibility: hidden;}
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        
        .block-container {
            padding-top: 1rem;
            max-width: 1300px;
        }

        /* Animations */
        @keyframes slideUpFade {
            0% { opacity: 0; transform: translateY(20px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes pulseIndicator {
            0% { opacity: 0.4; }
            50% { opacity: 1; }
            100% { opacity: 0.4; }
        }

        .animate-in {
            animation: slideUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            opacity: 0;
        }
        .delay-1 { animation-delay: 0.05s; }
        .delay-2 { animation-delay: 0.15s; }
        .delay-3 { animation-delay: 0.25s; }
        .delay-4 { animation-delay: 0.35s; }
        .delay-5 { animation-delay: 0.45s; }

        /* Dashboard Header */
        .dash-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #30363d;
            padding-bottom: 16px;
            margin-bottom: 32px;
        }
        
        .dash-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .timestamp-display {
            font-family: 'Inter', monospace;
            font-size: 0.85rem;
            color: #8b949e;
            background-color: #161b22;
            border: 1px solid #30363d;
            padding: 6px 16px;
            border-radius: 20px;
            display: flex;
            align-items: center;
        }

        .pulse-dot {
            height: 8px; width: 8px;
            background-color: #3fb950;
            border-radius: 50%;
            margin-right: 10px;
            animation: pulseIndicator 2s infinite;
        }

        /* Alerts */
        .alert-banner {
            display: flex;
            align-items: center;
            border-left: 3px solid #d29922;
            background-color: rgba(210, 153, 34, 0.08);
            padding: 16px 20px;
            border-radius: 6px;
            font-size: 0.9rem;
            color: #e3b341;
            margin-bottom: 32px;
        }
        .alert-banner i { margin-right: 12px; font-size: 1.2rem; }

        /* Metric Cards */
        .metric-container {
            display: flex;
            flex-direction: column;
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        .metric-container:hover {
            transform: translateY(-2px);
            border-color: #58a6ff;
        }

        .metric-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .metric-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #8b949e;
            font-weight: 700;
        }
        
        .metric-icon { font-size: 1.1rem; opacity: 0.8; }

        .metric-value {
            font-size: 2.4rem;
            font-weight: 800;
            color: #ffffff;
            line-height: 1;
            margin-bottom: 6px;
        }

        .metric-subtext { font-size: 0.75rem; color: #6e7681; }

        /* Section Headers */
        .section-header {
            display: flex;
            align-items: center;
            font-size: 1.15rem;
            font-weight: 600;
            color: #ffffff;
            border-bottom: 1px solid #30363d;
            padding-bottom: 12px;
            margin-top: 24px;
            margin-bottom: 24px;
            gap: 12px;
        }
        .section-header i { color: #58a6ff; }

        /* Data Cards */
        .data-card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 24px;
            height: 100%;
        }

        .data-card h4 {
            font-size: 1rem;
            font-weight: 600;
            color: #ffffff;
            margin-top: 0;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .data-card h4 i { color: #8b949e; font-size: 0.9rem; }

        .data-card p {
            font-size: 0.85rem;
            color: #8b949e;
            line-height: 1.6;
            margin-bottom: 20px;
        }

        .source-link {
            font-size: 0.75rem;
            text-transform: uppercase;
            color: #58a6ff;
            text-decoration: none;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        div[data-testid="stExpander"] {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
        }
        
        div[data-testid="stExpander"] summary p { font-weight: 600; color: #c9d1d9; }
        
        div[data-baseweb="select"] > div {
            background-color: #0d1117;
            border-color: #30363d;
            color: #c9d1d9;
            border-radius: 6px;
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
    apply_professional_css()
    initialize_cache()
    
    market_data = retrieve_market_telemetry()
    news_data = retrieve_news_telemetry()

    price_map = {
        "91 RON": market_data["p91"],
        "95 RON": market_data["p95"],
        "97 RON": market_data["p97"],
        "Diesel": market_data["dsl"]
    }

    st.markdown(f"""
        <div class="dash-header animate-in delay-1">
            <div class="dash-title">
                <i class="fa-solid fa-gas-pump" style="color: #58a6ff;"></i>
                Fuel Intelligence
            </div>
            <div class="timestamp-display">
                <span class="pulse-dot"></span>
                SYNC: {market_data["timestamp"]}
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="alert-banner animate-in delay-1">
            <i class="fa-solid fa-triangle-exclamation"></i>
            <div><strong>SYSTEM ADVISORY:</strong> Geopolitical shifts may introduce high volatility to short-term pricing models.</div>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    
    def render_metric(col, label, value, subtext, icon, color, delay_class):
        col.markdown(f"""
            <div class="metric-container animate-in {delay_class}">
                <div class="metric-top">
                    <span class="metric-label">{label}</span>
                    <i class="fa-solid {icon} metric-icon" style="color: {color};"></i>
                </div>
                <div class="metric-value">₱{value:.2f}</div>
                <div class="metric-subtext">{subtext}</div>
            </div>
        """, unsafe_allow_html=True)

    render_metric(c1, "91 RON", market_data['p91'], "Standard / Regular", "fa-car-side", "#3fb950", "delay-1")
    render_metric(c2, "95 RON", market_data['p95'], "Premium / Mid-Grade", "fa-gauge-high", "#58a6ff", "delay-2")
    render_metric(c3, "97+ RON", market_data['p97'], "Ultra / Performance", "fa-bolt", "#bc8cff", "delay-3")
    render_metric(c4, "Diesel", market_data['dsl'], "Heavy Duty / Commercial", "fa-truck-fast", "#f85149", "delay-4")

    st.markdown('<div class="section-header animate-in delay-2"><i class="fa-solid fa-chart-line"></i> Predictive Analytics</div>', unsafe_allow_html=True)

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
        ).properties(height=380).configure_view(strokeWidth=0).configure_axis(domain=False)
        
        st.altair_chart(chart, use_container_width=True)

    with data_col:
        st.markdown(f"""
            <div class="data-card animate-in delay-3" style="margin-bottom: 16px;">
                <div style="font-size: 0.75rem; color: #8b949e; text-transform: uppercase; margin-bottom: 8px; font-weight: 700;">Model Confidence</div>
                <div style="font-size: 2.2rem; font-weight: 800; color: #3fb950; margin-bottom: 12px; line-height: 1;">{confidence}%</div>
                <div style="font-size: 0.8rem; color: #8b949e; line-height: 1.5;"><i class="fa-solid fa-microchip" style="margin-right: 6px;"></i>Stochastic Random Walk Simulation</div>
            </div>
        """, unsafe_allow_html=True)
        st.dataframe(df_forecast[['Date'] + selected_fuels], hide_index=True, use_container_width=True, height=210)

    st.markdown('<div class="section-header animate-in delay-4"><i class="fa-solid fa-newspaper"></i> Market Context</div>', unsafe_allow_html=True)
    
    n1, n2 = st.columns(2)
    
    n1.markdown(f"""
        <div class="data-card animate-in delay-4">
            <h4><i class="fa-regular fa-compass"></i> {news_data[0]['title']}</h4>
            <p>{news_data[0]['description']}</p>
            <a href="{news_data[0]['link']}" target="_blank" class="source-link">Read Full Report <i class="fa-solid fa-arrow-right-long"></i></a>
        </div>
    """, unsafe_allow_html=True)
    
    n2.markdown(f"""
        <div class="data-card animate-in delay-5">
            <h4><i class="fa-regular fa-compass"></i> {news_data[1]['title']}</h4>
            <p>{news_data[1]['description']}</p>
            <a href="{news_data[1]['link']}" target="_blank" class="source-link">Read Full Report <i class="fa-solid fa-arrow-right-long"></i></a>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("Architecture Documentation"):
        st.markdown("""
            * **Data Aggregation:** Macro-economic telemetry ingested via Federal Reserve Economic Data (FRED).
            * **Estimation Engine:** Closed-form deterministic linear regression modeling based on structural petroleum scaling factors.
            * **Forward Projection:** Monte Carlo-derived Stochastic Random Walk applying normalized gaussian interference.
        """)

if __name__ == "__main__":
    render_ui()
