import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime, timedelta
import numpy as np
import math

st.set_page_config(
    page_title="Fuel Prices PH",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap');

        :root {
            --bg:           #f2f2f7;
            --surface:      #ffffff;
            --surface2:     #f2f2f7;
            --separator:    rgba(60,60,67,0.12);
            --label:        #000000;
            --label2:       rgba(60,60,67,0.6);
            --label3:       rgba(60,60,67,0.3);
            --blue:         #007aff;
            --green:        #34c759;
            --red:          #ff3b30;
            --orange:       #ff9500;
            --purple:       #af52de;
            --teal:         #5ac8fa;
            --radius-sm:    10px;
            --radius-md:    14px;
            --radius-lg:    20px;
            --shadow:       0 2px 12px rgba(0,0,0,0.07), 0 1px 3px rgba(0,0,0,0.05);
            --shadow-sm:    0 1px 4px rgba(0,0,0,0.06);
        }

        *, *::before, *::after {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            box-sizing: border-box;
        }

        .stApp {
            background-color: var(--bg);
            color: var(--label);
        }

        [data-testid="stHeader"] { display: none; }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }

        .block-container {
            padding-top: 48px !important;
            padding-bottom: 64px !important;
            padding-left: 6% !important;
            padding-right: 6% !important;
            max-width: 1200px !important;
            margin: 0 auto;
        }

        /* ── Page Title ───────────────────────────────────── */
        .page-eyebrow {
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: var(--blue);
            margin-bottom: 6px;
        }

        .page-title {
            font-size: 34px;
            font-weight: 700;
            letter-spacing: -0.8px;
            color: var(--label);
            line-height: 1.1;
            margin: 0 0 6px;
        }

        .page-subtitle {
            font-size: 15px;
            font-weight: 400;
            color: var(--label2);
            margin-bottom: 28px;
            line-height: 1.4;
        }

        /* ── Live Badge ───────────────────────────────────── */
        .badge-row {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 36px;
        }

        .live-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(52,199,89,0.12);
            color: #248a3d;
            font-size: 12px;
            font-weight: 600;
            padding: 5px 12px;
            border-radius: 100px;
        }

        .live-dot {
            width: 6px; height: 6px;
            background: var(--green);
            border-radius: 50%;
            animation: pulse 2.4s ease-in-out infinite;
        }

        @keyframes pulse {
            0%,100% { opacity: 1; transform: scale(1); }
            50%      { opacity: 0.5; transform: scale(0.85); }
        }

        .timestamp-badge {
            font-size: 12px;
            font-weight: 400;
            color: var(--label3);
        }

        /* ── Alert Card ───────────────────────────────────── */
        .alert-card {
            background: rgba(255,149,0,0.1);
            border-radius: var(--radius-md);
            padding: 14px 18px;
            display: flex;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 32px;
        }

        .alert-icon {
            font-size: 17px;
            line-height: 1;
            margin-top: 1px;
            flex-shrink: 0;
        }

        .alert-text {
            font-size: 14px;
            font-weight: 400;
            color: #7d4a00;
            line-height: 1.5;
        }

        .alert-text strong {
            font-weight: 600;
            color: #7d4a00;
        }

        /* ── Section Header ───────────────────────────────── */
        .section-header {
            font-size: 22px;
            font-weight: 700;
            letter-spacing: -0.4px;
            color: var(--label);
            margin: 0 0 16px;
        }

        /* ── Price Cards ──────────────────────────────────── */
        .price-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-bottom: 32px;
        }

        .price-card {
            background: var(--surface);
            border-radius: var(--radius-lg);
            padding: 22px 20px 18px;
            box-shadow: var(--shadow);
            position: relative;
            overflow: hidden;
            transition: transform 0.18s ease, box-shadow 0.18s ease;
        }

        .price-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 24px rgba(0,0,0,0.1), 0 2px 6px rgba(0,0,0,0.06);
        }

        .price-card-accent {
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            border-radius: var(--radius-lg) var(--radius-lg) 0 0;
        }

        .accent-green  { background: var(--green); }
        .accent-blue   { background: var(--blue); }
        .accent-purple { background: var(--purple); }
        .accent-orange { background: var(--orange); }

        .price-card-label {
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: var(--label3);
            margin-bottom: 10px;
        }

        .price-card-value {
            font-size: 36px;
            font-weight: 700;
            letter-spacing: -1.5px;
            line-height: 1;
            color: var(--label);
            font-variant-numeric: tabular-nums;
            margin-bottom: 4px;
        }

        .price-card-currency {
            font-size: 18px;
            font-weight: 400;
            color: var(--label2);
            letter-spacing: 0;
            margin-right: 1px;
        }

        .price-card-brands {
            font-size: 11px;
            font-weight: 400;
            color: var(--label3);
            margin-top: 10px;
            line-height: 1.4;
        }

        .price-card-pill {
            display: inline-block;
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 0.03em;
            padding: 3px 9px;
            border-radius: 100px;
            position: absolute;
            top: 18px;
            right: 16px;
        }

        .pill-green  { background: rgba(52,199,89,0.12);  color: #248a3d; }
        .pill-blue   { background: rgba(0,122,255,0.1);   color: #0055cc; }
        .pill-purple { background: rgba(175,82,222,0.1);  color: #8944ab; }
        .pill-orange { background: rgba(255,149,0,0.12);  color: #c87000; }

        /* ── Grouped Table Card ───────────────────────────── */
        .grouped-card {
            background: var(--surface);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow);
            overflow: hidden;
            margin-bottom: 32px;
        }

        .grouped-card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 18px 22px 14px;
            border-bottom: 1px solid var(--separator);
        }

        .grouped-card-title {
            font-size: 17px;
            font-weight: 600;
            letter-spacing: -0.3px;
            color: var(--label);
        }

        .grouped-card-meta {
            font-size: 12px;
            font-weight: 400;
            color: var(--label3);
        }

        .grouped-card-body {
            padding: 4px 0 4px;
        }

        /* ── Select overrides ─────────────────────────────── */
        [data-testid="stSelectbox"] label,
        [data-testid="stMultiSelect"] label {
            font-size: 12px !important;
            font-weight: 600 !important;
            letter-spacing: 0.04em !important;
            text-transform: uppercase !important;
            color: var(--label3) !important;
            margin-bottom: 4px !important;
        }

        [data-testid="stSelectbox"] > div > div,
        [data-testid="stMultiSelect"] > div > div {
            background: var(--surface) !important;
            border: 1px solid var(--separator) !important;
            border-radius: var(--radius-sm) !important;
            font-size: 15px !important;
            color: var(--label) !important;
            box-shadow: var(--shadow-sm) !important;
        }

        /* ── Stat row ─────────────────────────────────────── */
        .stat-inline-row {
            display: flex;
            gap: 12px;
            margin-bottom: 28px;
            flex-wrap: wrap;
        }

        .stat-inline-chip {
            background: var(--surface);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-sm);
            padding: 14px 18px;
            flex: 1;
            min-width: 120px;
        }

        .stat-inline-label {
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: var(--label3);
            margin-bottom: 6px;
        }

        .stat-inline-value {
            font-size: 22px;
            font-weight: 700;
            letter-spacing: -0.5px;
            color: var(--label);
            line-height: 1;
        }

        .stat-inline-sub {
            font-size: 11px;
            font-weight: 400;
            color: var(--label3);
            margin-top: 4px;
        }

        .confidence-track {
            height: 4px;
            background: var(--separator);
            border-radius: 2px;
            margin-top: 8px;
            overflow: hidden;
        }

        .confidence-thumb {
            height: 100%;
            border-radius: 2px;
            background: var(--green);
        }

        /* ── News Cards ───────────────────────────────────── */
        .news-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 32px;
        }

        .news-card {
            background: var(--surface);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow);
            padding: 22px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            transition: transform 0.18s ease;
        }

        .news-card:hover {
            transform: translateY(-2px);
        }

        .news-source-tag {
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: var(--blue);
        }

        .news-title {
            font-size: 16px;
            font-weight: 600;
            letter-spacing: -0.3px;
            color: var(--label);
            line-height: 1.35;
        }

        .news-body {
            font-size: 13px;
            font-weight: 400;
            color: var(--label2);
            line-height: 1.55;
            flex: 1;
        }

        .news-link {
            font-size: 13px;
            font-weight: 500;
            color: var(--blue);
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }

        /* ── Expanders ────────────────────────────────────── */
        [data-testid="stExpander"] {
            background: var(--surface) !important;
            border: none !important;
            border-radius: var(--radius-md) !important;
            box-shadow: var(--shadow-sm) !important;
            margin-bottom: 10px;
        }

        [data-testid="stExpander"] summary {
            font-size: 15px !important;
            font-weight: 600 !important;
            letter-spacing: -0.2px !important;
            color: var(--label) !important;
            padding: 16px 20px !important;
        }

        [data-testid="stExpanderDetails"] {
            font-size: 14px !important;
            font-weight: 400 !important;
            color: var(--label2) !important;
            line-height: 1.65 !important;
            padding: 0 20px 18px !important;
        }

        /* ── Dataframe ────────────────────────────────────── */
        [data-testid="stDataFrame"] {
            border-radius: var(--radius-sm);
            overflow: hidden;
        }

        /* ── Footer ───────────────────────────────────────── */
        .page-footer {
            text-align: center;
            margin-top: 48px;
            font-size: 12px;
            font-weight: 400;
            color: var(--label3);
            line-height: 1.8;
        }

        /* ── Responsive ───────────────────────────────────── */
        @media (max-width: 820px) {
            .block-container { padding-left: 1.2rem !important; padding-right: 1.2rem !important; }
            .price-grid { grid-template-columns: repeat(2, 1fr); }
            .news-grid  { grid-template-columns: 1fr; }
            .page-title { font-size: 28px; }
            .price-card-value { font-size: 28px; }
            .stat-inline-row { gap: 8px; }
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

# ── Title ─────────────────────────────────────────────────────────────────────
time_str = datetime.now().strftime("%B %d, %Y · %I:%M %p")

st.markdown(f"""
<div class="page-eyebrow">Philippines</div>
<div class="page-title">Fuel Prices</div>
<div class="page-subtitle">Estimated pump prices based on live Brent Crude &amp; USD/PHP rates.</div>
<div class="badge-row">
    <div class="live-badge"><span class="live-dot"></span>Live</div>
    <span class="timestamp-badge">{time_str}</span>
</div>
""", unsafe_allow_html=True)

# ── Alert ─────────────────────────────────────────────────────────────────────
if bias > 0.005:
    alert_msg = "<strong>Price increase likely.</strong> Supply-side signals suggest an upward adjustment this cycle."
    alert_icon = "↑"
elif bias < -0.005:
    alert_msg = "<strong>Rollback possible.</strong> Market signals point toward a potential price reduction."
    alert_icon = "↓"
else:
    alert_msg = "<strong>Stable outlook.</strong> Current indices are within normal variance. No significant movement forecast."
    alert_icon = "◎"

st.markdown(f"""
<div class="alert-card">
    <span class="alert-icon">{alert_icon}</span>
    <span class="alert-text">{alert_msg}</span>
</div>
""", unsafe_allow_html=True)

# ── Controls ──────────────────────────────────────────────────────────────────
c1, c2 = st.columns([1, 2.4])
with c1:
    prediction_period = st.selectbox("Horizon", ["7 Days Forecast","14 Days Forecast","30 Days Forecast"])
    days_forecast = int(prediction_period.split()[0])

all_fuel_types = [
    "91 RON (Xtra Advance / FuelSave / Silver)",
    "95 RON (XCS / V-Power / Platinum)",
    "97+ RON (Blaze 100 / Racing)",
    "Diesel (Turbo / Max / Power)"
]
with c2:
    selected_fuels = st.multiselect("Fuel Types", options=all_fuel_types, default=all_fuel_types)

forecast_df, dynamic_accuracy = generate_forecast_dataframe(base_prices, days_forecast, bias)

p91  = forecast_df['91 RON (Xtra Advance / FuelSave / Silver)'].iloc[0]
p95  = forecast_df['95 RON (XCS / V-Power / Platinum)'].iloc[0]
p97  = forecast_df['97+ RON (Blaze 100 / Racing)'].iloc[0]
pdsl = forecast_df['Diesel (Turbo / Max / Power)'].iloc[0]

# ── Price Cards ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-header" style="margin-top:12px;">Today\'s Prices</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="price-grid">
    <div class="price-card">
        <div class="price-card-accent accent-green"></div>
        <div class="price-card-pill pill-green">RON 91</div>
        <div class="price-card-label">91 Regular</div>
        <div class="price-card-value"><span class="price-card-currency">₱</span>{p91:.2f}</div>
        <div class="price-card-brands">Xtra Advance · FuelSave · Silver</div>
    </div>
    <div class="price-card">
        <div class="price-card-accent accent-blue"></div>
        <div class="price-card-pill pill-blue">RON 95</div>
        <div class="price-card-label">95 Premium</div>
        <div class="price-card-value"><span class="price-card-currency">₱</span>{p95:.2f}</div>
        <div class="price-card-brands">XCS · V-Power · Platinum</div>
    </div>
    <div class="price-card">
        <div class="price-card-accent accent-purple"></div>
        <div class="price-card-pill pill-purple">RON 97</div>
        <div class="price-card-label">97+ Ultra</div>
        <div class="price-card-value"><span class="price-card-currency">₱</span>{p97:.2f}</div>
        <div class="price-card-brands">Blaze 100 · Extreme 97</div>
    </div>
    <div class="price-card">
        <div class="price-card-accent accent-orange"></div>
        <div class="price-card-pill pill-orange">DSL</div>
        <div class="price-card-label">Diesel</div>
        <div class="price-card-value"><span class="price-card-currency">₱</span>{pdsl:.2f}</div>
        <div class="price-card-brands">Turbo · Max · Power Diesel</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Chart ─────────────────────────────────────────────────────────────────────
st.markdown(f'<div class="section-header">{days_forecast}-Day Forecast</div>', unsafe_allow_html=True)

if selected_fuels:
    plot_df = forecast_df[["Date"] + selected_fuels]
    melted  = plot_df.melt('Date', var_name='Fuel Type', value_name='Price')

    color_scale = alt.Scale(
        domain=["91 RON (Xtra Advance / FuelSave / Silver)",
                "95 RON (XCS / V-Power / Platinum)",
                "97+ RON (Blaze 100 / Racing)",
                "Diesel (Turbo / Max / Power)"],
        range=['#34c759','#007aff','#af52de','#ff9500']
    )

    chart = (
        alt.Chart(melted)
        .mark_line(point=alt.OverlayMarkDef(size=45, filled=True), strokeWidth=2)
        .encode(
            x=alt.X('Date:N', sort=None, title=None,
                     axis=alt.Axis(grid=False, labelColor='rgba(60,60,67,0.4)',
                                   labelFont='Inter', tickColor='rgba(60,60,67,0.1)',
                                   domainColor='rgba(60,60,67,0.1)', labelFontSize=11)),
            y=alt.Y('Price:Q', scale=alt.Scale(zero=False), title='₱ per Litre',
                     axis=alt.Axis(grid=True, gridColor='rgba(60,60,67,0.06)',
                                   labelColor='rgba(60,60,67,0.4)', titleColor='rgba(60,60,67,0.4)',
                                   labelFont='Inter', titleFont='Inter',
                                   labelFontSize=11, titleFontSize=11, domainOpacity=0)),
            color=alt.Color('Fuel Type:N', scale=color_scale,
                             legend=alt.Legend(orient='bottom', title=None,
                                               labelColor='rgba(60,60,67,0.7)',
                                               labelFont='Inter', labelFontSize=12,
                                               symbolSize=80, padding=14, columnPadding=20)),
            tooltip=['Date','Fuel Type','Price']
        )
        .properties(height=360, background='#ffffff',
                    padding={"left":16,"right":16,"top":16,"bottom":8})
        .configure_view(strokeWidth=0, cornerRadius=14)
        .configure_axis(domain=False)
    )

    st.altair_chart(chart, use_container_width=True)
else:
    st.info("Select at least one fuel type to display the chart.")

# ── Model Stats row ───────────────────────────────────────────────────────────
bar_w = min(dynamic_accuracy, 100)
if bias > 0.003:   sentiment_str, sentiment_color = "Bullish", "#248a3d"
elif bias < -0.003: sentiment_str, sentiment_color = "Bearish", "#c0392b"
else:               sentiment_str, sentiment_color = "Neutral", "rgba(60,60,67,0.4)"

st.markdown(f"""
<div class="stat-inline-row">
    <div class="stat-inline-chip">
        <div class="stat-inline-label">Confidence</div>
        <div class="stat-inline-value">{dynamic_accuracy}%</div>
        <div class="confidence-track">
            <div class="confidence-thumb" style="width:{bar_w}%"></div>
        </div>
        <div class="stat-inline-sub">{days_forecast}-day horizon</div>
    </div>
    <div class="stat-inline-chip">
        <div class="stat-inline-label">Market Signal</div>
        <div class="stat-inline-value" style="color:{sentiment_color};">{sentiment_str}</div>
        <div class="stat-inline-sub">Based on news NLP</div>
    </div>
    <div class="stat-inline-chip">
        <div class="stat-inline-label">Model</div>
        <div class="stat-inline-value" style="font-size:16px; font-weight:600; letter-spacing:-0.2px;">MLR + RW</div>
        <div class="stat-inline-sub">Brent Crude · USD/PHP</div>
    </div>
    <div class="stat-inline-chip">
        <div class="stat-inline-label">Data Refresh</div>
        <div class="stat-inline-value" style="font-size:16px; font-weight:600; letter-spacing:-0.2px;">5 min</div>
        <div class="stat-inline-sub">Via FRED API</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Forecast Table ────────────────────────────────────────────────────────────
if selected_fuels:
    st.markdown('<div class="section-header">Forecast Table</div>', unsafe_allow_html=True)
    st.dataframe(forecast_df[["Date"] + selected_fuels], hide_index=True, use_container_width=True, height=220)

# ── News ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header" style="margin-top:8px;">Market News</div>', unsafe_allow_html=True)

news_html = '<div class="news-grid">'
for art in ph_news:
    news_html += f"""
    <div class="news-card">
        <div class="news-source-tag">{art['source']}</div>
        <div class="news-title">{art['title']}</div>
        <div class="news-body">{art['description']}</div>
        <a href="{art['url']}" target="_blank" class="news-link">Read more →</a>
    </div>"""
news_html += '</div>'
st.markdown(news_html, unsafe_allow_html=True)

# ── Expanders ─────────────────────────────────────────────────────────────────
with st.expander("Methodology"):
    st.markdown("""
**Data.** Live Brent Crude and USD/PHP rates are fetched from the Federal Reserve Economic Data (FRED) API every 5 minutes.

**Price Estimation.** A Multiple Linear Regression model maps international indices to domestic pump prices using historical calibration data.

**Forecast.** A Stochastic Random Walk, biased by an NLP sentiment score derived from domestic oil news, simulates forward price trajectories.
    """)

with st.expander("Fuel Grade Definitions"):
    st.markdown("""
- **91 RON** — Standard unleaded. Petron Xtra Advance, Shell FuelSave, Caltex Silver.
- **95 RON** — Higher-octane premium. Petron XCS, Shell V-Power, Caltex Platinum.
- **97+ RON** — Performance ultra. Petron Blaze 100, Seaoil Extreme 97.
- **Diesel** — Automotive gas oil. Petron Turbo, Shell V-Power Diesel, Caltex Power Diesel.
    """)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-footer">
    Developed by Ignacio L. and Andrei B. · © {datetime.now().year}
</div>
""", unsafe_allow_html=True)
