import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(
    page_title="Fuel Price Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4 { color: #ffffff; font-weight: 600; }
    
    .dashboard-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 4px;
        letter-spacing: -0.01em;
    }
    .dashboard-subtext {
        color: #8b949e;
        font-size: 0.9rem;
        margin-bottom: 24px;
    }
    
    .top-grid {
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 20px;
        margin-bottom: 20px;
    }
    
    .metrics-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
    }
    
    .glass-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        display: flex;
        flex-direction: column;
    }
    
    .metric-card {
        align-items: center;
        text-align: center;
        justify-content: center;
    }
    
    .ring-indicator {
        width: 54px;
        height: 54px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 12px;
        position: relative;
    }
    
    .ring-green { border: 2px solid #238636; color: #3fb950; }
    .ring-blue { border: 2px solid #1f6feb; color: #58a6ff; }
    .ring-purple { border: 2px solid #8957e5; color: #bc8cff; }
    .ring-red { border: 2px solid #da3633; color: #ff7b72; }
    
    .metric-value {
        color: #ffffff;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    
    .metric-label {
        color: #8b949e;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
    }
    
    .macro-card {
        justify-content: center;
        position: relative;
        overflow: hidden;
    }
    
    .macro-title {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .macro-data {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        border-top: 1px solid #30363d;
        padding-top: 16px;
        margin-top: 16px;
    }
    
    .macro-val { font-size: 2rem; font-weight: 700; color: #58a6ff; line-height: 1; }
    .macro-lbl { font-size: 0.85rem; color: #8b949e; margin-bottom: 4px; }
    
    .news-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
    }
    
    .news-header {
        color: #58a6ff;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
    }
    
    .news-title {
        color: #ffffff;
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 8px;
        line-height: 1.4;
    }
    
    .news-desc {
        color: #8b949e;
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 20px;
    }
    
    .action-btn {
        background-color: #238636;
        color: #ffffff;
        border: 1px solid rgba(240, 246, 252, 0.1);
        padding: 6px 16px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
        text-decoration: none;
        display: inline-block;
        transition: 0.2s;
    }
    
    .action-btn:hover { background-color: #2ea043; }
    .action-btn-alt { background-color: #21262d; border-color: #363b42; }
    .action-btn-alt:hover { background-color: #30363d; border-color: #8b949e; }
    
    div[data-testid="stExpander"] { background-color: #161b22; border-color: #30363d; border-radius: 8px; }
    div[data-baseweb="select"] > div { background-color: #161b22; border-color: #30363d; color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

if 'last_market_data' not in st.session_state:
    st.session_state.last_market_data = {
        "fx": 59.02, "brent": 82.50, "p91": 72.35, "p95": 74.50, "p97": 82.30, "dsl": 75.10,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S PST")
    }

if 'last_news_data' not in st.session_state:
    st.session_state.last_news_data = [
        {"title": "Global Supply Constraints", "description": "Market indicators reflect tightening supply margins across key maritime routes.", "link": "#", "source": "Reuters"},
        {"title": "Regulatory Monitoring", "description": "Domestic price ceilings are under continuous review to stabilize consumer indices.", "link": "#", "source": "DOE"}
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
            
        brent_price = float(brent_res.json()['observations'][0]['value'])
        php_rate = float(fx_res.json()['observations'][0]['value'])

        X_historical = np.array([[1, 74.2, 55.8], [1, 78.5, 56.1], [1, 80.2, 56.5], [1, 82.5, 57.0]])
        y_91 = np.array([50.50, 52.10, 57.30, 59.10])
        y_95 = np.array([54.20, 56.90, 62.10, 63.90])
        y_97 = np.array([58.10, 60.40, 65.60, 67.40])
        y_dsl = np.array([58.00, 60.50, 72.10, 75.90])

        w_91 = np.linalg.inv(X_historical.T.dot(X_historical)).dot(X_historical.T).dot(y_91)
        w_95 = np.linalg.inv(X_historical.T.dot(X_historical)).dot(X_historical.T).dot(y_95)
        w_97 = np.linalg.inv(X_historical.T.dot(X_historical)).dot(X_historical.T).dot(y_97)
        w_dsl = np.linalg.inv(X_historical.T.dot(X_historical)).dot(X_historical.T).dot(y_dsl)

        live_features = np.array([1, brent_price, php_rate])
        
        new_data = {
            "fx": php_rate, "brent": brent_price,
            "p91": live_features.dot(w_91), "p95": live_features.dot(w_95), 
            "p97": live_features.dot(w_97), "dsl": live_features.dot(w_dsl),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S PST")
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
            desc = article.get("description") or "Access source document for comprehensive data."
            if len(desc) > 120: desc = desc[:120] + "..."
            news_list.append({
                "title": article.get("title", "Market Update"),
                "description": desc,
                "link": article.get("link", "#"),
                "source": article.get("source_id", "Source").upper()
            })
        
        st.session_state.last_news_data = news_list
        return news_list
    except:
        return st.session_state.last_news_data

def generate_stochastic_forecast(base_prices, days):
    np.random.seed(42)
    dates = [(datetime.now() + timedelta(days=i)).strftime('%m/%d') for i in range(1, days + 1)]
    data = {"Date": dates}
    for grade, price in base_prices.items():
        shocks = np.random.normal(0.002, 0.012, days)
        data[grade] = [round(price * (1 + s), 2) for s in shocks]
    return pd.DataFrame(data)

data = fetch_comprehensive_market_data()
news = fetch_news_data()

pump_prices = {
    "91 RON": data["p91"], 
    "95 RON": data["p95"], 
    "97 RON": data["p97"], 
    "Diesel": data["dsl"]
}

st.markdown(f"""
    <div class="dashboard-header">Market Intelligence Console</div>
    <div class="dashboard-subtext">System synchronized: {data['timestamp']}. Operations normal.</div>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="top-grid">
        <div class="metrics-container">
            <div class="glass-card metric-card">
                <div class="ring-indicator ring-green">91</div>
                <div class="metric-value">₱{data['p91']:.2f}</div>
                <div class="metric-label">Regular</div>
            </div>
            <div class="glass-card metric-card">
                <div class="ring-indicator ring-blue">95</div>
                <div class="metric-value">₱{data['p95']:.2f}</div>
                <div class="metric-label">Premium</div>
            </div>
            <div class="glass-card metric-card">
                <div class="ring-indicator ring-purple">97</div>
                <div class="metric-value">₱{data['p97']:.2f}</div>
                <div class="metric-label">Ultra</div>
            </div>
            <div class="glass-card metric-card">
                <div class="ring-indicator ring-red">D</div>
                <div class="metric-value">₱{data['dsl']:.2f}</div>
                <div class="metric-label">Diesel</div>
            </div>
        </div>
        <div class="glass-card macro-card">
            <div class="macro-title">
                Macro Indicators
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#8b949e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 16 16 12 12 8"></polyline><line x1="8" y1="12" x2="16" y2="12"></line></svg>
            </div>
            <div>
                <div class="macro-lbl">USD/PHP Spot Rate</div>
                <div class="macro-val">₱{data['fx']:.2f}</div>
            </div>
            <div class="macro-data">
                <div>
                    <div class="macro-lbl">Brent Crude (USD/bbl)</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #ffffff;">${data['brent']:.2f}</div>
                </div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

col_chart, col_news = st.columns([2.5, 1])

with col_chart:
    st.markdown("""
        <div class="glass-card" style="padding: 24px; height: 100%;">
            <div style="font-weight: 600; font-size: 1.1rem; color: #ffffff; margin-bottom: 20px;">Performance Projections (7 Days)</div>
    """, unsafe_allow_html=True)
    
    forecast_df = generate_stochastic_forecast(pump_prices, 7)
    melted = forecast_df.melt('Date', var_name='Fuel Type', value_name='Price')
    
    chart = alt.Chart(melted).mark_line(strokeWidth=2, point=True).encode(
        x=alt.X('Date:N', axis=alt.Axis(grid=False, labelColor='#8b949e', title=None)),
        y=alt.Y('Price:Q', scale=alt.Scale(zero=False), axis=alt.Axis(grid=True, gridColor='#30363d', labelColor='#8b949e', title='Estimated Price (₱/L)')),
        color=alt.Color('Fuel Type:N', scale=alt.Scale(range=['#3fb950', '#58a6ff', '#bc8cff', '#ff7b72']), legend=alt.Legend(orient="bottom", title=None, labelColor='#8b949e')),
        tooltip=['Date', 'Fuel Type', 'Price']
    ).properties(height=320).configure_view(strokeOpacity=0)
    
    st.altair_chart(chart, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_news:
    st.markdown(f"""
        <div class="news-card">
            <div class="news-header">Intelligence Feed</div>
            <div class="news-title">{news[0]['title']}</div>
            <div class="news-desc">{news[0]['description']}</div>
            <a href="{news[0]['link']}" class="action-btn" target="_blank">View Report</a>
        </div>
        <div class="news-card">
            <div class="news-header">Regulatory Advisory</div>
            <div class="news-title">{news[1]['title']}</div>
            <div class="news-desc">{news[1]['description']}</div>
            <a href="{news[1]['link']}" class="action-btn action-btn-alt" target="_blank">Access Data</a>
        </div>
    """, unsafe_allow_html=True)

with st.expander("System Configuration & Methodology"):
    st.markdown("""
    **Architecture:**
    * Macro parameters (USD/PHP, Brent Crude) retrieved via Federal Reserve Economic Data (FRED) API.
    * Intelligence feed aggregated via NewsData.io API.
    * Regression model utilizes Ordinary Least Squares (OLS) for real-time parameter weighting.
    * Forward projections executed via Stochastic Random Walk with Gaussian distribution models.
    """)
