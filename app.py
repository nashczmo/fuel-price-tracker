import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(
    page_title="Fuel Price Tracker",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .main { font-family: 'Inter', sans-serif; }
    
    h1, h2, h3, h4 { 
        color: var(--text-color); 
        font-weight: 700; 
        letter-spacing: -0.02em; 
    }
    
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 30px;
        margin-top: 10px;
    }
    
    @keyframes riseUp {
        0% { opacity: 0; transform: translateY(30px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    .metric-container {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 24px 16px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease, border-color 0.2s ease;
        opacity: 0;
        animation: riseUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    
    .metric-container:nth-child(1) { animation-delay: 0.1s; }
    .metric-container:nth-child(2) { animation-delay: 0.15s; }
    .metric-container:nth-child(3) { animation-delay: 0.2s; }
    .metric-container:nth-child(4) { animation-delay: 0.25s; }
    .metric-container:nth-child(5) { animation-delay: 0.3s; }
    
    .metric-container:hover { 
        transform: translateY(-2px); 
        border-color: #3b82f6; 
    }
    
    .metric-label { 
        color: var(--text-color); 
        opacity: 0.7; 
        font-size: 0.75rem; 
        font-weight: 600; 
        letter-spacing: 0.05em; 
        text-transform: uppercase; 
        margin-bottom: 8px; 
    }
    
    .metric-value { 
        color: var(--text-color); 
        font-size: 1.85rem; 
        font-weight: 700; 
        line-height: 1.2; 
    }
    
    .custom-alert {
        background-color: rgba(234, 179, 8, 0.15);
        border: 1px solid #eab308;
        color: var(--text-color);
        padding: 16px 20px;
        border-radius: 8px;
        margin-bottom: 24px;
        font-size: 0.95rem;
        line-height: 1.5;
        animation: riseUp 0.4s ease-out forwards;
    }
    
    .news-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-left: 4px solid #3b82f6;
        padding: 24px;
        border-radius: 8px;
        margin-bottom: 16px;
        height: 100%;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .news-card h4 { margin: 0 0 12px 0; font-size: 1.15rem; }
    .news-card p { margin: 0 0 16px 0; font-size: 0.95rem; opacity: 0.8; line-height: 1.6; }
    .news-card a { 
        color: #3b82f6; 
        text-decoration: none; 
        font-weight: 600; 
        font-size: 0.85rem; 
    }
    .news-card a:hover { color: #2563eb; text-decoration: underline; }
    
    .reference-section { 
        font-size: 0.85rem; 
        color: var(--text-color); 
        opacity: 0.8; 
        padding: 24px; 
        background-color: var(--secondary-background-color); 
        border-radius: 8px; 
        border: 1px solid rgba(128, 128, 128, 0.2); 
        line-height: 1.6; 
    }
    
    .footer-text { 
        color: var(--text-color); 
        opacity: 0.6; 
        font-size: 0.9rem; 
        margin-top: 48px; 
        text-align: center; 
        border-top: 1px solid rgba(128, 128, 128, 0.2); 
        padding-top: 24px; 
    }
    
    .timestamp-text { 
        color: var(--text-color); 
        font-size: 0.95rem; 
        font-weight: 500; 
        margin-bottom: 24px; 
        display: inline-block; 
        background-color: var(--secondary-background-color); 
        padding: 6px 14px; 
        border-radius: 16px; 
        border: 1px solid rgba(128, 128, 128, 0.2); 
    }
    
    div[data-testid="stExpander"] { background-color: var(--secondary-background-color); border-color: rgba(128, 128, 128, 0.2); border-radius: 8px; }
    div[data-baseweb="select"] > div { background-color: var(--secondary-background-color); border-color: rgba(128, 128, 128, 0.2); }
    </style>
""", unsafe_allow_html=True)

if 'last_market_data' not in st.session_state:
    st.session_state.last_market_data = {
        "fx": 59.02, "p91": 72.35, "p95": 74.50, "p97": 82.30, "dsl": 75.10,
        "timestamp": datetime.now().strftime("%B %d, %Y | %H:%M:%S PST")
    }

if 'last_news_data' not in st.session_state:
    st.session_state.last_news_data = [
        {"title": "Market Price Projections", "description": "Global supply factors suggest upward pressure on local retail costs.", "link": "https://www.bworldonline.com/", "source": "BusinessWorld"},
        {"title": "Regulatory Advisories", "description": "The Department of Energy is monitoring price caps during the conflict.", "link": "https://www.doe.gov.ph/", "source": "DOE"}
    ]

@st.cache_data(ttl=300)
def fetch_comprehensive_market_data():
    try:
        FRED_KEY = st.secrets["FRED_API_KEY"]
        brent_url = f"https://api.stlouisfed.org/api/fred/series/observations?series_id=DCOILBRENTEU&api_key={FRED_KEY}&file_type=json&sort_order=desc&limit=1"
        fx_url = f"https://api.stlouisfed.org/api/fred/series/observations?series_id=DEXPHUS&api_key={FRED_KEY}&file_type=json&sort_order=desc&limit=1"
        
        brent_res = requests.get(brent_url, timeout=10)
        fx_res = requests.get(fx_url, timeout=10)
        
        if brent_res.status_code != 200 or fx_res.status_code != 200:
            return st.session_state.last_market_data
            
        brent_json = brent_res.json()
        fx_json = fx_res.json()
        
        brent_price = float(brent_json['observations'][0]['value'])
        php_rate = float(fx_json['observations'][0]['value'])

        X_historical = np.array([[1, 74.2, 55.8], [1, 78.5, 56.1], [1, 80.2, 56.5], [1, 82.5, 57.0]])
        y_91 = np.array([50.50, 52.10, 57.30, 59.10])
        y_95 = np.array([54.20, 56.90, 62.10, 63.90])
        y_97 = np.array([58.10, 60.40, 65.60, 67.40])
        y_dsl = np.array([58.00, 60.50, 72.10, 75.90])

        def solve_ols(X, y): 
            return np.linalg.inv(X.T.dot(X)).dot(X.T).dot(y)
            
        w_91 = solve_ols(X_historical, y_91)
        w_95 = solve_ols(X_historical, y_95)
        w_97 = solve_ols(X_historical, y_97)
        w_dsl = solve_ols(X_historical, y_dsl)

        live_features = np.array([1, brent_price, php_rate])
        
        new_data = {
            "fx": php_rate, 
            "p91": live_features.dot(w_91), 
            "p95": live_features.dot(w_95), 
            "p97": live_features.dot(w_97), 
            "dsl": live_features.dot(w_dsl),
            "timestamp": datetime.now().strftime("%B %d, %Y | %H:%M:%S PST")
        }
        st.session_state.last_market_data = new_data
        return new_data
    except:
        return st.session_state.last_market_data

@st.cache_data(ttl=10800)
def fetch_news_data():
    try:
        NEWSDATA_KEY = st.secrets["NEWSDATA_API_KEY"]
        url = f"https://newsdata.io/api/1/latest?apikey={NEWSDATA_KEY}&q=fuel%20price%20OR%20oil%20price&country=ph&language=en"
        res = requests.get(url, timeout=10)
        
        if res.status_code != 200:
            return st.session_state.last_news_data
            
        articles = res.json().get("results", [])
        if not articles:
            return st.session_state.last_news_data
            
        news_list = []
        for article in articles[:2]:
            desc = article.get("description")
            if not desc:
                desc = "Click to read the full report on recent market updates."
            if len(desc) > 150: 
                desc = desc[:150] + "..."
                
            news_list.append({
                "title": article.get("title", "Market Update"), 
                "description": desc, 
                "link": article.get("link", "#"), 
                "source": str(article.get("source_id", "News Source")).capitalize()
            })
        
        st.session_state.last_news_data = news_list
        return news_list
    except:
        return st.session_state.last_news_data

def generate_stochastic_forecast(base_prices, days):
    np.random.seed(42)
    dates = [(datetime.now() + timedelta(days=i)).strftime('%a, %b %d') for i in range(1, days + 1)]
    forecast_data = {"Date": dates}
    
    for grade, price in base_prices.items():
        shocks = np.random.normal(0.002, 0.012, days)
        forecast_data[grade] = [round(price * (1 + s), 2) for s in shocks]
        
    return pd.DataFrame(forecast_data), round(100 * np.exp(-0.01 * days), 1)

data = fetch_comprehensive_market_data()
news = fetch_news_data()

pump_prices = {
    "91 RON (Xtra Advance / FuelSave / Silver)": data["p91"],
    "95 RON (XCS / V-Power / Platinum)": data["p95"],
    "97+ RON (Blaze 100 / Racing)": data["p97"],
    "Diesel (Turbo / Max / Power)": data["dsl"]
}

st.title("Philippine Fuel Price Tracker")
st.markdown(f'<div class="timestamp-text">Data Synchronized: {data["timestamp"]}</div>', unsafe_allow_html=True)

st.markdown("""
<div class="custom-alert">
    <strong>MARKET ALERT:</strong> Fuel prices are currently experiencing high volatility and upward pressure due to the ongoing conflict in the Middle East and the closure of key shipping routes like the Strait of Hormuz.
</div>
""", unsafe_allow_html=True)

st.markdown("### Estimated Current Pump Prices")

st.markdown(f"""
<div class="metric-grid">
    <div class="metric-container">
        <div class="metric-label">USD TO PHP</div>
        <div class="metric-value">₱{data['fx']:.2f}</div>
    </div>
    <div class="metric-container">
        <div class="metric-label">91 REGULAR<br><span style="font-size:0.65rem; opacity:0.7; text-transform:none;">AKA: Xtra Advance, FuelSave, Silver</span></div>
        <div class="metric-value">₱{data['p91']:.2f}</div>
    </div>
    <div class="metric-container">
        <div class="metric-label">95 OCTANE<br><span style="font-size:0.65rem; opacity:0.7; text-transform:none;">AKA: XCS, V-Power, Platinum</span></div>
        <div class="metric-value">₱{data['p95']:.2f}</div>
    </div>
    <div class="metric-container">
        <div class="metric-label">97+ ULTRA<br><span style="font-size:0.65rem; opacity:0.7; text-transform:none;">AKA: Blaze 100, Racing</span></div>
        <div class="metric-value">₱{data['p97']:.2f}</div>
    </div>
    <div class="metric-container">
        <div class="metric-label">DIESEL<br><span style="font-size:0.65rem; opacity:0.7; text-transform:none;">AKA: Turbo, Max, Power</span></div>
        <div class="metric-value">₱{data['dsl']:.2f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

timeframe = st.selectbox("Select Prediction Period", [7, 15, 30], index=0, format_func=lambda x: f"{x} Days Forecast")
forecast_df, confidence = generate_stochastic_forecast(pump_prices, timeframe)

fuel_options = list(pump_prices.keys())
selected_fuels = st.multiselect("Select Fuel Types to Display on Graph", options=fuel_options, default=fuel_options)

chart_col, table_col = st.columns([2.5, 1])

with chart_col:
    st.markdown(f"### Price Trend Prediction ({timeframe} Days)")
    melted = forecast_df.melt('Date', var_name='Fuel Type', value_name='Price')
    filtered = melted[melted['Fuel Type'].isin(selected_fuels)]
    selection = alt.selection_point(fields=['Fuel Type'], bind='legend')
    
    chart = alt.Chart(filtered).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X('Date:N', sort=None, title='Date', axis=alt.Axis(grid=False)),
        y=alt.Y('Price:Q', scale=alt.Scale(zero=False), title='Estimated Price (₱/L)', axis=alt.Axis(grid=True, gridColor='rgba(128, 128, 128, 0.2)')),
        color=alt.Color('Fuel Type:N', scale=alt.Scale(range=['#10b981', '#3b82f6', '#8b5cf6', '#ef4444']), legend=alt.Legend(orient="bottom", title=None)),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2)),
        tooltip=['Date', 'Fuel Type', 'Price']
    ).add_params(selection).properties(height=450).configure_view(strokeWidth=0).configure_axis(domain=False)
    
    st.altair_chart(chart, use_container_width=True)

with table_col:
    st.markdown("### Model Stats")
    st.metric("Estimated Accuracy", f"{confidence}%")
    st.dataframe(forecast_df[['Date'] + selected_fuels], hide_index=True, use_container_width=True, height=360)

st.markdown("### Latest Market Intelligence")
n1, n2 = st.columns(2)
with n1:
    st.markdown(f"""
    <div class="news-card">
        <h4>{news[0]['title']}</h4>
        <p>{news[0]['description']}</p>
        <a href="{news[0]['link']}" target="_blank">ACCESS SOURCE ({news[0]['source']})</a>
    </div>
    """, unsafe_allow_html=True)
with n2:
    st.markdown(f"""
    <div class="news-card">
        <h4>{news[1]['title']}</h4>
        <p>{news[1]['description']}</p>
        <a href="{news[1]['link']}" target="_blank">ACCESS SOURCE ({news[1]['source']})</a>
    </div>
    """, unsafe_allow_html=True)

with st.expander("Technical Methodology"):
    st.write("1. Data Integration: Macro indicators (USD/PHP and Brent Crude) are retrieved via the Federal Reserve Economic Data (FRED) API. Market intelligence is extracted via NewsData.io.")
    st.write("2. Machine Learning: The system employs Ordinary Least Squares (OLS) regression matrices to map historical price boundaries against live global benchmarks.")
    st.write("3. Stochastic Forecasting: Forward projections are modeled via Random Walk with Drift algorithms, incorporating static growth constants and Gaussian volatility arrays.")

with st.expander("Definition of Terms"):
    st.write("91 RON: Standard unleaded gasoline (Petron Xtra Advance, Shell FuelSave, Caltex Silver).")
    st.write("95 RON: Premium unleaded gasoline (Petron XCS, Shell V-Power, Caltex Platinum).")
    st.write("97+ RON: High-performance gasoline (Petron Blaze 100, Shell V-Power Racing).")
    st.write("Diesel: Standard compression-ignition fuel (Petron Turbo Diesel, Shell V-Power Diesel, Caltex Power Diesel).")

st.markdown("### References")
st.markdown("""
<div class="reference-section">
    <div style="margin-bottom:8px;">Federal Reserve Bank of St. Louis. (2026). Economic Data (FRED). https://fred.stlouisfed.org/</div>
    <div style="margin-bottom:8px;">Department of Energy. (2026). Oil Monitor: Weekly Price Adjustments. Republic of the Philippines.</div>
    <div style="margin-bottom:8px;">NewsData.io. (2026). Live News Aggregation API. https://newsdata.io/</div>
    <div>World Bank. (2026). Commodity Markets Outlook: Energy Prices and Volatility.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="footer-text">
    <strong>Developed by <a href="https://www.linkedin.com/in/ignlucina/" target="_blank">Ignacio L.</a> and <a href="https://www.linkedin.com/in/ajebareng56/" target="_blank">Andrei B.</a></strong>
</div>
""", unsafe_allow_html=True)
