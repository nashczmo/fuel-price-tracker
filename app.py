import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(
    page_title="Fuel Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Theme Overrides */
    .stApp {
        background-color: #111318;
        color: #e1e7ef;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Overrides */
    [data-testid="stSidebar"] {
        background-color: #171a21 !important;
        border-right: 1px solid #262b36;
    }
    
    .sidebar-menu-item {
        padding: 10px 16px;
        margin: 4px 0;
        border-radius: 8px;
        color: #8b949e;
        display: flex;
        align-items: center;
        gap: 12px;
        font-weight: 500;
        cursor: pointer;
        transition: 0.2s;
    }
    .sidebar-menu-item:hover, .sidebar-menu-item.active {
        background-color: #1f242d;
        color: #fff;
    }
    
    /* Hide Streamlit elements */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}

    /* Custom UI Classes */
    .greeting {
        font-size: 1.4rem;
        font-weight: 700;
        color: #fff;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .subtext {
        color: #8b949e;
        font-size: 0.85rem;
        margin-bottom: 24px;
    }
    
    .flex-row {
        display: flex;
        gap: 16px;
        margin-bottom: 16px;
        flex-wrap: wrap;
    }
    
    .e-card {
        background-color: #1c1f27;
        border: 1px solid #2d3340;
        border-radius: 12px;
        padding: 16px;
        position: relative;
        overflow: hidden;
    }
    
    /* Green Metric Cards */
    .metric-box {
        flex: 1;
        min-width: 120px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    .metric-circle {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        border: 2px solid #22c55e;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 12px;
        color: #22c55e;
        font-weight: bold;
        position: relative;
    }
    .metric-circle::after {
        content: '';
        position: absolute;
        top: -4px; left: -4px; right: -4px; bottom: -4px;
        border: 1px solid rgba(34, 197, 94, 0.2);
        border-radius: 50%;
    }
    .metric-val {
        color: #fff;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 4px;
    }
    .metric-lbl {
        color: #22c55e;
        font-size: 0.75rem;
    }

    /* Score Card Equivalent */
    .score-box {
        flex: 1.5;
        min-width: 250px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 24px;
    }
    .score-text {
        font-size: 1.1rem;
        font-weight: 600;
        color: #fff;
        max-width: 120px;
    }
    .score-circle {
        width: 70px;
        height: 70px;
        border-radius: 50%;
        border: 6px solid #3b82f6;
        border-right-color: #1c1f27;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        font-weight: 700;
        color: #fff;
        transform: rotate(-45deg);
    }
    .score-circle span {
        transform: rotate(45deg);
    }

    /* Monitor / Chart Container */
    .monitor-box {
        padding: 24px;
        height: 100%;
        background: linear-gradient(135deg, #1c1f27 0%, #171a21 100%);
    }
    .monitor-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #fff;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .monitor-desc {
        font-size: 0.85rem;
        color: #8b949e;
        margin-bottom: 20px;
        line-height: 1.5;
    }
    
    /* Action Buttons */
    .btn-primary {
        background-color: #3b82f6;
        color: #fff;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
        cursor: pointer;
        display: inline-block;
        text-decoration: none;
    }
    
    /* Standard Streamlit Overrides for Altair */
    [data-testid="stVegaLiteChart"] {
        background-color: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- DATA LOGIC -----------------
if 'last_market_data' not in st.session_state:
    st.session_state.last_market_data = {
        "fx": 59.02, "p91": 72.35, "p95": 74.50, "p97": 82.30, "dsl": 75.10,
        "timestamp": datetime.now().strftime("%B %d, %Y | %H:%M:%S PST")
    }

if 'last_news_data' not in st.session_state:
    st.session_state.last_news_data = [
        {"title": "Market Price Projections", "description": "Global supply factors suggest upward pressure on local retail costs.", "link": "#", "source": "BusinessWorld"},
        {"title": "Regulatory Advisories", "description": "The Department of Energy is monitoring price caps during the conflict.", "link": "#", "source": "DOE"}
    ]

@st.cache_data(ttl=300)
def fetch_comprehensive_market_data():
    try:
        FRED_KEY = st.secrets["FRED_API_KEY"]
        brent_url = f"https://api.stlouisfed.org/api/fred/series/observations?series_id=DCOILBRENTEU&api_key={FRED_KEY}&file_type=json&sort_order=desc&limit=1"
        fx_url = f"https://api.stlouisfed.org/api/fred/series/observations?series_id=DEXPHUS&api_key={FRED_KEY}&file_type=json&sort_order=desc&limit=1"
        
        brent_res = requests.get(brent_url, timeout=10)
        fx_res = requests.get(fx_url, timeout=10)
        
        if brent_res.status_code != 200 or fx_res.status_code != 200: return st.session_state.last_market_data
            
        brent_price = float(brent_res.json()['observations'][0]['value'])
        php_rate = float(fx_res.json()['observations'][0]['value'])

        X_historical = np.array([[1, 74.2, 55.8], [1, 78.5, 56.1], [1, 80.2, 56.5], [1, 82.5, 57.0]])
        y_91, y_95, y_97, y_dsl = np.array([50.50, 52.10, 57.30, 59.10]), np.array([54.20, 56.90, 62.10, 63.90]), np.array([58.10, 60.40, 65.60, 67.40]), np.array([58.00, 60.50, 72.10, 75.90])

        w_91 = np.linalg.inv(X_historical.T.dot(X_historical)).dot(X_historical.T).dot(y_91)
        w_95 = np.linalg.inv(X_historical.T.dot(X_historical)).dot(X_historical.T).dot(y_95)
        w_97 = np.linalg.inv(X_historical.T.dot(X_historical)).dot(X_historical.T).dot(y_97)
        w_dsl = np.linalg.inv(X_historical.T.dot(X_historical)).dot(X_historical.T).dot(y_dsl)

        live_features = np.array([1, brent_price, php_rate])
        
        new_data = {"fx": php_rate, "p91": live_features.dot(w_91), "p95": live_features.dot(w_95), "p97": live_features.dot(w_97), "dsl": live_features.dot(w_dsl), "timestamp": datetime.now().strftime("%B %d, %Y | %H:%M")}
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
        
        if res.status_code != 200: return st.session_state.last_news_data
        articles = res.json().get("results", [])
        if not articles: return st.session_state.last_news_data
            
        news_list = []
        for article in articles[:2]:
            desc = article.get("description") or "Click to read the full report on recent market updates."
            if len(desc) > 100: desc = desc[:100] + "..."
            news_list.append({"title": article.get("title", "Market Update")[:40]+"...", "description": desc, "link": article.get("link", "#")})
        
        st.session_state.last_news_data = news_list
        return news_list
    except:
        return st.session_state.last_news_data

def generate_forecast(base_prices):
    np.random.seed(42)
    dates = [(datetime.now() + timedelta(days=i)).strftime('%m/%d') for i in range(1, 8)]
    data = {"Date": dates}
    for grade, price in base_prices.items():
        data[grade] = [round(price * (1 + s), 2) for s in np.random.normal(0.002, 0.012, 7)]
    return pd.DataFrame(data)

data = fetch_comprehensive_market_data()
news = fetch_news_data()
forecast_df = generate_forecast({"91 RON": data["p91"], "95 RON": data["p95"], "97 RON": data["p97"], "Diesel": data["dsl"]})

# ----------------- SIDEBAR UI -----------------
with st.sidebar:
    st.markdown("<h2 style='color: #3b82f6; font-size: 1.5rem; margin-bottom: 30px;'>⚙️ FuelTrack</h2>", unsafe_allow_html=True)
    st.markdown("""
        <div class="sidebar-menu-item active">🏠 Home</div>
        <div class="sidebar-menu-item">📈 Optimizer</div>
        <div class="sidebar-menu-item">📊 Cleaner</div>
        <div class="sidebar-menu-item">⚡ Booster</div>
        <div class="sidebar-menu-item">⚙️ Settings</div>
    """, unsafe_allow_html=True)

# ----------------- MAIN UI -----------------
st.markdown(f"""
    <div class="greeting">👋 Good day, driver</div>
    <div class="subtext">System synchronized at {data['timestamp']}. Ready for deployment.</div>
""", unsafe_allow_html=True)

# Top Row: 4 Metrics + Score Card
st.markdown(f"""
    <div class="flex-row">
        <div class="e-card metric-box">
            <div class="metric-circle">91</div>
            <div class="metric-val">₱{data['p91']:.2f}</div>
            <div class="metric-lbl">Updated today</div>
        </div>
        <div class="e-card metric-box">
            <div class="metric-circle">95</div>
            <div class="metric-val">₱{data['p95']:.2f}</div>
            <div class="metric-lbl">Updated today</div>
        </div>
        <div class="e-card metric-box">
            <div class="metric-circle">97</div>
            <div class="metric-val">₱{data['p97']:.2f}</div>
            <div class="metric-lbl">Updated today</div>
        </div>
        <div class="e-card metric-box" style="border-color: #3b82f6;">
            <div class="metric-circle" style="border-color: #3b82f6; color: #3b82f6;">D</div>
            <div class="metric-val">₱{data['dsl']:.2f}</div>
            <div class="metric-lbl" style="color: #3b82f6;">Updated today</div>
        </div>
        <div class="e-card score-box">
            <div class="score-text">Your USD/PHP <span style="color:#3b82f6;">exchange</span> rate is...</div>
            <div class="score-circle"><span>{int(data['fx'])}</span></div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Middle Row: Graph + News Cards
col_main, col_side = st.columns([2.2, 1])

with col_main:
    st.markdown("""
        <div class="e-card monitor-box" style="margin-bottom: 0px; padding-bottom: 0px;">
            <div class="monitor-title">📈 Monitor your Market</div>
            <div class="monitor-desc">Understand how fuel trajectories operate during idle and load by monitoring global resources in real-time.</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Altair Chart styling to match dark theme
    melted = forecast_df.melt('Date', var_name='Fuel Type', value_name='Price')
    chart = alt.Chart(melted).mark_line(strokeWidth=3, point=True).encode(
        x=alt.X('Date:N', axis=alt.Axis(grid=False, labelColor='#8b949e', titleColor='#8b949e')),
        y=alt.Y('Price:Q', scale=alt.Scale(zero=False), axis=alt.Axis(grid=True, gridColor='#2d3340', labelColor='#8b949e', titleColor='#8b949e')),
        color=alt.Color('Fuel Type:N', scale=alt.Scale(range=['#22c55e', '#3b82f6', '#8b5cf6', '#ef4444']), legend=None),
        tooltip=['Date', 'Fuel Type', 'Price']
    ).properties(height=280).configure_view(strokeOpacity=0).configure_axis(domainColor='#2d3340')
    
    st.altair_chart(chart, use_container_width=True)

with col_side:
    st.markdown(f"""
        <div class="e-card" style="margin-bottom: 16px;">
            <div class="monitor-title" style="color: #3b82f6;">Market Intelligence Mode</div>
            <div class="monitor-desc" style="font-size: 0.8rem;">{news[0]['title']}<br><br>{news[0]['description']}</div>
            <a href="{news[0]['link']}" class="btn-primary" target="_blank">Read Report</a>
        </div>
        <div class="e-card">
            <div class="monitor-title" style="color: #3b82f6;">Quick Advisory</div>
            <div class="monitor-desc" style="font-size: 0.8rem;">{news[1]['title']}<br><br>{news[1]['description']}</div>
            <a href="{news[1]['link']}" class="btn-primary" target="_blank">Verify Update</a>
        </div>
    """, unsafe_allow_html=True)
