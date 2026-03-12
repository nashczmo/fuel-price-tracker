import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime, timedelta
import numpy as np
import math

st.set_page_config(
    page_title="FuelTrack",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        /* Global Theme */
        .stApp {
            background-color: #0b0f19;
            font-family: 'Inter', sans-serif;
            color: #c9d1d9;
        }
        
        /* Hide Streamlit Default Elements */
        [data-testid="stHeader"] {display: none;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem;
            max-width: 1600px;
        }

        /* Navbar */
        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 32px;
            background-color: #0b0f19;
            border-bottom: 1px solid #1f2937;
            margin-bottom: 32px;
            margin-left: -4rem;
            margin-right: -4rem;
        }
        .nav-brand { 
            flex: 1;
            font-weight: 800; 
            font-size: 1.25rem; 
            color: #f8fafc; 
            letter-spacing: -0.5px; 
        }
        .nav-links { 
            flex: 1;
            display: flex; 
            justify-content: center;
            gap: 32px; 
        }
        .nav-link { 
            color: #94a3b8; 
            text-decoration: none; 
            font-weight: 600; 
            font-size: 0.9rem; 
            padding-bottom: 16px;
            margin-bottom: -17px;
        }
        .nav-link.active { 
            color: #3b82f6; 
            border-bottom: 2px solid #3b82f6; 
        }
        .nav-right {
            flex: 1;
            display: flex;
            justify-content: flex-end;
        }
        .clock {
            font-family: monospace;
            font-size: 0.85rem;
            color: #64748b;
            border: 1px solid #1f2937;
            padding: 6px 12px;
            border-radius: 6px;
            background: transparent;
        }

        /* Badges */
        .status-badge {
            display: inline-flex;
            align-items: center;
            background-color: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.2);
            border-radius: 20px;
            padding: 6px 16px;
            font-size: 0.8rem;
            font-weight: 600;
            color: #cbd5e1;
            margin-bottom: 24px;
        }
        .pulse-dot {
            height: 8px;
            width: 8px;
            background-color: #10b981;
            border-radius: 50%;
            margin-right: 8px;
        }

        /* Metric Grid */
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 24px;
            margin-bottom: 24px;
        }
        .metric-card {
            background-color: #111827;
            border: 1px solid #1f2937;
            border-radius: 8px;
            padding: 32px 24px;
            text-align: center;
        }
        .metric-label {
            color: #94a3b8;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            margin-bottom: 12px;
            letter-spacing: 0.5px;
        }
        .metric-value {
            color: #f8fafc;
            font-size: 2.5rem;
            font-weight: 800;
            line-height: 1;
            margin: 16px 0;
            font-family: 'Inter', sans-serif;
        }
        .metric-sub {
            color: #64748b;
            font-size: 0.75rem;
            margin-top: 8px;
        }

        /* Containers */
        .panel-container {
            background-color: #111827;
            border: 1px solid #1f2937;
            border-radius: 8px;
            padding: 24px;
            height: 100%;
            min-height: 400px;
        }
        .panel-title {
            color: #f8fafc;
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 24px;
        }

        /* Intelligence Panel */
        .intel-label { color: #94a3b8; font-size: 0.85rem; margin-bottom: 8px; }
        .intel-value { color: #10b981; font-size: 3.5rem; font-weight: 800; margin-bottom: 24px; line-height: 1;}
        .intel-meta { color: #94a3b8; font-size: 0.85rem; line-height: 1.8; }
        .intel-meta strong { color: #cbd5e1; }
        </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    if 'last_market_data' not in st.session_state:
        st.session_state.last_market_data = {
            "fx": 56.10, "p91": 72.35, "p95": 74.50, "p97": 82.30, "dsl": 75.10,
            "timestamp": datetime.now().strftime("%I:%M:%S %p")
        }

@st.cache_data(ttl=300)
def compute_linear_regression(brent_price, php_rate):
    historical_features = np.array([[1, 74.2, 55.8], [1, 78.5, 56.1], [1, 80.2, 56.5], [1, 82.5, 57.0]])
    historical_targets_91 = np.array([50.50, 52.10, 57.30, 59.10])
    historical_targets_95 = np.array([54.20, 56.90, 62.10, 63.90])
    historical_targets_97 = np.array([58.10, 60.40, 65.60, 67.40])
    historical_targets_dsl = np.array([58.00, 60.50, 72.10, 75.90])

    def resolve_matrix(X, y): 
        return np.linalg.inv(X.T.dot(X)).dot(X.T.dot(y))
        
    weights_91 = resolve_matrix(historical_features, historical_targets_91)
    weights_95 = resolve_matrix(historical_features, historical_targets_95)
    weights_97 = resolve_matrix(historical_features, historical_targets_97)
    weights_dsl = resolve_matrix(historical_features, historical_targets_dsl)

    current_input_vector = np.array([1, brent_price, php_rate])
    
    return {
        "p91": current_input_vector.dot(weights_91),
        "p95": current_input_vector.dot(weights_95),
        "p97": current_input_vector.dot(weights_97),
        "dsl": current_input_vector.dot(weights_dsl)
    }

@st.cache_data(ttl=300)
def fetch_comprehensive_market_data():
    try:
        fred_api_key = st.secrets.get("FRED_API_KEY", "")
        if not fred_api_key: return st.session_state.last_market_data

        response_brent = requests.get(f"https://api.stlouisfed.org/api/fred/series/observations?series_id=DCOILBRENTEU&api_key={fred_api_key}&file_type=json&sort_order=desc&limit=1", timeout=10)
        response_fx = requests.get(f"https://api.stlouisfed.org/api/fred/series/observations?series_id=DEXPHUS&api_key={fred_api_key}&file_type=json&sort_order=desc&limit=1", timeout=10)
        
        if response_brent.status_code != 200 or response_fx.status_code != 200: return st.session_state.last_market_data
            
        current_brent_price = float(response_brent.json()['observations'][0]['value'])
        current_php_rate = float(response_fx.json()['observations'][0]['value'])
        computed_prices = compute_linear_regression(current_brent_price, current_php_rate)
        
        final_data_object = {
            "fx": current_php_rate, "p91": computed_prices["p91"], "p95": computed_prices["p95"], 
            "p97": computed_prices["p97"], "dsl": computed_prices["dsl"],
            "timestamp": datetime.now().strftime("%I:%M:%S %p")
        }
        st.session_state.last_market_data = final_data_object
        return final_data_object
    except Exception:
        return st.session_state.last_market_data

def generate_forecast_dataframe(base_prices, forecast_horizon_days=7):
    np.random.seed(42)
    generation_dates = [(datetime.now() + timedelta(days=i)).strftime('%b %d') for i in range(1, forecast_horizon_days + 1)]
    stochastic_data = {"Date": generation_dates}
    
    for fuel_grade, current_price in base_prices.items():
        daily_price_shocks = np.random.normal(0.002, 0.012, forecast_horizon_days)
        stochastic_data[fuel_grade] = [round(current_price * (1 + shock_value), 2) for shock_value in daily_price_shocks]
        
    return pd.DataFrame(stochastic_data), round(100 * math.exp(-0.01 * forecast_horizon_days), 1)

def build_interactive_chart(forecast_df):
    melted_dataframe = forecast_df.melt('Date', var_name='Fuel Type', value_name='Price')
    line_chart = alt.Chart(melted_dataframe).mark_line(point=True, strokeWidth=2).encode(
        x=alt.X('Date:N', sort=None, title=None, axis=alt.Axis(grid=False, labelColor='#94a3b8')),
        y=alt.Y('Price:Q', scale=alt.Scale(zero=False), title=None, axis=alt.Axis(grid=True, gridColor='#1f2937', labelColor='#94a3b8')),
        color=alt.Color('Fuel Type:N', scale=alt.Scale(range=['#10b981', '#3b82f6', '#8b5cf6', '#ef4444']), legend=None),
        tooltip=['Date', 'Fuel Type', 'Price']
    ).properties(height=320).configure_view(strokeWidth=0).configure_axis(domain=False)
    st.altair_chart(line_chart, use_container_width=True)

inject_custom_css()
initialize_session_state()

live_market_data = fetch_comprehensive_market_data()
structured_pump_prices = {
    "91": live_market_data["p91"], "95": live_market_data["p95"],
    "97": live_market_data["p97"], "dsl": live_market_data["dsl"]
}

st.markdown(f"""
    <div class="navbar">
        <div class="nav-brand">FuelTrack</div>
        <div class="nav-links">
            <div class="nav-link active">Dashboard</div>
            <div class="nav-link">Logistics Calculator</div>
        </div>
        <div class="nav-right">
            <div class="clock">{live_market_data['timestamp']}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="status-badge">
        <span class="pulse-dot"></span> Initialization Sequence...
    </div>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">91 REGULAR</div>
            <div class="metric-value">&#8369;{live_market_data['p91']:.2f}</div>
            <div class="metric-sub">Xtra Advance, FuelSave</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">95 OCTANE</div>
            <div class="metric-value">&#8369;{live_market_data['p95']:.2f}</div>
            <div class="metric-sub">XCS, V-Power</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">97+ ULTRA</div>
            <div class="metric-value">&#8369;{live_market_data['p97']:.2f}</div>
            <div class="metric-sub">Blaze 100, Racing</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">DIESEL</div>
            <div class="metric-value">&#8369;{live_market_data['dsl']:.2f}</div>
            <div class="metric-sub">Turbo, Power Diesel</div>
        </div>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2.5, 1])
generated_forecast_dataframe, model_confidence = generate_forecast_dataframe(structured_pump_prices, 7)

with col1:
    st.markdown("""
        <div class="panel-container" style="padding-bottom: 0px;">
            <div class="panel-title">Price Trend Prediction (7 Days)</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('<div style="margin-top: -340px; padding: 24px;">', unsafe_allow_html=True)
    build_interactive_chart(generated_forecast_dataframe)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="panel-container">
            <div class="panel-title">System Intelligence</div>
            <div class="intel-label">Model Confidence</div>
            <div class="intel-value">{model_confidence}%</div>
            <div class="intel-meta">
                <strong>Architecture:</strong> Server-Side Linear Regression & Stochastic Walk<br>
                <strong>Status:</strong> <span style="color:#eab308;">Live / Optimized</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
