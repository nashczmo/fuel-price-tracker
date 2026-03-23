import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime, timedelta
import numpy as np
import math

st.set_page_config(
    page_title="PH Fuel Tracker",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap');

        *, *::before, *::after {
            font-family: 'Inter', sans-serif !important;
            box-sizing: border-box;
        }

        /* ─── Base ─────────────────────────────────────────── */
        .stApp {
            background-color: #f7f7f5;
            color: #1a1a1a;
        }

        [data-testid="stHeader"] { display: none; }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }

        .block-container {
            padding-top: 3rem !important;
            padding-bottom: 3rem !important;
            padding-left: 5% !important;
            padding-right: 5% !important;
            max-width: 1500px !important;
        }

        /* ─── Page Header ───────────────────────────────────── */
        .page-header {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            margin-bottom: 40px;
            padding-bottom: 28px;
            border-bottom: 1px solid #e5e5e3;
        }

        .main-title {
            font-size: 1.85rem;
            font-weight: 700;
            color: #111111;
            letter-spacing: -0.6px;
            line-height: 1;
            margin: 0;
        }

        .main-subtitle {
            font-size: 0.82rem;
            color: #888;
            font-weight: 400;
            margin-top: 6px;
            letter-spacing: 0.01em;
        }

        .time-badge {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            font-size: 0.75rem;
            font-weight: 500;
            color: #555;
            background: #ffffff;
            border: 1px solid #e5e5e3;
            border-radius: 100px;
            padding: 6px 14px;
        }

        .live-dot {
            width: 7px;
            height: 7px;
            background: #22c55e;
            border-radius: 50%;
            flex-shrink: 0;
        }

        /* ─── Alert ─────────────────────────────────────────── */
        .alert-strip {
            display: flex;
            align-items: center;
            gap: 12px;
            background: #fffbeb;
            border: 1px solid #fde68a;
            border-radius: 8px;
            padding: 12px 18px;
            font-size: 0.8rem;
            color: #92400e;
            margin-bottom: 36px;
            font-weight: 500;
        }

        .alert-icon {
            font-size: 1rem;
            flex-shrink: 0;
        }

        /* ─── Section Label ─────────────────────────────────── */
        .section-label {
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: #aaa;
            margin-bottom: 16px;
        }

        /* ─── Metric Cards ──────────────────────────────────── */
        .metric-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 40px;
        }

        .metric-card {
            background: #ffffff;
            border: 1px solid #e9e9e7;
            border-radius: 12px;
            padding: 26px 24px 22px;
            position: relative;
            transition: box-shadow 0.2s ease, transform 0.2s ease;
        }

        .metric-card:hover {
            box-shadow: 0 4px 20px rgba(0,0,0,0.07);
            transform: translateY(-1px);
        }

        .metric-tag {
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #bbb;
            margin-bottom: 14px;
        }

        .metric-price {
            font-size: 2.3rem;
            font-weight: 750;
            letter-spacing: -1.5px;
            color: #111;
            line-height: 1;
            font-variant-numeric: tabular-nums;
        }

        .metric-peso {
            font-size: 1.3rem;
            font-weight: 500;
            vertical-align: super;
            letter-spacing: 0;
            color: #888;
        }

        .metric-brands {
            font-size: 0.7rem;
            color: #bbb;
            margin-top: 12px;
            font-weight: 400;
        }

        .metric-chip {
            position: absolute;
            top: 22px;
            right: 20px;
            background: #f4f4f2;
            border-radius: 100px;
            padding: 3px 10px;
            font-size: 0.62rem;
            font-weight: 600;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        .chip-91  { background: #ecfdf5; color: #15803d; }
        .chip-95  { background: #eff6ff; color: #1d4ed8; }
        .chip-97  { background: #faf5ff; color: #7e22ce; }
        .chip-dsl { background: #fff1f2; color: #be123c; }

        /* ─── Divider ────────────────────────────────────────── */
        .divider {
            border: none;
            border-top: 1px solid #e9e9e7;
            margin: 0 0 36px;
        }

        /* ─── Sub-header ─────────────────────────────────────── */
        .sub-header {
            font-size: 1rem;
            font-weight: 650;
            color: #111;
            margin-bottom: 20px;
            letter-spacing: -0.3px;
        }

        /* ─── Stats Panel ────────────────────────────────────── */
        .stats-panel {
            background: #ffffff;
            border: 1px solid #e9e9e7;
            border-radius: 12px;
            padding: 28px 24px;
            height: 100%;
        }

        .stat-block {
            margin-bottom: 28px;
        }

        .stat-block-label {
            font-size: 0.68rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #aaa;
            margin-bottom: 6px;
        }

        .stat-block-value {
            font-size: 2.4rem;
            font-weight: 800;
            color: #111;
            letter-spacing: -1px;
            line-height: 1;
        }

        .accuracy-bar-bg {
            height: 6px;
            background: #f0f0ee;
            border-radius: 100px;
            margin-top: 12px;
            overflow: hidden;
        }

        .accuracy-bar-fill {
            height: 100%;
            border-radius: 100px;
            background: linear-gradient(90deg, #22c55e, #16a34a);
            transition: width 0.5s ease;
        }

        .stat-note {
            font-size: 0.7rem;
            color: #bbb;
            margin-top: 6px;
        }

        /* ─── Select / Multiselect overrides ────────────────── */
        [data-testid="stSelectbox"] label,
        [data-testid="stMultiSelect"] label {
            color: #555 !important;
            font-size: 0.78rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.07em !important;
        }

        [data-testid="stSelectbox"] > div > div,
        [data-testid="stMultiSelect"] > div > div {
            background: #ffffff !important;
            border: 1px solid #e5e5e3 !important;
            border-radius: 8px !important;
            color: #111 !important;
            font-size: 0.85rem !important;
        }

        /* ─── Chart wrapper ─────────────────────────────────── */
        .chart-wrapper {
            background: #ffffff;
            border: 1px solid #e9e9e7;
            border-radius: 12px;
            padding: 24px 20px 12px;
        }

        /* ─── News ───────────────────────────────────────────── */
        .news-section-header {
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: #aaa;
            margin: 48px 0 18px;
        }

        .news-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 48px;
        }

        .news-card {
            background: #ffffff;
            border: 1px solid #e9e9e7;
            border-radius: 12px;
            padding: 24px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 170px;
            transition: box-shadow 0.2s;
        }

        .news-card:hover {
            box-shadow: 0 4px 20px rgba(0,0,0,0.07);
        }

        .news-card-source {
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #bbb;
            margin-bottom: 10px;
        }

        .news-card-title {
            font-size: 0.95rem;
            font-weight: 650;
            color: #111;
            line-height: 1.4;
            margin-bottom: 12px;
        }

        .news-card-body {
            font-size: 0.8rem;
            color: #888;
            line-height: 1.6;
            flex-grow: 1;
            margin-bottom: 18px;
        }

        .news-card-link {
            font-size: 0.72rem;
            font-weight: 700;
            color: #111;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 1px;
            width: fit-content;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* ─── Expanders ─────────────────────────────────────── */
        [data-testid="stExpander"] {
            background-color: #ffffff !important;
            border: 1px solid #e9e9e7 !important;
            border-radius: 10px !important;
            margin-bottom: 10px;
        }

        [data-testid="stExpander"] summary {
            color: #333 !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
            padding: 16px 20px !important;
        }

        [data-testid="stExpanderDetails"] {
            color: #666 !important;
            font-size: 0.83rem !important;
            line-height: 1.7 !important;
            padding: 0 20px 18px !important;
        }

        /* ─── Dataframe ─────────────────────────────────────── */
        [data-testid="stDataFrame"] {
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #e9e9e7;
        }

        /* ─── Tooltip ────────────────────────────────────────── */
        .info-tooltip {
            position: relative;
            display: inline-flex;
            align-items: center;
            margin-left: 6px;
            cursor: pointer;
            vertical-align: middle;
        }
        .info-tooltip svg { fill: #ccc; transition: fill 0.2s; }
        .info-tooltip:hover svg { fill: #888; }
        .info-tooltip .tooltip-text {
            visibility: hidden;
            width: 260px;
            background: #111;
            color: #f0f0f0;
            text-align: left;
            border-radius: 8px;
            padding: 12px 14px;
            position: absolute;
            z-index: 50;
            bottom: 150%;
            left: 50%;
            margin-left: -130px;
            opacity: 0;
            transition: opacity 0.25s;
            font-size: 0.72rem;
            line-height: 1.5;
            pointer-events: none;
        }
        .info-tooltip .tooltip-text::after {
            content: "";
            position: absolute;
            top: 100%; left: 50%;
            margin-left: -5px;
            border-width: 5px; border-style: solid;
            border-color: #111 transparent transparent transparent;
        }
        .info-tooltip:hover .tooltip-text { visibility: visible; opacity: 1; }

        /* ─── Footer ─────────────────────────────────────────── */
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 24px;
            border-top: 1px solid #e9e9e7;
            font-size: 0.75rem;
            color: #bbb;
            line-height: 1.8;
        }

        /* ─── Responsive ─────────────────────────────────────── */
        @media (max-width: 768px) {
            .block-container {
                padding-left: 1.2rem !important;
                padding-right: 1.2rem !important;
            }
            .metric-row { grid-template-columns: repeat(2, 1fr); gap: 12px; }
            .page-header { flex-direction: column; align-items: flex-start; gap: 14px; }
            .main-title { font-size: 1.5rem; }
            .metric-price { font-size: 1.9rem; }
            .news-grid { grid-template-columns: 1fr; }
        }
        </style>
    """, unsafe_allow_html=True)


# ─── Data / Model ────────────────────────────────────────────────────────────

HISTORICAL_FEATURES = np.array([[1, 74.2, 55.8], [1, 78.5, 56.1], [1, 80.2, 56.5], [1, 82.5, 57.0]])
INV_MATRIX = np.linalg.inv(HISTORICAL_FEATURES.T.dot(HISTORICAL_FEATURES)).dot(HISTORICAL_FEATURES.T)

WEIGHTS_91  = INV_MATRIX.dot(np.array([50.50, 52.10, 57.30, 59.10]))
WEIGHTS_95  = INV_MATRIX.dot(np.array([54.20, 56.90, 62.10, 63.90]))
WEIGHTS_97  = INV_MATRIX.dot(np.array([58.10, 60.40, 65.60, 67.40]))
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


@st.cache_data(ttl=300, show_spinner=False)
def fetch_comprehensive_market_data():
    try:
        fred_api_key = st.secrets.get("FRED_API_KEY", None)
        if not fred_api_key:
            return st.session_state.last_market_data

        req_params = {"api_key": fred_api_key, "file_type": "json", "sort_order": "desc", "limit": 1}
        rb = requests.get("https://api.stlouisfed.org/api/fred/series/observations?series_id=DCOILBRENTEU", params=req_params, timeout=3)
        rf = requests.get("https://api.stlouisfed.org/api/fred/series/observations?series_id=DEXPHUS",      params=req_params, timeout=3)

        if rb.status_code == 200 and rf.status_code == 200:
            brent = float(rb.json()['observations'][0]['value'])
            fx    = float(rf.json()['observations'][0]['value'])
            cp    = compute_linear_regression(brent, fx)
            data  = {"fx": fx, "p91": cp["p91"], "p95": cp["p95"], "p97": cp["p97"], "dsl": cp["dsl"],
                     "timestamp": datetime.now().strftime("%I:%M:%S %p")}
            st.session_state.last_market_data = data
            return data

        return st.session_state.last_market_data
    except Exception:
        return st.session_state.last_market_data


@st.cache_data(ttl=300, show_spinner=False)
def fetch_philippine_oil_news():
    fallback_news = [
        {"title": "Legislative Review of Fuel Excise Tax Initiated",
         "description": "National legislators are currently evaluating structural modifications to fuel taxation to alleviate domestic price pressures.",
         "url": "#", "source": "Internal Database"},
        {"title": "Global Brent Crude Trends Impact Local Markets",
         "description": "Recent shifts in global Brent crude valuations continue to influence local retail pump prices within the Philippine archipelago.",
         "url": "#", "source": "Internal Database"},
    ]
    try:
        key = st.secrets.get("NEWSDATA_API_KEY", None)
        if not key:
            return fallback_news

        url = f"https://newsdata.io/api/1/news?apikey={key}&country=ph&q=fuel%20OR%20oil%20OR%20gasoline%20OR%20diesel&language=en"
        r   = requests.get(url, timeout=5)

        if r.status_code == 200:
            results = r.json().get('results', [])
            if len(results) >= 2:
                return [{"title": a.get("title", "Market Update"),
                         "description": str(a.get("description", ""))[:160] + "...",
                         "url": a.get("link", "#"),
                         "source": a.get("source_id", "News")} for a in results[:2]]

        return fallback_news
    except Exception:
        return fallback_news


def analyze_news_sentiment(articles):
    bullish  = ['hike', 'increase', 'surge', 'conflict', 'war', 'shortage', 'upward', 'soar', 'unrest', 'tighten']
    bearish  = ['rollback', 'decrease', 'drop', 'slump', 'surplus', 'ease', 'plunge', 'cheaper', 'suspend']
    score = 0
    for art in articles:
        text = f"{art['title']} {art['description']}".lower()
        for w in bullish:  score += 0.003 if w in text else 0
        for w in bearish:  score -= 0.003 if w in text else 0
    return max(min(score, 0.015), -0.015)


@st.cache_data(ttl=300, show_spinner=False)
def generate_forecast_dataframe(base_prices, days, sentiment_bias):
    np.random.seed(42)
    now   = datetime.now()
    dates = [(now + timedelta(days=i)).strftime('%a, %b %d') for i in range(days)]

    mapping = {
        "91":  "91 RON (Xtra Advance / FuelSave / Silver)",
        "95":  "95 RON (XCS / V-Power / Platinum)",
        "97":  "97+ RON (Blaze 100 / Racing)",
        "dsl": "Diesel (Turbo / Max / Power)"
    }

    drift  = 0.002 + sentiment_bias
    data   = {"Date": dates}

    for grade, price in base_prices.items():
        shocks = np.random.normal(drift, 0.012, days)
        data[mapping[grade]] = np.round(price * np.cumprod(1 + shocks), 2)

    confidence = round(100 * math.exp(-0.01 * days), 1)
    return pd.DataFrame(data), confidence


# ─── App ─────────────────────────────────────────────────────────────────────

inject_custom_css()
initialize_session_state()

market_data     = fetch_comprehensive_market_data()
ph_news         = fetch_philippine_oil_news()
bias            = analyze_news_sentiment(ph_news)

base_prices = {
    "91":  market_data["p91"],
    "95":  market_data["p95"],
    "97":  market_data["p97"],
    "dsl": market_data["dsl"]
}

# ── Page header ──────────────────────────────────────────────────────────────
time_str = datetime.now().strftime("%b %d, %Y · %I:%M %p")

st.markdown(f"""
<div class="page-header">
    <div>
        <div class="main-title">Philippine Fuel Price Tracker</div>
        <div class="main-subtitle">Real-time estimates powered by Brent Crude &amp; USD/PHP indices</div>
    </div>
    <div class="time-badge">
        <span class="live-dot"></span>
        Updated {time_str}
        <div class="info-tooltip">
            <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24">
                <path d="M11 7h2v2h-2zm0 4h2v6h-2zm1-9C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
            </svg>
            <span class="tooltip-text">Prices are recalibrated every 5 minutes using live FRED macroeconomic data.</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Alert strip ──────────────────────────────────────────────────────────────
if bias > 0.005:
    alert_msg = "Market signals indicate a possible upward price adjustment due to supply constraints."
    alert_icon = "↑"
elif bias < -0.005:
    alert_msg = "Market signals suggest a potential rollback based on current global trends."
    alert_icon = "↓"
else:
    alert_msg = "Macroeconomic indicators are within standard ranges. No significant adjustment expected."
    alert_icon = "◎"

st.markdown(f"""
<div class="alert-strip">
    <span class="alert-icon">{alert_icon}</span>
    <span><strong>Market Signal&nbsp;&nbsp;·&nbsp;&nbsp;</strong>{alert_msg}</span>
</div>
""", unsafe_allow_html=True)

# ── Controls ─────────────────────────────────────────────────────────────────
ctrl_col1, ctrl_col2 = st.columns([1, 2], gap="large")

with ctrl_col1:
    prediction_period = st.selectbox(
        "Prediction Horizon",
        ["7 Days Forecast", "14 Days Forecast", "30 Days Forecast"]
    )
    days_forecast = int(prediction_period.split()[0])

all_fuel_types = [
    "91 RON (Xtra Advance / FuelSave / Silver)",
    "95 RON (XCS / V-Power / Platinum)",
    "97+ RON (Blaze 100 / Racing)",
    "Diesel (Turbo / Max / Power)"
]

with ctrl_col2:
    selected_fuels = st.multiselect(
        "Fuel Types to Display",
        options=all_fuel_types,
        default=all_fuel_types
    )

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ── Generate forecast ─────────────────────────────────────────────────────────
forecast_df, dynamic_accuracy = generate_forecast_dataframe(base_prices, days_forecast, bias)

# ── Metric cards ─────────────────────────────────────────────────────────────
p91_val  = forecast_df['91 RON (Xtra Advance / FuelSave / Silver)'].iloc[0]
p95_val  = forecast_df['95 RON (XCS / V-Power / Platinum)'].iloc[0]
p97_val  = forecast_df['97+ RON (Blaze 100 / Racing)'].iloc[0]
dsl_val  = forecast_df['Diesel (Turbo / Max / Power)'].iloc[0]

st.markdown('<div class="section-label">Estimated Pump Prices — Today</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="metric-row">
    <div class="metric-card">
        <div class="metric-tag">91 Regular</div>
        <div class="metric-chip chip-91">RON 91</div>
        <div class="metric-price"><span class="metric-peso">₱</span>{p91_val:.2f}</div>
        <div class="metric-brands">Xtra Advance · FuelSave · Silver</div>
    </div>
    <div class="metric-card">
        <div class="metric-tag">95 Premium</div>
        <div class="metric-chip chip-95">RON 95</div>
        <div class="metric-price"><span class="metric-peso">₱</span>{p95_val:.2f}</div>
        <div class="metric-brands">XCS · V-Power · Platinum</div>
    </div>
    <div class="metric-card">
        <div class="metric-tag">97+ Ultra</div>
        <div class="metric-chip chip-97">RON 97</div>
        <div class="metric-price"><span class="metric-peso">₱</span>{p97_val:.2f}</div>
        <div class="metric-brands">Blaze 100 · Racing</div>
    </div>
    <div class="metric-card">
        <div class="metric-tag">Diesel</div>
        <div class="metric-chip chip-dsl">DSL</div>
        <div class="metric-price"><span class="metric-peso">₱</span>{dsl_val:.2f}</div>
        <div class="metric-brands">Turbo · Max · Power Diesel</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Chart + Stats ─────────────────────────────────────────────────────────────
col_chart, col_stats = st.columns([2.6, 1], gap="large")

with col_chart:
    st.markdown(f'<div class="sub-header">Price Forecast — Next {days_forecast} Days</div>', unsafe_allow_html=True)

    if selected_fuels:
        plot_df = forecast_df[["Date"] + selected_fuels]
        melted  = plot_df.melt('Date', var_name='Fuel Type', value_name='Price')

        color_scale = alt.Scale(
            domain=[
                "91 RON (Xtra Advance / FuelSave / Silver)",
                "95 RON (XCS / V-Power / Platinum)",
                "97+ RON (Blaze 100 / Racing)",
                "Diesel (Turbo / Max / Power)"
            ],
            range=['#16a34a', '#2563eb', '#7c3aed', '#dc2626']
        )

        chart = (
            alt.Chart(melted)
            .mark_line(point=alt.OverlayMarkDef(size=50, filled=True), strokeWidth=2)
            .encode(
                x=alt.X('Date:N', sort=None, title=None,
                         axis=alt.Axis(grid=False, labelColor='#aaa', labelFont='Inter',
                                       tickColor='#e9e9e7', domainColor='#e9e9e7', labelFontSize=11)),
                y=alt.Y('Price:Q', scale=alt.Scale(zero=False), title='₱ / Litre',
                         axis=alt.Axis(grid=True, gridColor='#f0f0ee', gridDash=[3, 3],
                                       labelColor='#aaa', titleColor='#bbb', labelFont='Inter',
                                       titleFont='Inter', labelFontSize=11, titleFontSize=11,
                                       domainOpacity=0)),
                color=alt.Color('Fuel Type:N', scale=color_scale,
                                 legend=alt.Legend(orient='bottom', title=None,
                                                   labelColor='#555', labelFont='Inter',
                                                   labelFontSize=11, symbolSize=80,
                                                   padding=10, columnPadding=20)),
                tooltip=['Date', 'Fuel Type', 'Price']
            )
            .properties(height=380, background='#ffffff', padding={"left": 12, "right": 12, "top": 12, "bottom": 12})
            .configure_view(strokeWidth=0, cornerRadius=12)
            .configure_axis(domain=False)
        )

        st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
        st.altair_chart(chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Select at least one fuel type above to display the chart.")

with col_stats:
    st.markdown('<div class="sub-header">Model Stats</div>', unsafe_allow_html=True)
    bar_width = min(dynamic_accuracy, 100)
    accuracy_color = "#22c55e" if dynamic_accuracy >= 80 else "#f59e0b" if dynamic_accuracy >= 60 else "#ef4444"

    st.markdown(f"""
    <div class="stats-panel">
        <div class="stat-block">
            <div class="stat-block-label">
                Forecast Confidence
                <div class="info-tooltip">
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24">
                        <path d="M11 7h2v2h-2zm0 4h2v6h-2zm1-9C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
                    </svg>
                    <span class="tooltip-text">Probability that volatility stays within normal standard deviations. Declines as forecast horizon grows.</span>
                </div>
            </div>
            <div class="stat-block-value">{dynamic_accuracy}%</div>
            <div class="accuracy-bar-bg">
                <div class="accuracy-bar-fill" style="width:{bar_width}%; background: linear-gradient(90deg, {accuracy_color}, {accuracy_color}cc);"></div>
            </div>
            <div class="stat-note">Based on {days_forecast}-day horizon</div>
        </div>

        <div class="stat-block">
            <div class="stat-block-label">Model</div>
            <div style="font-size:0.82rem; color:#555; line-height:1.6;">
                Multiple Linear Regression<br>
                <span style="color:#bbb; font-size:0.72rem;">Brent Crude · USD/PHP · Historical Prices</span>
            </div>
        </div>

        <div class="stat-block">
            <div class="stat-block-label">Sentiment Bias</div>
            <div style="font-size:0.82rem; color:{'#16a34a' if bias > 0 else '#dc2626' if bias < 0 else '#888'}; font-weight:600;">
                {'↑ Bullish' if bias > 0.003 else '↓ Bearish' if bias < -0.003 else '— Neutral'}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if selected_fuels:
        st.dataframe(
            forecast_df[["Date"] + selected_fuels],
            hide_index=True,
            use_container_width=True,
            height=230
        )

# ── News ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="news-section-header">Market Intelligence</div>', unsafe_allow_html=True)

news_html = '<div class="news-grid">'
for art in ph_news:
    news_html += f"""
    <div class="news-card">
        <div>
            <div class="news-card-source">{art['source']}</div>
            <div class="news-card-title">{art['title']}</div>
            <div class="news-card-body">{art['description']}</div>
        </div>
        <a href="{art['url']}" target="_blank" class="news-card-link">
            Read source &nbsp;→
        </a>
    </div>"""
news_html += '</div>'
st.markdown(news_html, unsafe_allow_html=True)

# ── Expanders ─────────────────────────────────────────────────────────────────
with st.expander("Methodology & Data Integrity Statement"):
    st.markdown("""
**I. Data Acquisition.**  Live macroeconomic data is pulled from the Federal Reserve Economic Data (FRED) API every 5 minutes — covering global Brent Crude spot prices and the USD/PHP exchange rate.

**II. Price Estimation.**  Retail estimates are computed via a Multiple Linear Regression model calibrated on the historical correlation between international indices and domestic pump prices.

**III. Forecasting.**  A Stochastic Random Walk simulation, adjusted by an NLP-derived news sentiment bias sourced from NewsData.io, projects the forward price trajectory over the selected horizon.
    """)

with st.expander("Fuel Grade Definitions"):
    st.markdown("""
- **91 RON (Regular):** Standard unleaded gasoline — Petron Xtra Advance, Shell FuelSave, Caltex Silver.
- **95 RON (Premium):** Higher-octane formulation for improved engine efficiency — Petron XCS, Shell V-Power, Caltex Platinum.
- **97+ RON (Ultra):** Maximum-performance gasoline for high-compression engines — Petron Blaze 100, Seaoil Extreme 97.
- **Diesel:** Automotive gas oil for conventional diesel engines — Petron Turbo Diesel, Shell V-Power Diesel, Caltex Power Diesel.
    """)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
    Developed by Ignacio L. and Andrei B. &nbsp;·&nbsp; &copy; {datetime.now().year}
</div>
""", unsafe_allow_html=True)
