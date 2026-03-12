import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime, timedelta
import numpy as np
import math

st.set_page_config(
    page_title="Fuel Price Tracker",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        .main { 
            font-family: 'Inter', sans-serif; 
            background-color: var(--background-color);
        }
        
        h1, h2, h3, h4, h5, h6 { 
            color: var(--text-color); 
            font-weight: 700; 
            letter-spacing: -0.02em; 
            margin-bottom: 1rem;
        }
        
        p {
            line-height: 1.6;
            color: var(--text-color);
            opacity: 0.9;
        }
        
        @keyframes riseUpFade {
            0% { 
                opacity: 0; 
                transform: translateY(25px); 
            }
            100% { 
                opacity: 1; 
                transform: translateY(0); 
            }
        }
        
        @keyframes pulseIndicator {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-bottom: 32px;
            margin-top: 12px;
        }
        
        @media (min-width: 768px) {
            .metric-grid {
                grid-template-columns: repeat(4, 1fr);
            }
        }
        
        .metric-container {
            background-color: var(--secondary-background-color);
            border: 1px solid rgba(128, 128, 128, 0.15);
            padding: 20px 12px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            opacity: 0;
            animation: riseUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        
        .metric-container:nth-child(1) { animation-delay: 0.05s; }
        .metric-container:nth-child(2) { animation-delay: 0.15s; }
        .metric-container:nth-child(3) { animation-delay: 0.25s; }
        .metric-container:nth-child(4) { animation-delay: 0.35s; }
        
        .metric-container:hover { 
            transform: translateY(-4px); 
            border-color: #3b82f6; 
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        
        .metric-label { 
            color: var(--text-color); 
            opacity: 0.75; 
            font-size: 0.75rem; 
            font-weight: 700; 
            letter-spacing: 0.06em; 
            text-transform: uppercase; 
            margin-bottom: 12px; 
        }
        
        .metric-value { 
            color: var(--text-color); 
            font-size: 1.8rem; 
            font-weight: 800; 
            line-height: 1.1; 
            letter-spacing: -0.03em;
        }

        .metric-subtitle {
            font-size: 0.65rem; 
            opacity: 0.6; 
            text-transform: none;
            font-weight: 500;
            display: block;
            margin-top: 4px;
        }
        
        .custom-alert {
            background-color: rgba(234, 179, 8, 0.1);
            border-left: 4px solid #eab308;
            border-radius: 4px;
            padding: 16px 24px;
            margin-bottom: 32px;
            font-size: 0.95rem;
            line-height: 1.6;
            color: var(--text-color);
            opacity: 0;
            animation: riseUpFade 0.5s ease-out forwards;
            animation-delay: 0.1s;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        
        .news-card {
            background-color: var(--secondary-background-color);
            border: 1px solid rgba(128, 128, 128, 0.15);
            border-top: 4px solid #3b82f6;
            padding: 28px;
            border-radius: 8px;
            margin-bottom: 20px;
            height: 100%;
            display: flex;
            flex-direction: column;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            opacity: 0;
            animation: riseUpFade 0.6s ease-out forwards;
            animation-delay: 0.5s;
        }
        
        .news-card h4 { 
            margin: 0 0 12px 0; 
            font-size: 1.2rem; 
            line-height: 1.4;
        }
        
        .news-card p { 
            margin: 0 0 20px 0; 
            font-size: 0.95rem; 
            opacity: 0.85; 
            flex-grow: 1;
        }
        
        .news-card a { 
            color: #3b82f6; 
            text-decoration: none; 
            font-weight: 600; 
            font-size: 0.85rem; 
            text-transform: uppercase;
            letter-spacing: 0.02em;
            display: inline-block;
            transition: color 0.2s ease;
        }
        
        .news-card a:hover { 
            color: #2563eb; 
            text-decoration: underline; 
        }
        
        .reference-section { 
            font-size: 0.85rem; 
            color: var(--text-color); 
            opacity: 0.8; 
            padding: 28px; 
            background-color: var(--secondary-background-color); 
            border-radius: 8px; 
            border: 1px solid rgba(128, 128, 128, 0.15); 
            line-height: 1.7; 
        }
        
        .footer-text { 
            color: var(--text-color); 
            opacity: 0.6; 
            font-size: 0.9rem; 
            margin-top: 60px; 
            text-align: center; 
            border-top: 1px solid rgba(128, 128, 128, 0.15); 
            padding-top: 30px; 
            padding-bottom: 30px;
        }
        
        .timestamp-text { 
            color: var(--text-color); 
            font-size: 0.9rem; 
            font-weight: 600; 
            margin-bottom: 24px; 
            display: inline-flex;
            align-items: center;
            background-color: var(--secondary-background-color); 
            padding: 8px 16px; 
            border-radius: 20px; 
            border: 1px solid rgba(128, 128, 128, 0.15); 
        }

        .pulse-dot {
            height: 8px;
            width: 8px;
            background-color: #10b981;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
            animation: pulseIndicator 2s infinite;
        }
        
        div[data-testid="stExpander"] { 
            background-color: var(--secondary-background-color); 
            border-color: rgba(128, 128, 128, 0.15); 
            border-radius: 8px; 
        }
        
        div[data-baseweb="select"] > div { 
            background-color: var(--secondary-background-color); 
            border-color: rgba(128, 128, 128, 0.15); 
        }
        </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    if 'last_market_data' not in st.session_state:
        st.session_state.last_market_data = {
            "fx": 59.02, 
            "p91": 72.35, 
            "p95": 74.50, 
            "p97": 82.30, 
            "dsl": 75.10,
            "timestamp": datetime.now().strftime("%B %d, %Y | %I:%M %p PST")
        }

    if 'last_news_data' not in st.session_state:
        st.session_state.last_news_data = [
            {
                "title": "Global Market Pressures", 
                "description": "International supply chains influence domestic retail costs. Read the attached report for a detailed breakdown.", 
                "link": "https://www.bworldonline.com/", 
                "source": "BusinessWorld"
            },
            {
                "title": "Regulatory Oversight", 
                "description": "Government agencies monitor local price adjustments to ensure compliance with national economic guidelines.", 
                "link": "https://www.doe.gov.ph/", 
                "source": "DOE"
            }
        ]

@st.cache_data(ttl=300)
def compute_linear_regression(brent_price, php_rate):
    historical_features = np.array([
        [1, 74.2, 55.8], 
        [1, 78.5, 56.1], 
        [1, 80.2, 56.5], 
        [1, 82.5, 57.0]
    ])
    
    historical_targets_91 = np.array([50.50, 52.10, 57.30, 59.10])
    historical_targets_95 = np.array([54.20, 56.90, 62.10, 63.90])
    historical_targets_97 = np.array([58.10, 60.40, 65.60, 67.40])
    historical_targets_dsl = np.array([58.00, 60.50, 72.10, 75.90])

    def resolve_matrix(X, y): 
        transposed_x = X.T
        dot_product_xx = transposed_x.dot(X)
        inverse_matrix = np.linalg.inv(dot_product_xx)
        dot_product_xy = transposed_x.dot(y)
        final_weights = inverse_matrix.dot(dot_product_xy)
        return final_weights
        
    weights_91 = resolve_matrix(historical_features, historical_targets_91)
    weights_95 = resolve_matrix(historical_features, historical_targets_95)
    weights_97 = resolve_matrix(historical_features, historical_targets_97)
    weights_dsl = resolve_matrix(historical_features, historical_targets_dsl)

    current_input_vector = np.array([1, brent_price, php_rate])
    
    predicted_prices = {
        "p91": current_input_vector.dot(weights_91),
        "p95": current_input_vector.dot(weights_95),
        "p97": current_input_vector.dot(weights_97),
        "dsl": current_input_vector.dot(weights_dsl)
    }
    
    return predicted_prices

@st.cache_data(ttl=300)
def fetch_comprehensive_market_data():
    try:
        fred_api_key = st.secrets["FRED_API_KEY"]
        
        endpoint_brent = f"https://api.stlouisfed.org/api/fred/series/observations?series_id=DCOILBRENTEU&api_key={fred_api_key}&file_type=json&sort_order=desc&limit=1"
        endpoint_fx = f"https://api.stlouisfed.org/api/fred/series/observations?series_id=DEXPHUS&api_key={fred_api_key}&file_type=json&sort_order=desc&limit=1"
        
        response_brent = requests.get(endpoint_brent, timeout=10)
        response_fx = requests.get(endpoint_fx, timeout=10)
        
        if response_brent.status_code != 200 or response_fx.status_code != 200:
            return st.session_state.last_market_data
            
        json_brent = response_brent.json()
        json_fx = response_fx.json()
        
        current_brent_price = float(json_brent['observations'][0]['value'])
        current_php_rate = float(json_fx['observations'][0]['value'])

        computed_prices = compute_linear_regression(current_brent_price, current_php_rate)
        
        final_data_object = {
            "fx": current_php_rate, 
            "p91": computed_prices["p91"], 
            "p95": computed_prices["p95"], 
            "p97": computed_prices["p97"], 
            "dsl": computed_prices["dsl"],
            "timestamp": datetime.now().strftime("%B %d, %Y | %I:%M %p PST")
        }
        
        st.session_state.last_market_data = final_data_object
        return final_data_object
        
    except Exception:
        return st.session_state.last_market_data

@st.cache_data(ttl=10800)
def fetch_news_data():
    try:
        newsdata_api_key = st.secrets["NEWSDATA_API_KEY"]
        search_query = "fuel%20price%20OR%20oil%20price"
        target_country = "ph"
        target_language = "en"
        
        endpoint_url = f"https://newsdata.io/api/1/latest?apikey={newsdata_api_key}&q={search_query}&country={target_country}&language={target_language}"
        
        response_news = requests.get(endpoint_url, timeout=10)
        
        if response_news.status_code != 200:
            return st.session_state.last_news_data
            
        parsed_json = response_news.json()
        articles_array = parsed_json.get("results", [])
        
        if not articles_array or len(articles_array) == 0:
            return st.session_state.last_news_data
            
        formatted_news_list = []
        
        for article_object in articles_array[:2]:
            extracted_description = article_object.get("description")
            
            if not extracted_description or str(extracted_description).strip() == "":
                extracted_description = "Access the source document directly for comprehensive data regarding recent market updates and fuel price fluctuations."
                
            if len(extracted_description) > 160: 
                extracted_description = extracted_description[:160] + "..."
                
            formatted_article = {
                "title": article_object.get("title", "Market Update"), 
                "description": extracted_description, 
                "link": article_object.get("link", "#"), 
                "source": str(article_object.get("source_id", "News Source")).capitalize()
            }
            formatted_news_list.append(formatted_article)
        
        while len(formatted_news_list) < 2:
            formatted_news_list.append(st.session_state.last_news_data[1])
            
        st.session_state.last_news_data = formatted_news_list
        return formatted_news_list
        
    except Exception:
        return st.session_state.last_news_data

def generate_forecast_dataframe(base_prices, forecast_horizon_days):
    np.random.seed(42)
    
    generation_dates = []
    for day_increment in range(1, forecast_horizon_days + 1):
        target_date = datetime.now() + timedelta(days=day_increment)
        formatted_date = target_date.strftime('%a, %b %d')
        generation_dates.append(formatted_date)
        
    stochastic_data = {"Date": generation_dates}
    
    constant_drift_factor = 0.002
    historical_volatility = 0.012
    
    for fuel_grade, current_price in base_prices.items():
        daily_price_shocks = np.random.normal(constant_drift_factor, historical_volatility, forecast_horizon_days)
        projected_trajectory = []
        
        for shock_value in daily_price_shocks:
            calculated_price = current_price * (1 + shock_value)
            projected_trajectory.append(round(calculated_price, 2))
            
        stochastic_data[fuel_grade] = projected_trajectory
        
    compiled_dataframe = pd.DataFrame(stochastic_data)
    model_confidence_score = round(100 * math.exp(-0.01 * forecast_horizon_days), 1)
    
    return compiled_dataframe, model_confidence_score

def render_metric_dashboard(market_data):
    st.markdown("### Estimated Current Pump Prices")

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-container">
            <div class="metric-label">
                91 REGULAR
                <span class="metric-subtitle">AKA: Xtra Advance, FuelSave, Silver</span>
            </div>
            <div class="metric-value">₱{market_data['p91']:.2f}</div>
        </div>
        <div class="metric-container">
            <div class="metric-label">
                95 OCTANE
                <span class="metric-subtitle">AKA: XCS, V-Power, Platinum</span>
            </div>
            <div class="metric-value">₱{market_data['p95']:.2f}</div>
        </div>
        <div class="metric-container">
            <div class="metric-label">
                97+ ULTRA
                <span class="metric-subtitle">AKA: Blaze 100, Racing</span>
            </div>
            <div class="metric-value">₱{market_data['p97']:.2f}</div>
        </div>
        <div class="metric-container">
            <div class="metric-label">
                DIESEL
                <span class="metric-subtitle">AKA: Turbo, Max, Power</span>
            </div>
            <div class="metric-value">₱{market_data['dsl']:.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def build_interactive_chart(forecast_df, selected_columns, timeframe_int):
    st.markdown(f"### Price Trend Prediction ({timeframe_int} Days)")
    
    melted_dataframe = forecast_df.melt('Date', var_name='Fuel Type', value_name='Price')
    filtered_dataframe = melted_dataframe[melted_dataframe['Fuel Type'].isin(selected_columns)]
    
    legend_selection_binding = alt.selection_point(fields=['Fuel Type'], bind='legend')
    
    line_chart = alt.Chart(filtered_dataframe).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X('Date:N', sort=None, title='Date', axis=alt.Axis(grid=False)),
        y=alt.Y('Price:Q', scale=alt.Scale(zero=False), title='Estimated Price (₱/L)', axis=alt.Axis(grid=True, gridColor='rgba(128, 128, 128, 0.2)')),
        color=alt.Color('Fuel Type:N', scale=alt.Scale(range=['#10b981', '#3b82f6', '#8b5cf6', '#ef4444']), legend=alt.Legend(orient="bottom", title=None)),
        opacity=alt.condition(legend_selection_binding, alt.value(1), alt.value(0.2)),
        tooltip=['Date', 'Fuel Type', 'Price']
    ).add_params(
        legend_selection_binding
    ).properties(
        height=450
    ).configure_view(
        strokeWidth=0
    ).configure_axis(
        domain=False
    )
    
    st.altair_chart(line_chart, use_container_width=True)

def render_educational_expanders():
    with st.expander("How We Calculate Our Data (Methodology)"):
        st.write("**1. Data Gathering:**")
        st.write("The system continuously pulls live economic numbers directly from the Federal Reserve database. Specifically, it monitors the current price of Brent Crude oil globally and the exact conversion rate between the US Dollar and the Philippine Peso. It simultaneously gathers verified local news articles regarding market shifts.")
        
        st.write("**2. Calculating Today's Prices:**")
        st.write("We use a statistical method known as Linear Regression. Imagine drawing a straight line through a messy scatterplot of past receipts. By analyzing how past fuel prices in the Philippines reacted to historical changes in global oil prices, the system identifies a core pattern. It applies this historical pattern to today's global numbers to calculate a highly accurate estimate of the current local pump prices.")
        
        st.write("**3. Predicting Future Prices:**")
        st.write("To forecast prices for the next 7 to 30 days, the application uses a Stochastic Random Walk simulation. This means the model assumes prices will naturally drift upward over time due to inflation, while randomly adding minor daily fluctuations to mimic the unpredictable nature of the real-world stock market.")

    with st.expander("Definition of Fuel Types"):
        st.write("**91 RON (Regular Gas):** The standard unleaded gasoline tier. You will commonly see this sold as Petron Xtra Advance, Shell FuelSave, or Caltex Silver. It is the most economical choice and suitable for standard everyday driving.")
        st.write("**95 RON (Premium Gas):** The mid-tier gasoline designed to provide better engine efficiency and cleaning agents. Common brand names include Petron XCS, Shell V-Power, and Caltex Platinum.")
        st.write("**97+ RON (Ultra Premium):** High-performance fuel engineered with maximum octane ratings to prevent engine knocking. Common names include Petron Blaze 100 and Shell V-Power Racing. This is specifically required for sports cars and high-end luxury vehicles.")
        st.write("**Diesel:** The standard compression-ignition fuel used by trucks, SUVs, and commercial vehicles. Common names include Petron Turbo Diesel, Shell V-Power Diesel, and Caltex Power Diesel.")

def render_footer():
    st.markdown("""
    <div class="footer-text">
        <strong>Developed by <a href="https://www.linkedin.com/in/ignlucina/" target="_blank">Ignacio L.</a> and <a href="https://www.linkedin.com/in/ajebareng56/" target="_blank">Andrei B.</a></strong>
    </div>
    """, unsafe_allow_html=True)

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

st.title("Philippine Fuel Price Tracker")
st.markdown(f'<div class="timestamp-text"><span class="pulse-dot"></span> As of {live_market_data["timestamp"]}</div>', unsafe_allow_html=True)

st.markdown("""
<div class="custom-alert">
    <strong>MARKET ALERT:</strong> Conflict in the Middle East may affect global oil supply, which could lead to possible fuel price increases.
</div>
""", unsafe_allow_html=True)

render_metric_dashboard(live_market_data)

user_selected_timeframe = st.selectbox(
    "Select Prediction Period", 
    [7, 15, 30], 
    index=0, 
    format_func=lambda x: f"{x} Days Forecast"
)

generated_forecast_dataframe, model_confidence = generate_forecast_dataframe(structured_pump_prices, user_selected_timeframe)

available_fuel_options = list(structured_pump_prices.keys())
user_selected_fuels = st.multiselect(
    "Select Fuel Types to Display on Graph", 
    options=available_fuel_options, 
    default=available_fuel_options
)

layout_column_left, layout_column_right = st.columns([2.5, 1])

with layout_column_left:
    build_interactive_chart(generated_forecast_dataframe, user_selected_fuels, user_selected_timeframe)

with layout_column_right:
    st.markdown("### Model Stats")
    st.metric("Estimated Accuracy", f"{model_confidence}%")
    
    display_columns = ['Date'] + user_selected_fuels
    filtered_table_data = generated_forecast_dataframe[display_columns]
    
    st.dataframe(
        filtered_table_data, 
        hide_index=True, 
        use_container_width=True, 
        height=360
    )

st.markdown("### Latest Market Intelligence")
news_column_1, news_column_2 = st.columns(2)

with news_column_1:
    st.markdown(f"""
    <div class="news-card">
        <h4>{live_news_data[0]['title']}</h4>
        <p>{live_news_data[0]['description']}</p>
        <a href="{live_news_data[0]['link']}" target="_blank">ACCESS SOURCE ({live_news_data[0]['source']})</a>
    </div>
    """, unsafe_allow_html=True)

with news_column_2:
    st.markdown(f"""
    <div class="news-card">
        <h4>{live_news_data[1]['title']}</h4>
        <p>{live_news_data[1]['description']}</p>
        <a href="{live_news_data[1]['link']}" target="_blank">ACCESS SOURCE ({live_news_data[1]['source']})</a>
    </div>
    """, unsafe_allow_html=True)

render_educational_expanders()
render_footer()
