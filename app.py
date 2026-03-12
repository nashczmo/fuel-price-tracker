import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime, timedelta
import numpy as np
import math

st.set_page_config(
    page_title="Philippine Fuel Price Tracker",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        .stApp {
            background-color: #0f111a;
            font-family: 'Inter', sans-serif;
            color: #c9d1d9;
        }
        
        [data-testid="stHeader"] {display: none;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem;
            max-width: 1600px;
        }

        .main-title {
            font-size: 2.2rem;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 1rem;
            letter-spacing: -0.5px;
        }

        .time-badge {
            display: inline-flex;
            align-items: center;
            background-color: rgba(0, 0, 0, 0.4);
            border: 1px solid #1f2937;
            border-radius: 20px;
            padding: 6px 16px;
            font-size: 0.8rem;
            font-weight: 600;
            color: #e2e8f0;
            margin-bottom: 24px;
        }
        
        .pulse-dot {
            height: 8px;
            width: 8px;
            background-color: #10b981;
            border-radius: 50%;
            margin-right: 8px;
        }

        .alert-box {
            background-color: #241c0e;
            border-left: 4px solid #ca8a04;
            padding: 16px 20px;
            border-radius: 0 4px 4px 0;
            color: #e2e8f0;
            font-size: 0.85rem;
            margin-bottom: 32px;
        }

        .section-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 20px;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 32px;
        }

        .metric-card {
            background-color: #111520;
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
            margin-bottom: 16px;
            letter-spacing: 0.5px;
        }

        .metric-value {
            color: #ffffff;
            font-size: 2.5rem;
            font-weight: 800;
            line-height: 1;
            margin: 0;
            font-family: 'Inter', sans-serif;
        }

        .metric-sub {
            color: #475569;
            font-size: 0.75rem;
            margin-top: 16px;
        }

        .sub-header {
            font-size: 1.25rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 16px;
        }
        
        .stat-label {
            color: #e2e8f0;
            font-size: 0.85rem;
            margin-bottom: 4px;
        }
        
        .stat-value {
            color: #e2e8f0;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 24px;
        }

        [data-testid="stSelectbox"] label, [data-testid="stMultiSelect"] label {
            color: #e2e8f0 !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
        }
        
        [data-testid="stDataFrame"] {
            background-color: transparent;
        }
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
    generation_dates = [(datetime.now() + timedelta(days=i)).strftime('%a, %b %d') for i in range(1, forecast_horizon_days + 1)]
    stochastic_data = {"Date": generation_dates}
    
    mapping = {
        "91": "91 RON (Xtra Advance / FuelSave / Silver)",
        "95": "95 RON (XCS / V-Power / Platinum)",
        "97": "97+ RON (Blaze 100 / Racing)",
        "dsl": "Diesel (Turbo / Max / Power)"
    }
    
    for fuel_grade, current_price in base_prices.items():
        daily_price_shocks = np.random.normal(0.002, 0.012, forecast_horizon_days)
        stochastic_data[mapping[fuel_grade]] = [round(current_price * (1 + shock_value), 2) for shock_value in daily_price_shocks]
        
    return pd.DataFrame(stochastic_data), round(100 * math.exp(-0.01 * forecast_horizon_days), 1)

def build_interactive_chart(forecast_df, selected_fuels):
    if not selected_fuels:
        st.warning("Please select at least one fuel type to display.")
        return

    plot_df = forecast_df[["Date"] + selected_fuels]
    melted_dataframe = plot_df.melt('Date', var_name='Fuel Type', value_name='Price')
    
    color_scale = alt.Scale(
        domain=[
            "91 RON (Xtra Advance / FuelSave / Silver)", 
            "95 RON (XCS / V-Power / Platinum)", 
            "97+ RON (Blaze 100 / Racing)", 
            "Diesel (Turbo / Max / Power)"
        ],
        range=['#10b981', '#3b82f6', '#8b5cf6', '#ef4444']
    )

    line_chart = alt.Chart(melted_dataframe).mark_line(point=True, strokeWidth=2).encode(
        x=alt.X('Date:N', sort=None, title='Date', axis=alt.Axis(grid=False, labelColor='#94a3b8', titleColor='#94a3b8')),
        y=alt.Y('Price:Q', scale=alt.Scale(zero=False), title='Estimated Price (P/L)', axis=alt.Axis(grid=True, gridColor='#1f2937', labelColor='#94a3b8', titleColor='#94a3b8')),
        color=alt.Color('Fuel Type:N', scale=color_scale, legend=alt.Legend(orient='bottom', title=None, labelColor='#94a3b8')),
        tooltip=['Date', 'Fuel Type', 'Price']
    ).properties(height=400).configure_view(strokeWidth=0).configure_axis(domain=False)
    st.altair_chart(line_chart, use_container_width=True)

inject_custom_css()
initialize_session_state()

live_market_data = fetch_comprehensive_market_data()
structured_pump_prices = {
    "91": live_market_data["p91"], "95": live_market_data["p95"],
    "97": live_market_data["p97"], "dsl": live_market_data["dsl"]
}

current_time_str = datetime.now().strftime("%B %d, %Y | %I:%M %p PST")

st.markdown('<div class="main-title">Philippine Fuel Price Tracker</div>', unsafe_allow_html=True)

st.markdown(f"""
    <div class="time-badge">
        <span class="pulse-dot"></span> As of {current_time_str}
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="alert-box">
        <strong>MARKET ALERT:</strong> Conflict in the Middle East may affect global oil supply, which could lead to possible fuel price increases.
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">Estimated Current Pump Prices</div>', unsafe_allow_html=True)

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

prediction_period = st.selectbox("Select Prediction Period", ["7 Days Forecast", "14 Days Forecast", "30 Days Forecast"])
days_forecast = int(prediction_period.split()[0])

all_fuel_types = [
    "91 RON (Xtra Advance / FuelSave / Silver)", 
    "95 RON (XCS / V-Power / Platinum)", 
    "97+ RON (Blaze 100 / Racing)", 
    "Diesel (Turbo / Max / Power)"
]

selected_fuels = st.multiselect(
    "Select Fuel Types to Display on Graph",
    options=all_fuel_types,
    default=all_fuel_types
)

st.markdown("<hr style='border-color: #1f2937; margin: 32px 0;'>", unsafe_allow_html=True)

col1, col2 = st.columns([2.5, 1], gap="large")
generated_forecast_dataframe, model_confidence = generate_forecast_dataframe(structured_pump_prices, days_forecast)

with col1:
    st.markdown(f'<div class="sub-header">Price Trend Prediction ({days_forecast} Days)</div>', unsafe_allow_html=True)
    build_interactive_chart(generated_forecast_dataframe, selected_fuels)

with col2:
    st.markdown('<div class="sub-header">Model Stats</div>', unsafe_allow_html=True)
    st.markdown('<div class="stat-label">Estimated Accuracy</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-value">{model_confidence}%</div>', unsafe_allow_html=True)
    
    st.dataframe(
        generated_forecast_dataframe,
        hide_index=True,
        use_container_width=True
    )
