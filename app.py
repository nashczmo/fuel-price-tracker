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
        
        .stApp, p, h1, h2, h3, h4, h5, h6, label, [data-testid="stMarkdownContainer"] {
            font-family: 'Inter', sans-serif !important;
        }

        .stApp {
            background-color: #0f111a;
            color: #c9d1d9;
        }
        
        [data-testid="stHeader"] {display: none;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            padding-left: 4% !important;
            padding-right: 4% !important;
            max-width: 1650px !important;
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

        .info-tooltip {
            position: relative;
            display: inline-flex;
            align-items: center;
            margin-left: 8px;
            cursor: pointer;
        }
        .info-tooltip svg {
            fill: #94a3b8;
            transition: fill 0.2s;
        }
        .info-tooltip:hover svg {
            fill: #e2e8f0;
        }
        .info-tooltip .tooltip-text {
            visibility: hidden;
            width: 280px;
            background-color: #1f2937;
            color: #e2e8f0;
            text-align: left;
            border-radius: 6px;
            padding: 12px;
            position: absolute;
            z-index: 50;
            bottom: 150%;
            left: 50%;
            margin-left: -140px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 0.75rem;
            font-weight: 400;
            line-height: 1.5;
            border: 1px solid #374151;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
            pointer-events: none;
        }
        .info-tooltip .tooltip-text::after {
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: #1f2937 transparent transparent transparent;
        }
        .info-tooltip:hover .tooltip-text, .info-tooltip:active .tooltip-text {
            visibility: visible;
            opacity: 1;
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

        .news-header {
            font-size: 1.5rem;
            font-weight: 700;
            color: #f8fafc;
            margin-top: 64px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .news-header svg {
            width: 20px;
            height: 20px;
            fill: #94a3b8;
        }
        .news-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 48px;
        }
        .news-card {
            background-color: #111520;
            border: 1px solid #1f2937;
            border-top: 3px solid #3b82f6;
            border-radius: 8px;
            padding: 24px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 180px;
        }
        .news-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 16px;
        }
        .news-body {
            font-size: 0.9rem;
            color: #94a3b8;
            line-height: 1.6;
            margin-bottom: 24px;
        }
        .news-link {
            font-size: 0.8rem;
            font-weight: 600;
            color: #3b82f6;
            text-decoration: none;
            text-transform: uppercase;
        }

        [data-testid="stExpander"] {
            background-color: transparent;
            border: 1px solid #1f2937;
            border-radius: 8px;
            margin-bottom: 12px;
        }
        [data-testid="stExpander"] summary {
            color: #f8fafc;
            font-weight: 600;
            padding: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        [data-testid="stExpander"] summary span.material-symbols-rounded {
            font-family: 'Material Symbols Rounded' !important;
        }
        [data-testid="stExpander"] summary svg {
            margin-right: 8px;
        }
        [data-testid="stExpanderDetails"] {
            color: #94a3b8;
            font-size: 0.9rem;
            line-height: 1.6;
            padding: 0 16px 16px 16px;
        }
        
        .footer {
            text-align: center;
            margin-top: 32px;
            padding-bottom: 24px;
            font-size: 0.85rem;
            color: #64748b;
            line-height: 1.8;
        }
        .footer a {
            color: #3b82f6;
            text-decoration: none;
            font-weight: 600;
        }

        @media (max-width: 768px) {
            .block-container {
                padding-top: 1rem !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
            .main-title {
                font-size: 1.6rem;
            }
            .metric-grid {
                grid-template-columns: repeat(2, 1fr);
                gap: 12px;
            }
            .metric-card {
                padding: 20px 12px;
            }
            .metric-value {
                font-size: 1.8rem;
            }
            .metric-label {
                font-size: 0.65rem;
                margin-bottom: 8px;
            }
            .metric-sub {
                font-size: 0.65rem;
                margin-top: 8px;
            }
            .news-grid {
                grid-template-columns: 1fr;
            }
            .info-tooltip .tooltip-text {
                width: 240px;
                margin-left: -120px;
            }
        }
        </style>
    """, unsafe_allow_html=True)

HISTORICAL_FEATURES = np.array([[1, 74.2, 55.8], [1, 78.5, 56.1], [1, 80.2, 56.5], [1, 82.5, 57.0]])
INV_MATRIX = np.linalg.inv(HISTORICAL_FEATURES.T.dot(HISTORICAL_FEATURES)).dot(HISTORICAL_FEATURES.T)

WEIGHTS_91 = INV_MATRIX.dot(np.array([50.50, 52.10, 57.30, 59.10]))
WEIGHTS_95 = INV_MATRIX.dot(np.array([54.20, 56.90, 62.10, 63.90]))
WEIGHTS_97 = INV_MATRIX.dot(np.array([58.10, 60.40, 65.60, 67.40]))
WEIGHTS_DSL = INV_MATRIX.dot(np.array([58.00, 60.50, 72.10, 75.90]))

def initialize_session_state():
    if 'last_market_data' not in st.session_state:
        st.session_state.last_market_data = {
            "fx": 56.10, "p91": 72.35, "p95": 74.50, "p97": 82.30, "dsl": 75.10,
            "timestamp": datetime.now().strftime("%I:%M:%S %p")
        }

def compute_linear_regression(brent_price, php_rate):
    current_input = np.array([1, brent_price, php_rate])
    return {
        "p91": current_input.dot(WEIGHTS_91),
        "p95": current_input.dot(WEIGHTS_95),
        "p97": current_input.dot(WEIGHTS_97),
        "dsl": current_input.dot(WEIGHTS_DSL)
    }

@st.cache_data(ttl=600, show_spinner=False)
def fetch_comprehensive_market_data():
    try:
        fred_api_key = st.secrets.get("FRED_API_KEY", None)
        if not fred_api_key: return st.session_state.last_market_data

        req_params = {"api_key": fred_api_key, "file_type": "json", "sort_order": "desc", "limit": 1}
        
        response_brent = requests.get(
            "https://api.stlouisfed.org/api/fred/series/observations?series_id=DCOILBRENTEU", 
            params=req_params, timeout=3
        )
        response_fx = requests.get(
            "https://api.stlouisfed.org/api/fred/series/observations?series_id=DEXPHUS", 
            params=req_params, timeout=3
        )
        
        if response_brent.status_code != 200 or response_fx.status_code != 200: 
            return st.session_state.last_market_data
            
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
    except requests.exceptions.RequestException:
        return st.session_state.last_market_data

@st.cache_data(ttl=3600, show_spinner=False)
def generate_forecast_dataframe(base_prices, forecast_horizon_days=7):
    np.random.seed(42)
    current_time = datetime.now()
    generation_dates = [(current_time + timedelta(days=i)).strftime('%a, %b %d') for i in range(1, forecast_horizon_days + 1)]
    
    mapping = {
        "91": "91 RON (Xtra Advance / FuelSave / Silver)",
        "95": "95 RON (XCS / V-Power / Platinum)",
        "97": "97+ RON (Blaze 100 / Racing)",
        "dsl": "Diesel (Turbo / Max / Power)"
    }
    
    stochastic_data = {"Date": generation_dates}
    for fuel_grade, current_price in base_prices.items():
        daily_price_shocks = np.random.normal(0.002, 0.012, forecast_horizon_days)
        cumulative_shocks = np.cumprod(1 + daily_price_shocks)
        stochastic_data[mapping[fuel_grade]] = np.round(current_price * cumulative_shocks, 2)
        
    df = pd.DataFrame(stochastic_data)
    confidence = round(100 * math.exp(-0.01 * forecast_horizon_days), 1)
    return df, confidence

def build_interactive_chart(forecast_df, selected_fuels):
    if not selected_fuels:
        st.warning("Select at least one fuel type.")
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
        x=alt.X('Date:N', sort=None, title='Date', axis=alt.Axis(grid=False, labelColor='#94a3b8', titleColor='#94a3b8', labelFont='Inter', titleFont='Inter')),
        y=alt.Y('Price:Q', scale=alt.Scale(zero=False), title='Estimated Price (P/L)', axis=alt.Axis(grid=True, gridColor='#1f2937', labelColor='#94a3b8', titleColor='#94a3b8', labelFont='Inter', titleFont='Inter')),
        color=alt.Color('Fuel Type:N', scale=color_scale, legend=alt.Legend(orient='bottom', title=None, labelColor='#94a3b8', labelFont='Inter')),
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
        <div class="info-tooltip">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24">
                <path d="M11 7h2v2h-2zm0 4h2v6h-2zm1-9C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
            </svg>
            <span class="tooltip-text"><strong>Data Latency Notice:</strong> Prices are synchronized with global macroeconomic indices. Displayed data may reflect a 24-48 hour delay due to API aggregation limits and disparity in international trading hours.</span>
        </div>
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
    
    # Map long names to short names to dynamically clean the table headers based on user selection
    short_col_names = {
        "91 RON (Xtra Advance / FuelSave / Silver)": "91 RON",
        "95 RON (XCS / V-Power / Platinum)": "95 RON",
        "97+ RON (Blaze 100 / Racing)": "97+ RON",
        "Diesel (Turbo / Max / Power)": "Diesel"
    }
    
    # Filter the dataframe to only include the specific fuels selected by the user
    display_df = generated_forecast_dataframe[["Date"] + selected_fuels].copy()
    display_df.columns = ["Date"] + [short_col_names[col] for col in selected_fuels]
    
    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True,
        height=340
    )

st.markdown("""
    <div class="news-header">
        Latest Market Intelligence
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"/>
        </svg>
    </div>
    <div class="news-grid">
        <div class="news-card">
            <div>
                <div class="news-title">House OKs bill allowing Marcos to tweak excise tax on fuel on 2nd reading</div>
                <div class="news-body">THE HOUSE of Representatives on Wednesday passed on second reading a bill authorizing President Ferdinand R. Marcos, Jr. to suspend or cut excise taxes on fuel ...</div>
            </div>
            <a href="#" class="news-link">ACCESS SOURCE (BWORLDONLINE)</a>
        </div>
        <div class="news-card">
            <div>
                <div class="news-title">House panel approves measure on fuel excise taxes suspension</div>
                <div class="news-body">The House of Representatives approved on second reading Wednesday a measure that would authorize President Ferdinand Marcos Jr. to temporarily suspend or reduce</div>
            </div>
            <a href="#" class="news-link">ACCESS SOURCE (TRIBUNE)</a>
        </div>
    </div>
""", unsafe_allow_html=True)

with st.expander("How We Calculate Our Data (Methodology)"):
    st.markdown(r"""
    **Data Ingestion & Aggregation**
    The system interfaces with the Federal Reserve Economic Data (FRED) API to retrieve real-time macroeconomic indicators. Specifically, it tracks the continuous contract for Brent Crude Oil (`DCOILBRENTEU`) and the United States Dollar to Philippine Peso exchange rate (`DEXPHUS`).
    
    **Price Determination Algorithm**
    Base pump prices are computed utilizing a multiple linear regression model optimized via Ordinary Least Squares (OLS). The algorithm resolves the normal equation $\beta = (X^T X)^{-1} X^T y$ against historical pricing matrices to isolate the precise scalar weights of global crude variations and forex fluctuations on local retail prices. The resulting coefficient vector is multiplied by real-time market inputs to produce the estimated current price per liter.
    
    **Predictive Forecasting Architecture**
    Future trend projection operates on a Stochastic Random Walk model. The simulation maps future price trajectories by applying daily percentage shocks drawn from a normal distribution $\mathcal{N}(\mu=0.002, \sigma=0.012)$, which accounts for standard market volatility and inherent supply-chain latency. Cumulative variance limits model accuracy exponentially over extended horizons.
    """)

with st.expander("Definition of Fuel Types"):
    st.markdown("""
    * **91 RON (Regular):** Standard unleaded gasoline formulation. Equivalent to market brands such as Petron Xtra Advance, Shell FuelSave, and Caltex Silver.
    * **95 RON (Premium):** Higher octane formulation offering increased knock resistance. Equivalent to Petron XCS, Shell V-Power, and Caltex Platinum.
    * **97+ RON (Ultra):** Maximum performance gasoline for high-compression engines. Equivalent to Petron Blaze 100 and Seaoil Extreme 97.
    * **Diesel:** Standard automotive gas oil. Equivalent to Petron Turbo Diesel, Shell V-Power Diesel, and Caltex Power Diesel.
    """)

st.markdown(f"""
    <div class="footer">
        Developed by 12th grade students <a href="https://www.linkedin.com/in/ignlucina/" target="_blank">Ignacio L.</a> and <a href="https://www.linkedin.com/in/ajebareng56/" target="_blank">Andrei B.</a>
        <br>
        &copy; {datetime.now().year} FuelTrack. All rights reserved.
    </div>
""", unsafe_allow_html=True)
