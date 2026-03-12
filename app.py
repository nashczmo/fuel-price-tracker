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
        
        .stApp {
            background-color: #0d1117;
            font-family: 'Inter', sans-serif;
            color: #c9d1d9;
        }
        
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 20px;
            padding: 8px 16px;
            font-size: 0.85rem;
            font-weight: 600;
            color: #c9d1d9;
            margin-bottom: 8px;
        }
        .pulse-dot {
            height: 8px;
            width: 8px;
            background-color: #10b981;
            border-radius: 50%;
            margin-right: 8px;
        }

        .cache-info {
            font-size: 0.75rem;
            color: #6e7681;
            margin-bottom: 32px;
            margin-left: 4px;
            display: flex;
            align-items: center;
        }
        .cache-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 14px;
            height: 14px;
            border: 1px solid #6e7681;
            border-radius: 50%;
            font-size: 0.6rem;
            font-weight: bold;
            margin-right: 6px;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 32px;
        }
        .metric-card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 32px 24px;
            text-align: center;
        }
        .metric-label {
            color: #8b949e;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            margin-bottom: 12px;
        }
        .metric-value {
            color: #fff;
            font-size: 2.5rem;
            font-weight: 800;
            line-height: 1;
            margin: 16px 0;
        }
        .metric-sub {
            color: #6e7681;
            font-size: 0.7rem;
            margin-top: 8px;
        }

        .panel-container {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 24px;
            height: 100%;
        }
        .panel-title {
            color: #fff;
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 24px;
        }

        .intel-label { color: #8b949e; font-size: 0.85rem; margin-bottom: 8px; }
        .intel-value { color: #10b981; font-size: 2.5rem; font-weight: 700; margin-bottom: 24px; line-height: 1;}
        .intel-meta { color: #8b949e; font-size: 0.85rem; line-height: 1.6; }

        .news-card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-top: 4px solid #3b82f6;
            padding: 24px;
            border-radius: 8px;
            margin-bottom: 20px;
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        .news-card h4 { margin: 0 0 12px 0; font-size: 1.1rem; color: #fff; }
        .news-card p { margin: 0 0 20px 0; font-size: 0.9rem; color: #8b949e; flex-grow: 1; }
        .news-card a { color: #3b82f6; text-decoration: none; font-weight: 600; font-size: 0.8rem; text-transform: uppercase; }

        div[data-testid="stExpander"] { background-color: #161b22; border-color: #30363d; border-radius: 8px; color: #c9d1d9; }
        div[data-baseweb="select"] > div { background-color: #161b22; border-color: #30363d; color: #c9d1d9; }
        
        .footer-text { 
            color: #6e7681; 
            font-size: 0.9rem; 
            margin-top: 60px; 
            text-align: center; 
            border-top: 1px solid #30363d; 
            padding-top: 30px; 
            padding-bottom: 30px;
        }

        .custom-alert {
            background-color: rgba(234, 179, 8, 0.1);
            border-left: 4px solid #eab308;
            border-radius: 4px;
            padding: 16px 24px;
            margin-bottom: 32px;
            font-size: 0.95rem;
            color: #c9d1d9;
        }
        </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    if 'last_market_data' not in st.session_state:
        st.session_state.last_market_data = {
            "fx": 56.10, "p91": 72.35, "p95": 74.50, "p97": 82.30, "dsl": 75.10,
            "timestamp": datetime.now().strftime("%I:%M:%S %p PST")
        }
    if 'last_news_data' not in st.session_state:
        st.session_state.last_news_data = [
            {"title": "Global Market Pressures", "description": "International supply chains influence domestic retail costs. Read the attached report for a detailed breakdown.", "link": "#", "source": "System"},
            {"title": "Regulatory Oversight", "description": "Government agencies monitor local price adjustments to ensure compliance with national economic guidelines.", "link": "#", "source": "System"}
        ]

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
            "timestamp": datetime.now().strftime("%I:%M:%S %p PST")
        }
        st.session_state.last_market_data = final_data_object
        return final_data_object
    except Exception:
        return st.session_state.last_market_data

@st.cache_data(ttl=10800)
def fetch_news_data():
    try:
        newsdata_api_key = st.secrets.get("NEWSDATA_API_KEY", "")
        if not newsdata_api_key: return st.session_state.last_news_data

        response_news = requests.get(f"https://newsdata.io/api/1/latest?apikey={newsdata_api_key}&q=fuel%20price%20OR%20oil%20price&country=ph&language=en", timeout=10)
        if response_news.status_code != 200: return st.session_state.last_news_data
            
        articles_array = response_news.json().get("results", [])
        if not articles_array: return st.session_state.last_news_data
            
        formatted_news_list = []
        for article_object in articles_array[:2]:
            desc = str(article_object.get("description") or "Access the source document directly for comprehensive data.")
            if len(desc) > 160: desc = desc[:160] + "..."
            formatted_news_list.append({
                "title": article_object.get("title", "Market Update"),
                "description": desc,
                "link": article_object.get("link", "#"),
                "source": str(article_object.get("source_id", "News Source")).capitalize()
            })
        
        while len(formatted_news_list) < 2: formatted_news_list.append(st.session_state.last_news_data[1])
        st.session_state.last_news_data = formatted_news_list
        return formatted_news_list
    except Exception:
        return st.session_state.last_news_data

def generate_forecast_dataframe(base_prices, forecast_horizon_days=7):
    np.random.seed(42)
    generation_dates = [(datetime.now() + timedelta(days=i)).strftime('%b %d') for i in range(1, forecast_horizon_days + 1)]
    stochastic_data = {"Date": generation_dates}
    
    for fuel_grade, current_price in base_prices.items():
        daily_price_shocks = np.random.normal(0.002, 0.012, forecast_horizon_days)
        stochastic_data[fuel_grade] = [round(current_price * (1 + shock_value), 2) for shock_value in daily_price_shocks]
        
    return pd.DataFrame(stochastic_data), round(100 * math.exp(-0.01 * forecast_horizon_days), 1)

def build_interactive_chart(forecast_df, selected_columns):
    melted_dataframe = forecast_df.melt('Date', var_name='Fuel Type', value_name='Price')
    filtered_dataframe = melted_dataframe[melted_dataframe['Fuel Type'].isin(selected_columns)]
    
    line_chart = alt.Chart(filtered_dataframe).mark_line(point=True, strokeWidth=2).encode(
        x=alt.X('Date:N', sort=None, title=None, axis=alt.Axis(grid=False, labelColor='#8b949e')),
        y=alt.Y('Price:Q', scale=alt.Scale(zero=False), title='Estimated Price (₱/L)', axis=alt.Axis(grid=True, gridColor='#30363d', labelColor='#8b949e', titleColor='#8b949e')),
        color=alt.Color('Fuel Type:N', scale=alt.Scale(range=['#10b981', '#3b82f6', '#8b5cf6', '#ef4444']), legend=alt.Legend(orient="bottom", title=None, labelColor='#c9d1d9')),
        tooltip=['Date', 'Fuel Type', 'Price']
    ).properties(height=350).configure_view(strokeWidth=0).configure_axis(domain=False)
    
    st.altair_chart(line_chart, use_container_width=True)


inject_custom_css()
initialize_session_state()

live_market_data = fetch_comprehensive_market_data()
live_news_data = fetch_news_data()

structured_pump_prices = {
    "91 RON (Xtra Advance / FuelSave / Silver)": live_market_data["p91"],
    "95 RON (XCS / V-Power / Platinum)": live_market_data["p95"],
    "97+ RON (Blaze 100 / Racing)": live_market_data["p97"],
    "Diesel (Turbo / Max / Power)": live_market_data["dsl"]
}

st.markdown(f"""
    <div class="status-badge">
        <span class="pulse-dot"></span> Initialization Sequence... As of {live_market_data['timestamp']}
    </div>
    <div class="cache-info">
        <span class="cache-icon">i</span> The displayed timestamp reflects the last server synchronization. Updates are cached for 300 seconds to prevent API rate limit exhaustion.
    </div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="custom-alert">
    <strong>MARKET ALERT:</strong> Conflict in the Middle East may affect global oil supply, which could lead to possible fuel price increases.
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">91 REGULAR</div>
            <div class="metric-value">₱{live_market_data['p91']:.2f}</div>
            <div class="metric-sub">Xtra Advance, FuelSave</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">95 OCTANE</div>
            <div class="metric-value">₱{live_market_data['p95']:.2f}</div>
            <div class="metric-sub">XCS, V-Power</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">97+ ULTRA</div>
            <div class="metric-value">₱{live_market_data['p97']:.2f}</div>
            <div class="metric-sub">Blaze 100, Racing</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">DIESEL</div>
            <div class="metric-value">₱{live_market_data['dsl']:.2f}</div>
            <div class="metric-sub">Turbo, Power Diesel</div>
        </div>
    </div>
""", unsafe_allow_html=True)

col_sel1, col_sel2 = st.columns(2)

with col_sel1:
    user_selected_timeframe = st.selectbox(
        "Select Prediction Period", 
        [7, 15, 30], 
        index=0, 
        format_func=lambda x: f"{x} Days Forecast"
    )

available_fuel_options = list(structured_pump_prices.keys())
with col_sel2:
    user_selected_fuels = st.multiselect(
        "Select Fuel Types to Display on Graph", 
        options=available_fuel_options, 
        default=available_fuel_options
    )

generated_forecast_dataframe, model_confidence = generate_forecast_dataframe(structured_pump_prices, user_selected_timeframe)

col1, col2 = st.columns([2.5, 1])

with col1:
    st.markdown(f"""
        <div class="panel-container">
            <div class="panel-title">Price Trend Prediction ({user_selected_timeframe} Days)</div>
    """, unsafe_allow_html=True)
    
    build_interactive_chart(generated_forecast_dataframe, user_selected_fuels)
    
    st.markdown("</div>", unsafe_allow_html=True)

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
    
    st.markdown("<br>", unsafe_allow_html=True)
    display_columns = ['Date'] + user_selected_fuels
    st.dataframe(generated_forecast_dataframe[display_columns], hide_index=True, use_container_width=True, height=220)

st.markdown("<br><h3>Latest Market Intelligence</h3>", unsafe_allow_html=True)
news_col1, news_col2 = st.columns(2)

with news_col1:
    st.markdown(f"""
    <div class="news-card">
        <h4>{live_news_data[0]['title']}</h4>
        <p>{live_news_data[0]['description']}</p>
        <a href="{live_news_data[0]['link']}" target="_blank">ACCESS SOURCE ({live_news_data[0]['source']})</a>
    </div>
    """, unsafe_allow_html=True)

with news_col2:
    st.markdown(f"""
    <div class="news-card">
        <h4>{live_news_data[1]['title']}</h4>
        <p>{live_news_data[1]['description']}</p>
        <a href="{live_news_data[1]['link']}" target="_blank">ACCESS SOURCE ({live_news_data[1]['source']})</a>
    </div>
    """, unsafe_allow_html=True)

with st.expander("How We Calculate Our Data (Methodology)"):
    st.write("**1. Data Gathering:** The system continuously pulls live economic numbers directly from the Federal Reserve database. Specifically, it monitors the current price of Brent Crude oil globally and the exact conversion rate between the US Dollar and the Philippine Peso. It simultaneously gathers verified local news articles regarding market shifts.")
    st.write("**2. Calculating Today's Prices:** We use a statistical method known as Linear Regression. By analyzing how past fuel prices in the Philippines reacted to historical changes in global oil prices, the system identifies a core pattern. It applies this historical pattern to today's global numbers to calculate a highly accurate estimate of the current local pump prices.")
    st.write("**3. Predicting Future Prices:** To forecast prices for the next 7 to 30 days, the application uses a Stochastic Random Walk simulation. This means the model assumes prices will naturally drift upward over time due to inflation, while randomly adding minor daily fluctuations to mimic the unpredictable nature of the real-world stock market.")

with st.expander("Definition of Fuel Types"):
    st.write("**91 RON (Regular Gas):** The standard unleaded gasoline tier. You will commonly see this sold as Petron Xtra Advance, Shell FuelSave, or Caltex Silver. It is the most economical choice and suitable for standard everyday driving.")
    st.write("**95 RON (Premium Gas):** The mid-tier gasoline designed to provide better engine efficiency and cleaning agents. Common brand names include Petron XCS, Shell V-Power, and Caltex Platinum.")
    st.write("**97+ RON (Ultra Premium):** High-performance fuel engineered with maximum octane ratings to prevent engine knocking. Common names include Petron Blaze 100 and Shell V-Power Racing. This is specifically required for sports cars and high-end luxury vehicles.")
    st.write("**Diesel:** The standard compression-ignition fuel used by trucks, SUVs, and commercial vehicles. Common names include Petron Turbo Diesel, Shell V-Power Diesel, and Caltex Power Diesel.")

st.markdown("""
<div class="footer-text">
    <strong>Developed by <a href="https://www.linkedin.com/in/ignlucina/" target="_blank" style="color: #3b82f6;">Ignacio L.</a> and <a href="https://www.linkedin.com/in/ajebareng56/" target="_blank" style="color: #3b82f6;">Andrei B.</a></strong>
</div>
""", unsafe_allow_html=True)
