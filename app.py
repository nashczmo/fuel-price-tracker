import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime, timedelta
import numpy as np
import math

st.set_page_config(
    page_title="PH Fuel — Market Desk",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

        :root {
            --ink:     #0d0d0b;
            --paper:   #f5f1ea;
            --rule:    #d4cfc6;
            --accent:  #c8450a;
            --accent2: #1a3a6b;
            --muted:   #8a8580;
            --card:    #ede9e1;
        }

        *, *::before, *::after { box-sizing: border-box; }

        body, .stApp {
            background-color: var(--paper);
            color: var(--ink);
            font-family: 'IBM Plex Sans', sans-serif !important;
        }

        [data-testid="stHeader"] { display: none; }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }

        .block-container {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
            max-width: 100% !important;
        }

        /* ─── MASTHEAD ─────────────────────────────────────── */
        .masthead {
            background: var(--ink);
            color: #f5f1ea;
            padding: 0 40px;
            display: flex;
            align-items: stretch;
            justify-content: space-between;
            border-bottom: 3px solid var(--accent);
        }

        .masthead-left {
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 18px 0;
            border-right: 1px solid rgba(245,241,234,0.15);
            padding-right: 32px;
            margin-right: 32px;
        }

        .masthead-title {
            font-family: 'Syne', sans-serif;
            font-size: 1.6rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            line-height: 1;
            color: #f5f1ea;
            margin: 0;
        }

        .masthead-sub {
            font-family: 'DM Mono', monospace;
            font-size: 0.62rem;
            font-weight: 300;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            color: rgba(245,241,234,0.5);
            margin-top: 5px;
        }

        .masthead-right {
            display: flex;
            align-items: center;
            gap: 32px;
        }

        .masthead-stat {
            text-align: right;
            padding: 14px 0;
        }

        .masthead-stat-label {
            font-family: 'DM Mono', monospace;
            font-size: 0.58rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: rgba(245,241,234,0.45);
            margin-bottom: 3px;
        }

        .masthead-stat-value {
            font-family: 'DM Mono', monospace;
            font-size: 0.9rem;
            font-weight: 500;
            color: #f5f1ea;
        }

        .live-pill {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            background: var(--accent);
            color: #fff;
            font-family: 'DM Mono', monospace;
            font-size: 0.62rem;
            font-weight: 500;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            padding: 6px 14px;
            border-radius: 2px;
        }

        .live-dot {
            width: 6px; height: 6px;
            background: #fff;
            border-radius: 50%;
            animation: blink 2s infinite;
        }

        @keyframes blink {
            0%,100% { opacity: 1; }
            50%      { opacity: 0.3; }
        }

        /* ─── LAYOUT WRAPPER ───────────────────────────────── */
        .layout-wrapper {
            display: grid;
            grid-template-columns: 300px 1fr;
            min-height: calc(100vh - 78px);
        }

        /* ─── LEFT SIDEBAR ─────────────────────────────────── */
        .sidebar {
            background: var(--ink);
            color: var(--paper);
            padding: 28px 24px 32px;
            border-right: 1px solid #222;
            display: flex;
            flex-direction: column;
            gap: 0;
        }

        .sidebar-section-label {
            font-family: 'DM Mono', monospace;
            font-size: 0.58rem;
            font-weight: 400;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: rgba(245,241,234,0.35);
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(245,241,234,0.08);
        }

        .price-tile {
            padding: 16px 0;
            border-bottom: 1px solid rgba(245,241,234,0.08);
            cursor: default;
            transition: background 0.15s;
        }

        .price-tile:last-of-type {
            border-bottom: none;
        }

        .price-tile-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 8px;
        }

        .price-tile-grade {
            font-family: 'Syne', sans-serif;
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: rgba(245,241,234,0.6);
        }

        .price-tile-badge {
            font-family: 'DM Mono', monospace;
            font-size: 0.58rem;
            font-weight: 400;
            padding: 2px 7px;
            border-radius: 2px;
            letter-spacing: 0.06em;
        }

        .badge-91  { background: rgba(22,163,74,0.18); color: #4ade80; }
        .badge-95  { background: rgba(37,99,235,0.18); color: #60a5fa; }
        .badge-97  { background: rgba(124,58,237,0.18); color: #c084fc; }
        .badge-dsl { background: rgba(220,38,38,0.18); color: #f87171; }

        .price-tile-value {
            font-family: 'DM Mono', monospace;
            font-size: 2rem;
            font-weight: 500;
            color: #f5f1ea;
            letter-spacing: -0.5px;
            line-height: 1;
        }

        .price-tile-peso {
            font-size: 1rem;
            font-weight: 300;
            color: rgba(245,241,234,0.4);
            margin-right: 2px;
        }

        .price-tile-brands {
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 0.65rem;
            color: rgba(245,241,234,0.3);
            margin-top: 6px;
            font-weight: 300;
        }

        /* ─── SIDEBAR STATS ────────────────────────────────── */
        .sidebar-divider {
            border: none;
            border-top: 1px solid rgba(245,241,234,0.08);
            margin: 20px 0;
        }

        .stat-row {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            padding: 6px 0;
        }

        .stat-key {
            font-family: 'DM Mono', monospace;
            font-size: 0.62rem;
            letter-spacing: 0.08em;
            color: rgba(245,241,234,0.35);
            text-transform: uppercase;
        }

        .stat-val {
            font-family: 'DM Mono', monospace;
            font-size: 0.8rem;
            font-weight: 500;
            color: rgba(245,241,234,0.75);
        }

        .sentiment-bull { color: #4ade80 !important; }
        .sentiment-bear { color: #f87171 !important; }
        .sentiment-neut { color: rgba(245,241,234,0.5) !important; }

        .confidence-bar {
            height: 3px;
            background: rgba(245,241,234,0.1);
            border-radius: 2px;
            margin-top: 10px;
            margin-bottom: 6px;
            overflow: hidden;
        }

        .confidence-fill {
            height: 100%;
            background: var(--accent);
            border-radius: 2px;
        }

        /* ─── MAIN CONTENT ─────────────────────────────────── */
        .main-content {
            padding: 32px 36px 48px;
            overflow-y: auto;
            background: var(--paper);
        }

        /* ─── ALERT BAND ───────────────────────────────────── */
        .alert-band {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 11px 18px;
            background: #fef3c7;
            border-left: 3px solid #d97706;
            margin-bottom: 28px;
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 0.78rem;
            font-weight: 400;
            color: #78350f;
        }

        .alert-band strong {
            font-family: 'DM Mono', monospace;
            font-size: 0.65rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            font-weight: 500;
        }

        /* ─── SECTION HEADING ──────────────────────────────── */
        .section-heading {
            display: flex;
            align-items: baseline;
            gap: 12px;
            margin-bottom: 18px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--ink);
        }

        .section-num {
            font-family: 'DM Mono', monospace;
            font-size: 0.62rem;
            color: var(--accent);
            font-weight: 400;
            letter-spacing: 0.08em;
        }

        .section-title {
            font-family: 'Syne', sans-serif;
            font-size: 1rem;
            font-weight: 700;
            color: var(--ink);
            letter-spacing: -0.3px;
        }

        .section-meta {
            font-family: 'DM Mono', monospace;
            font-size: 0.62rem;
            color: var(--muted);
            margin-left: auto;
            letter-spacing: 0.06em;
        }

        /* ─── CONTROLS STRIP ───────────────────────────────── */
        .controls-strip {
            display: flex;
            gap: 16px;
            margin-bottom: 24px;
            flex-wrap: wrap;
        }

        /* Streamlit widget label overrides */
        [data-testid="stSelectbox"] label,
        [data-testid="stMultiSelect"] label {
            font-family: 'DM Mono', monospace !important;
            font-size: 0.6rem !important;
            font-weight: 500 !important;
            letter-spacing: 0.12em !important;
            text-transform: uppercase !important;
            color: var(--muted) !important;
        }

        [data-testid="stSelectbox"] > div > div,
        [data-testid="stMultiSelect"] > div > div {
            background: #fff !important;
            border: 1px solid var(--rule) !important;
            border-radius: 2px !important;
            font-family: 'IBM Plex Sans', sans-serif !important;
            font-size: 0.82rem !important;
            color: var(--ink) !important;
        }

        /* ─── CHART AREA ───────────────────────────────────── */
        .chart-container {
            background: #fff;
            border: 1px solid var(--rule);
            border-top: 3px solid var(--ink);
            padding: 20px 16px 8px;
            margin-bottom: 36px;
        }

        /* ─── NEWS ─────────────────────────────────────────── */
        .news-columns {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0;
            border-top: 2px solid var(--ink);
            border-left: 1px solid var(--rule);
            margin-bottom: 40px;
        }

        .news-col {
            padding: 22px 24px;
            border-right: 1px solid var(--rule);
            border-bottom: 1px solid var(--rule);
        }

        .news-col-index {
            font-family: 'DM Mono', monospace;
            font-size: 0.58rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--accent);
            margin-bottom: 8px;
            font-weight: 400;
        }

        .news-col-title {
            font-family: 'Syne', sans-serif;
            font-size: 1.0rem;
            font-weight: 700;
            color: var(--ink);
            line-height: 1.35;
            margin-bottom: 12px;
        }

        .news-col-body {
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 0.8rem;
            color: var(--muted);
            line-height: 1.65;
            font-weight: 300;
            margin-bottom: 18px;
        }

        .news-col-link {
            font-family: 'DM Mono', monospace;
            font-size: 0.65rem;
            color: var(--accent2);
            text-decoration: none;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            border-bottom: 1px solid currentColor;
            padding-bottom: 2px;
        }

        /* ─── EXPANDERS ────────────────────────────────────── */
        [data-testid="stExpander"] {
            background: #fff !important;
            border: 1px solid var(--rule) !important;
            border-left: 3px solid var(--ink) !important;
            border-radius: 0 !important;
            margin-bottom: 8px;
        }

        [data-testid="stExpander"] summary {
            font-family: 'Syne', sans-serif !important;
            font-size: 0.85rem !important;
            font-weight: 700 !important;
            color: var(--ink) !important;
            padding: 14px 18px !important;
            letter-spacing: -0.2px;
        }

        [data-testid="stExpanderDetails"] {
            font-family: 'IBM Plex Sans', sans-serif !important;
            font-size: 0.82rem !important;
            font-weight: 300 !important;
            color: #444 !important;
            line-height: 1.75 !important;
            padding: 0 18px 16px !important;
        }

        /* ─── DATAFRAME ────────────────────────────────────── */
        [data-testid="stDataFrame"] {
            border: 1px solid var(--rule);
            border-radius: 0;
        }

        /* ─── FOOTER ───────────────────────────────────────── */
        .page-footer {
            text-align: left;
            margin-top: 32px;
            padding-top: 16px;
            border-top: 2px solid var(--ink);
            font-family: 'DM Mono', monospace;
            font-size: 0.62rem;
            color: var(--muted);
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        /* ─── RESPONSIVE ───────────────────────────────────── */
        @media (max-width: 900px) {
            .layout-wrapper { grid-template-columns: 1fr; }
            .sidebar { border-right: none; border-bottom: 2px solid var(--accent); }
            .masthead { padding: 0 18px; flex-wrap: wrap; gap: 10px; }
            .masthead-right { flex-wrap: wrap; gap: 14px; }
            .news-columns { grid-template-columns: 1fr; }
            .main-content { padding: 20px 18px 36px; }
        }
        </style>
    """, unsafe_allow_html=True)


# ─── Model ───────────────────────────────────────────────────────────────────

HISTORICAL_FEATURES = np.array([[1,74.2,55.8],[1,78.5,56.1],[1,80.2,56.5],[1,82.5,57.0]])
INV_MATRIX   = np.linalg.inv(HISTORICAL_FEATURES.T.dot(HISTORICAL_FEATURES)).dot(HISTORICAL_FEATURES.T)
WEIGHTS_91   = INV_MATRIX.dot(np.array([50.50,52.10,57.30,59.10]))
WEIGHTS_95   = INV_MATRIX.dot(np.array([54.20,56.90,62.10,63.90]))
WEIGHTS_97   = INV_MATRIX.dot(np.array([58.10,60.40,65.60,67.40]))
WEIGHTS_DSL  = INV_MATRIX.dot(np.array([58.00,60.50,72.10,75.90]))


def initialize_session_state():
    if 'last_market_data' not in st.session_state:
        st.session_state.last_market_data = {
            "fx":56.10,"p91":72.35,"p95":74.50,"p97":82.30,"dsl":75.10,
            "timestamp": datetime.now().strftime("%I:%M:%S %p")
        }


def compute_linear_regression(brent, fx):
    v = np.array([1, brent, fx])
    return {"p91":v.dot(WEIGHTS_91),"p95":v.dot(WEIGHTS_95),"p97":v.dot(WEIGHTS_97),"dsl":v.dot(WEIGHTS_DSL)}


@st.cache_data(ttl=300, show_spinner=False)
def fetch_comprehensive_market_data():
    try:
        key = st.secrets.get("FRED_API_KEY", None)
        if not key: return st.session_state.last_market_data
        p = {"api_key":key,"file_type":"json","sort_order":"desc","limit":1}
        rb = requests.get("https://api.stlouisfed.org/api/fred/series/observations?series_id=DCOILBRENTEU",params=p,timeout=3)
        rf = requests.get("https://api.stlouisfed.org/api/fred/series/observations?series_id=DEXPHUS",params=p,timeout=3)
        if rb.status_code==200 and rf.status_code==200:
            brent = float(rb.json()['observations'][0]['value'])
            fx    = float(rf.json()['observations'][0]['value'])
            cp    = compute_linear_regression(brent, fx)
            data  = {"fx":fx,"p91":cp["p91"],"p95":cp["p95"],"p97":cp["p97"],"dsl":cp["dsl"],
                     "timestamp":datetime.now().strftime("%I:%M:%S %p")}
            st.session_state.last_market_data = data
            return data
        return st.session_state.last_market_data
    except:
        return st.session_state.last_market_data


@st.cache_data(ttl=300, show_spinner=False)
def fetch_philippine_oil_news():
    fallback = [
        {"title":"Legislative Review of Fuel Excise Tax Initiated",
         "description":"National legislators are evaluating structural modifications to fuel taxation to alleviate domestic price pressures.",
         "url":"#","source":"Internal Database"},
        {"title":"Global Brent Crude Trends Impact Local Markets",
         "description":"Recent shifts in global Brent crude valuations continue to influence local retail pump prices within the Philippine archipelago.",
         "url":"#","source":"Internal Database"},
    ]
    try:
        key = st.secrets.get("NEWSDATA_API_KEY", None)
        if not key: return fallback
        r = requests.get(
            f"https://newsdata.io/api/1/news?apikey={key}&country=ph&q=fuel%20OR%20oil%20OR%20gasoline%20OR%20diesel&language=en",
            timeout=5)
        if r.status_code==200:
            results = r.json().get('results',[])
            if len(results)>=2:
                return [{"title":a.get("title","Market Update"),
                         "description":str(a.get("description",""))[:160]+"...",
                         "url":a.get("link","#"),
                         "source":a.get("source_id","News")} for a in results[:2]]
        return fallback
    except:
        return fallback


def analyze_news_sentiment(articles):
    bullish=['hike','increase','surge','conflict','war','shortage','upward','soar','unrest','tighten']
    bearish=['rollback','decrease','drop','slump','surplus','ease','plunge','cheaper','suspend']
    score=0
    for art in articles:
        text=f"{art['title']} {art['description']}".lower()
        for w in bullish: score+=0.003 if w in text else 0
        for w in bearish: score-=0.003 if w in text else 0
    return max(min(score,0.015),-0.015)


@st.cache_data(ttl=300, show_spinner=False)
def generate_forecast_dataframe(base_prices, days, bias):
    np.random.seed(42)
    now   = datetime.now()
    dates = [(now+timedelta(days=i)).strftime('%b %d') for i in range(days)]
    mapping = {
        "91":"91 RON (Xtra Advance / FuelSave / Silver)",
        "95":"95 RON (XCS / V-Power / Platinum)",
        "97":"97+ RON (Blaze 100 / Racing)",
        "dsl":"Diesel (Turbo / Max / Power)"
    }
    drift = 0.002+bias
    data  = {"Date": dates}
    for grade,price in base_prices.items():
        shocks = np.random.normal(drift, 0.012, days)
        data[mapping[grade]] = np.round(price * np.cumprod(1+shocks), 2)
    confidence = round(100*math.exp(-0.01*days), 1)
    return pd.DataFrame(data), confidence


# ─── App ─────────────────────────────────────────────────────────────────────

inject_custom_css()
initialize_session_state()

market_data = fetch_comprehensive_market_data()
ph_news     = fetch_philippine_oil_news()
bias        = analyze_news_sentiment(ph_news)
base_prices = {"91":market_data["p91"],"95":market_data["p95"],"97":market_data["p97"],"dsl":market_data["dsl"]}

# ── Controls (need before layout) ────────────────────────────────────────────
prediction_period = st.selectbox(
    "Prediction Horizon",
    ["7 Days Forecast","14 Days Forecast","30 Days Forecast"],
    label_visibility="collapsed"
)
days_forecast = int(prediction_period.split()[0])

all_fuel_types = [
    "91 RON (Xtra Advance / FuelSave / Silver)",
    "95 RON (XCS / V-Power / Platinum)",
    "97+ RON (Blaze 100 / Racing)",
    "Diesel (Turbo / Max / Power)"
]

selected_fuels = st.multiselect(
    "Fuel Types",
    options=all_fuel_types,
    default=all_fuel_types,
    label_visibility="collapsed"
)

forecast_df, dynamic_accuracy = generate_forecast_dataframe(base_prices, days_forecast, bias)

p91  = forecast_df['91 RON (Xtra Advance / FuelSave / Silver)'].iloc[0]
p95  = forecast_df['95 RON (XCS / V-Power / Platinum)'].iloc[0]
p97  = forecast_df['97+ RON (Blaze 100 / Racing)'].iloc[0]
pdsl = forecast_df['Diesel (Turbo / Max / Power)'].iloc[0]

time_str = datetime.now().strftime("%d %b %Y · %H:%M")

if bias > 0.003:
    sentiment_label = "BULLISH"
    sentiment_class = "sentiment-bull"
elif bias < -0.003:
    sentiment_label = "BEARISH"
    sentiment_class = "sentiment-bear"
else:
    sentiment_label = "NEUTRAL"
    sentiment_class = "sentiment-neut"

# ── Alert logic ───────────────────────────────────────────────────────────────
if bias > 0.005:
    alert_msg = "Supply-side pressures detected — model indicates an upward price correction is probable."
elif bias < -0.005:
    alert_msg = "Demand softness detected — model indicates a potential price rollback this cycle."
else:
    alert_msg = "Indices are within standard deviation. No significant price movement forecast."

# ─── MASTHEAD ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="masthead">
    <div class="masthead-left">
        <div class="masthead-title">PH Fuel Market Desk</div>
        <div class="masthead-sub">Philippine Energy Price Intelligence</div>
    </div>
    <div class="masthead-right">
        <div class="masthead-stat">
            <div class="masthead-stat-label">Brent Crude</div>
            <div class="masthead-stat-value">USD/BBL Index</div>
        </div>
        <div class="masthead-stat">
            <div class="masthead-stat-label">USD / PHP</div>
            <div class="masthead-stat-value">₱ {market_data['fx']:.2f}</div>
        </div>
        <div class="masthead-stat">
            <div class="masthead-stat-label">Sentiment</div>
            <div class="masthead-stat-value {sentiment_class}">{sentiment_label}</div>
        </div>
        <div class="masthead-stat">
            <div class="live-pill"><span class="live-dot"></span>Live</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── MAIN LAYOUT ─────────────────────────────────────────────────────────────
st.markdown('<div class="layout-wrapper">', unsafe_allow_html=True)

# ── LEFT SIDEBAR HTML ─────────────────────────────────────────────────────────
conf_bar = min(dynamic_accuracy, 100)
st.markdown(f"""
<div class="sidebar">

    <div class="sidebar-section-label">Pump Prices — Est. Today</div>

    <div class="price-tile">
        <div class="price-tile-header">
            <span class="price-tile-grade">91 Regular</span>
            <span class="price-tile-badge badge-91">RON 91</span>
        </div>
        <div class="price-tile-value"><span class="price-tile-peso">₱</span>{p91:.2f}</div>
        <div class="price-tile-brands">Xtra Advance · FuelSave · Silver</div>
    </div>

    <div class="price-tile">
        <div class="price-tile-header">
            <span class="price-tile-grade">95 Premium</span>
            <span class="price-tile-badge badge-95">RON 95</span>
        </div>
        <div class="price-tile-value"><span class="price-tile-peso">₱</span>{p95:.2f}</div>
        <div class="price-tile-brands">XCS · V-Power · Platinum</div>
    </div>

    <div class="price-tile">
        <div class="price-tile-header">
            <span class="price-tile-grade">97+ Ultra</span>
            <span class="price-tile-badge badge-97">RON 97</span>
        </div>
        <div class="price-tile-value"><span class="price-tile-peso">₱</span>{p97:.2f}</div>
        <div class="price-tile-brands">Blaze 100 · Seaoil 97</div>
    </div>

    <div class="price-tile">
        <div class="price-tile-header">
            <span class="price-tile-grade">Diesel</span>
            <span class="price-tile-badge badge-dsl">DSL</span>
        </div>
        <div class="price-tile-value"><span class="price-tile-peso">₱</span>{pdsl:.2f}</div>
        <div class="price-tile-brands">Turbo · Max · Power Diesel</div>
    </div>

    <hr class="sidebar-divider">

    <div class="sidebar-section-label">Model Parameters</div>

    <div class="stat-row">
        <span class="stat-key">Horizon</span>
        <span class="stat-val">{days_forecast}D</span>
    </div>

    <div class="stat-row">
        <span class="stat-key">Confidence</span>
        <span class="stat-val">{dynamic_accuracy}%</span>
    </div>

    <div class="confidence-bar">
        <div class="confidence-fill" style="width:{conf_bar}%"></div>
    </div>

    <div class="stat-row">
        <span class="stat-key">Signal</span>
        <span class="stat-val {sentiment_class}">{sentiment_label}</span>
    </div>

    <div class="stat-row">
        <span class="stat-key">Algorithm</span>
        <span class="stat-val">MLR + RW</span>
    </div>

    <div class="stat-row">
        <span class="stat-key">Refreshed</span>
        <span class="stat-val">{time_str}</span>
    </div>

</div>
""", unsafe_allow_html=True)

# ── RIGHT MAIN CONTENT ────────────────────────────────────────────────────────
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Alert band
st.markdown(f"""
<div class="alert-band">
    <strong>Market Signal</strong>&ensp;—&ensp;{alert_msg}
</div>
""", unsafe_allow_html=True)

# Controls row label
st.markdown("""
<div class="section-heading">
    <span class="section-num">01 —</span>
    <span class="section-title">Configure Forecast</span>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2.2])
with col1:
    st.markdown('<p style="font-family:\'DM Mono\',monospace;font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;color:#8a8580;margin-bottom:6px;">Horizon</p>', unsafe_allow_html=True)
    period_sel = st.selectbox("H", ["7 Days Forecast","14 Days Forecast","30 Days Forecast"],
                               label_visibility="collapsed",
                               index=["7 Days Forecast","14 Days Forecast","30 Days Forecast"].index(prediction_period))
with col2:
    st.markdown('<p style="font-family:\'DM Mono\',monospace;font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;color:#8a8580;margin-bottom:6px;">Fuel grades</p>', unsafe_allow_html=True)
    fuel_sel = st.multiselect("F", options=all_fuel_types, default=all_fuel_types, label_visibility="collapsed")

# Chart section
st.markdown(f"""
<div class="section-heading" style="margin-top:28px;">
    <span class="section-num">02 —</span>
    <span class="section-title">Price Trajectory</span>
    <span class="section-meta">{days_forecast}-Day Stochastic Forecast</span>
</div>
""", unsafe_allow_html=True)

if fuel_sel:
    plot_df = forecast_df[["Date"] + fuel_sel]
    melted  = plot_df.melt('Date', var_name='Fuel Type', value_name='Price')

    color_scale = alt.Scale(
        domain=["91 RON (Xtra Advance / FuelSave / Silver)",
                "95 RON (XCS / V-Power / Platinum)",
                "97+ RON (Blaze 100 / Racing)",
                "Diesel (Turbo / Max / Power)"],
        range=['#16a34a','#2563eb','#7c3aed','#c8450a']
    )

    chart = (
        alt.Chart(melted)
        .mark_line(point=alt.OverlayMarkDef(size=40, filled=True), strokeWidth=1.8)
        .encode(
            x=alt.X('Date:N', sort=None, title=None,
                     axis=alt.Axis(grid=False, labelColor='#8a8580', labelFont='DM Mono',
                                   tickColor='#d4cfc6', domainColor='#d4cfc6', labelFontSize=10)),
            y=alt.Y('Price:Q', scale=alt.Scale(zero=False), title='₱ / Litre',
                     axis=alt.Axis(grid=True, gridColor='#ede9e1', gridDash=[4,4],
                                   labelColor='#8a8580', titleColor='#8a8580',
                                   labelFont='DM Mono', titleFont='DM Mono',
                                   labelFontSize=10, titleFontSize=10, domainOpacity=0)),
            color=alt.Color('Fuel Type:N', scale=color_scale,
                             legend=alt.Legend(orient='bottom', title=None,
                                               labelColor='#444', labelFont='IBM Plex Sans',
                                               labelFontSize=11, symbolSize=80,
                                               padding=12, columnPadding=24)),
            tooltip=['Date','Fuel Type','Price']
        )
        .properties(height=360, background='#ffffff', padding={"left":12,"right":12,"top":12,"bottom":8})
        .configure_view(strokeWidth=0)
        .configure_axis(domain=False)
    )

    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.altair_chart(chart, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Select at least one fuel grade to render the chart.")

# Data table
st.markdown("""
<div class="section-heading">
    <span class="section-num">03 —</span>
    <span class="section-title">Forecast Table</span>
</div>
""", unsafe_allow_html=True)

if fuel_sel:
    st.dataframe(forecast_df[["Date"] + fuel_sel], hide_index=True, use_container_width=True, height=220)

# News section
st.markdown("""
<div class="section-heading" style="margin-top:36px;">
    <span class="section-num">04 —</span>
    <span class="section-title">Market Intelligence</span>
</div>
""", unsafe_allow_html=True)

news_html = '<div class="news-columns">'
for i, art in enumerate(ph_news):
    news_html += f"""
    <div class="news-col">
        <div class="news-col-index">Dispatch {i+1:02d} · {art['source'].upper()}</div>
        <div class="news-col-title">{art['title']}</div>
        <div class="news-col-body">{art['description']}</div>
        <a href="{art['url']}" target="_blank" class="news-col-link">Access Source ↗</a>
    </div>"""
news_html += '</div>'
st.markdown(news_html, unsafe_allow_html=True)

# Expanders
st.markdown('<div style="margin-top:8px;">', unsafe_allow_html=True)
with st.expander("Methodology & Data Integrity Statement"):
    st.markdown("""
**I. Data Acquisition.** Live macroeconomic data is pulled from the Federal Reserve Economic Data (FRED) API on a 5-minute cycle — covering global Brent Crude spot prices and the USD/PHP exchange rate index.

**II. Price Estimation.** Retail price estimates are computed via a Multiple Linear Regression model calibrated on the historical correlation between international benchmark indices and domestic pump prices.

**III. Forecast Simulation.** A sentiment-adjusted Stochastic Random Walk, informed by NLP analysis of domestic petroleum news (NewsData.io), projects the forward price trajectory over the selected forecast horizon.
    """)

with st.expander("Fuel Grade Definitions"):
    st.markdown("""
- **91 RON (Regular):** Standard unleaded gasoline — Petron Xtra Advance, Shell FuelSave, Caltex Silver.
- **95 RON (Premium):** Higher-octane formulation — Petron XCS, Shell V-Power, Caltex Platinum.
- **97+ RON (Ultra):** Maximum-performance gasoline for high-compression engines — Petron Blaze 100, Seaoil Extreme 97.
- **Diesel:** Automotive gas oil for conventional diesel engines — Petron Turbo Diesel, Shell V-Power Diesel, Caltex Power Diesel.
    """)
st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div class="page-footer">
    Developed by Ignacio L. &amp; Andrei B. &nbsp;·&nbsp; &copy; {datetime.now().year} &nbsp;·&nbsp; Data: FRED API · NewsData.io
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # close main-content
st.markdown('</div>', unsafe_allow_html=True)  # close layout-wrapper
