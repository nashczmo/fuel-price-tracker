import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime, timedelta
import numpy as np

# --- 1. Dashboard Configuration & Custom Responsive CSS ---
st.set_page_config(page_title="Fuel Price Tracker", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    .main { background-color: #0e1117; font-family: 'Inter', sans-serif; }
    
    /* Responsive Metric Grid */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 10px;
        margin-bottom: 20px;
    }
    
    .metric-container {
        background-color: #1e222d;
        border: 1px solid #2d3139;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
    
    .metric-label { color: #8e95a2; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 4px; }
    .metric-value { color: #ffffff; font-size: 1.4rem; font-weight: 700; }
    
    /* Card Styles */
    .news-card {
        background-color: #1e222d;
        border: 1px solid #2d3139;
        border-left: 4px solid #3b82f6;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 12px;
    }
    
    .news-card h4 { margin: 0 0 8px 0; font-size: 1rem; color: #ffffff; }
    .news-card p { margin: 0 0 10px 0; font-size: 0.85rem; color: #8e95a2; line-height: 1.4; }
    .news-card a { color: #3b82f6; text-decoration: none; font-weight: 600; font-size: 0.8rem; }
    
    /* Footer */
    .footer-text { color: #8e95a2; font-size: 0.8rem; margin-top: 30px; text-align: center; }
    
    /* Mobile specific adjustments */
    @media (max-width: 640px) {
        .metric-value { font-size: 1.2rem; }
        .stTable { font-size: 0.8rem; }
        .timestamp-text { font-size: 0.8rem; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Data Engine (Optimized for Credit Usage) ---
@st.cache_data(ttl=86400) 
def fetch_market_data():
    try:
        OIL_API_TOKEN = st.secrets["OIL_API_TOKEN"]
    except KeyError:
        return 59.02, 74.50, 75.10, "Config Error"

    try:
        fx_data = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10).json()
        php_rate = fx_data.get('rates', {}).get('PHP', 59.02)
        headers = {"Authorization": f"Token {OIL_API_TOKEN}"}
        oil_url = "https://api.oilpriceapi.com/v1/prices/latest?by_code=GASOLINE_USD,DIESEL_USD"
        oil_res = requests.get(oil_url, headers=headers, timeout=10).json()
        gas_raw, dsl_raw = oil_res['data'][0]['price'], oil_res['data'][1]['price']
        gas_base = ((gas_raw / 158.98) * php_rate * 1.35) + 18.50
        diesel_base = ((dsl_raw / 158.98) * php_rate * 1.35) + 13.50
        return php_rate, gas_base, diesel_base, datetime.now().strftime("%B %d, %Y")
    except Exception:
        return 59.02, 74.50, 75.10, datetime.now().strftime("%B %d, %Y")

def generate_forecast(base_prices, days):
    np.random.seed(42) 
    dates = [(datetime.now() + timedelta(days=i)).strftime('%b %d') for i in range(1, days + 1)]
    data = {"Date": dates}
    for grade, price in base_prices.items():
        data[grade] = [round(price * (1 + np.random.normal(0.002, 0.012)), 2) for _ in range(days)]
    return pd.DataFrame(data), round(100 * np.exp(-0.01 * days), 1)

# --- 3. Responsive UI Execution ---
fx, p95, dsl, last_updated = fetch_market_data()
prices = {"91 Reg": p95 - 2.15, "95 Oct": p95, "97+ Ultra": p95 + 7.80, "Diesel": dsl}

st.title("PH Fuel Price Tracker")
st.caption(f"Price baseline: {last_updated}")

# Metric Grid (HTML/CSS for better mobile wrapping)
st.markdown(f"""
<div class="metric-grid">
    <div class="metric-container"><div class="metric-label">USD/PHP</div><div class="metric-value">₱{fx:.2f}</div></div>
    <div class="metric-container"><div class="metric-label">91 REG</div><div class="metric-value">₱{prices['91 Reg']:.2f}</div></div>
    <div class="metric-container"><div class="metric-label">95 OCT</div><div class="metric-value">₱{prices['95 Oct']:.2f}</div></div>
    <div class="metric-container"><div class="metric-label">97+ ULT</div><div class="metric-value">₱{prices['97+ Ultra']:.2f}</div></div>
    <div class="metric-container"><div class="metric-label">DIESEL</div><div class="metric-value">₱{prices['Diesel']:.2f}</div></div>
</div>
""", unsafe_allow_html=True)

# Prediction Controls
timeframe = st.selectbox("Prediction Period", [7, 15, 30], index=0, format_func=lambda x: f"{x} Day Forecast")
forecast_df, accuracy = generate_forecast(prices, timeframe)

# Chart (Altair is natively responsive)
st.subheader("Forecast Trend")
melted = forecast_df.melt('Date', var_name='Fuel', value_name='Price')
chart = alt.Chart(melted).mark_line(point=True).encode(
    x=alt.X('Date:N', sort=None),
    y=alt.Y('Price:Q', scale=alt.Scale(zero=False)),
    color=alt.Color('Fuel:N', legend=alt.Legend(orient="bottom", columns=2))
).properties(height=300).interactive()
st.altair_chart(chart, use_container_width=True)

# News (Responsive Columns)
st.subheader("News")
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown('<div class="news-card"><h4>Market Updates</h4><p>Global supply remains volatile. Expect minor pump changes.</p><a href="https://www.bworldonline.com" target="_blank">Source</a></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="news-card"><h4>DOE Advisory</h4><p>Staggered price hikes implemented in various regions.</p><a href="https://doe.gov.ph" target="_blank">Advisory</a></div>', unsafe_allow_html=True)

# Methodology (Simplified for Mobile)
with st.expander("Methodology & APA References"):
    st.markdown("""
    **Methodology:** Stochastic Drift Model using normal distribution ($\mu=0.2\%, \sigma=1.2\%$). 
    
    **References (APA 7th):**
    * Department of Energy. (2026). *Fuel price adjustments*. Republic of the Philippines.
    * Oil Price API. (2026). *Energy price datasets*.
    """)

st.markdown('<div class="footer-text"><strong>Ignacio L. & Andrei B.</strong></div>', unsafe_allow_html=True)
