import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime, timedelta
import numpy as np
import math

st.set_page_config(
    page_title="Fuel PH",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,500;14..32,600;14..32,700;14..32,800&display=swap');

    :root {
        --bg:          #f5f5f7;
        --surface:     #ffffff;
        --surface-alt: #f5f5f7;
        --border:      rgba(0,0,0,0.06);
        --ink:         #1d1d1f;
        --ink-2:       #6e6e73;
        --ink-3:       #aeaeb2;
        --blue:        #0071e3;
        --blue-light:  rgba(0,113,227,0.08);
        --green:       #1d9d4e;
        --green-light: rgba(29,157,78,0.09);
        --orange:      #bf5200;
        --orange-light:rgba(191,82,0,0.08);
        --shadow-sm:   0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
        --shadow-md:   0 4px 16px rgba(0,0,0,0.07), 0 1px 4px rgba(0,0,0,0.04);
        --shadow-lg:   0 8px 32px rgba(0,0,0,0.09), 0 2px 8px rgba(0,0,0,0.05);
        --r-sm:        10px;
        --r-md:        14px;
        --r-lg:        18px;
        --r-xl:        22px;
    }

    /* ── Reset & Base ──────────────────────────────────── */
    *, *::before, *::after {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif !important;
        box-sizing: border-box;
        -webkit-font-smoothing: antialiased;
    }

    .stApp { background: var(--bg); color: var(--ink); }
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    #MainMenu, footer { display: none !important; }

    .block-container {
        padding: 56px 0 80px !important;
        max-width: 980px !important;
        margin: 0 auto !important;
    }

    /* ── Page-load animation keyframes ────────────────── */
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(18px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to   { opacity: 1; }
    }
    @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.97); }
        to   { opacity: 1; transform: scale(1); }
    }
    @keyframes livePulse {
        0%,100% { box-shadow: 0 0 0 0 rgba(29,157,78,0.4); }
        50%      { box-shadow: 0 0 0 5px rgba(29,157,78,0); }
    }
    @keyframes shimmer {
        0%   { background-position: -200% center; }
        100% { background-position:  200% center; }
    }
    @keyframes numberCount {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── Header ────────────────────────────────────────── */
    .app-header {
        padding: 0 0 40px;
        animation: fadeUp 0.55s cubic-bezier(.22,.68,0,1.2) both;
    }

    .header-eyebrow {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 10px;
    }

    .live-dot-wrap {
        display: flex;
        align-items: center;
        gap: 6px;
        background: var(--green-light);
        border-radius: 100px;
        padding: 4px 11px 4px 8px;
    }

    .live-dot {
        width: 7px;
        height: 7px;
        background: #1d9d4e;
        border-radius: 50%;
        animation: livePulse 2.2s ease-in-out infinite;
    }

    .live-label {
        font-size: 11.5px;
        font-weight: 600;
        color: var(--green);
        letter-spacing: 0.01em;
    }

    .header-timestamp {
        font-size: 12px;
        font-weight: 400;
        color: var(--ink-3);
    }

    .app-title {
        font-size: 48px;
        font-weight: 700;
        letter-spacing: -1.8px;
        line-height: 1.05;
        color: var(--ink);
        margin: 0 0 8px;
    }

    .app-description {
        font-size: 17px;
        font-weight: 400;
        color: var(--ink-2);
        line-height: 1.5;
        max-width: 480px;
    }

    /* ── Alert ─────────────────────────────────────────── */
    .alert-row {
        animation: fadeUp 0.55s 0.08s cubic-bezier(.22,.68,0,1.2) both;
        margin-bottom: 36px;
    }

    .alert-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 9px 16px;
        border-radius: 100px;
        font-size: 13.5px;
        font-weight: 500;
        line-height: 1.4;
    }

    .alert-neutral { background: rgba(0,0,0,0.05); color: var(--ink-2); }
    .alert-up      { background: rgba(255,59,48,0.09); color: #c0392b; }
    .alert-down    { background: var(--green-light); color: var(--green); }

    .alert-icon { font-size: 15px; }

    /* ── Section label ─────────────────────────────────── */
    .section-label {
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.02em;
        color: var(--ink-3);
        text-transform: uppercase;
        margin-bottom: 14px;
    }

    /* ── Price grid ────────────────────────────────────── */
    .price-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 40px;
    }

    .price-card {
        background: var(--surface);
        border-radius: var(--r-xl);
        padding: 22px 20px 20px;
        box-shadow: var(--shadow-sm);
        position: relative;
        overflow: hidden;
        cursor: default;
        transition: transform 0.22s cubic-bezier(.34,1.56,.64,1),
                    box-shadow 0.22s ease;
        animation: scaleIn 0.5s cubic-bezier(.22,.68,0,1.2) both;
    }

    .price-card:nth-child(1) { animation-delay: 0.12s; }
    .price-card:nth-child(2) { animation-delay: 0.18s; }
    .price-card:nth-child(3) { animation-delay: 0.24s; }
    .price-card:nth-child(4) { animation-delay: 0.30s; }

    .price-card:hover {
        transform: translateY(-3px) scale(1.01);
        box-shadow: var(--shadow-lg);
    }

    .price-card::before {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: inherit;
        border: 1px solid var(--border);
        pointer-events: none;
    }

    .price-card-icon {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        margin-bottom: 16px;
    }

    .icon-green  { background: var(--green-light); }
    .icon-blue   { background: var(--blue-light); }
    .icon-purple { background: rgba(88,86,214,0.09); }
    .icon-orange { background: var(--orange-light); }

    .price-card-grade {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: var(--ink-3);
        margin-bottom: 4px;
    }

    .price-card-name {
        font-size: 14px;
        font-weight: 500;
        color: var(--ink-2);
        margin-bottom: 10px;
    }

    .price-card-value {
        font-size: 34px;
        font-weight: 700;
        letter-spacing: -1.2px;
        color: var(--ink);
        line-height: 1;
        font-variant-numeric: tabular-nums;
        animation: numberCount 0.45s cubic-bezier(.22,.68,0,1.2) both;
    }

    .price-peso {
        font-size: 20px;
        font-weight: 400;
        color: var(--ink-3);
        margin-right: 1px;
        vertical-align: 3px;
    }

    .price-card-brands {
        font-size: 11px;
        font-weight: 400;
        color: var(--ink-3);
        margin-top: 10px;
        line-height: 1.5;
    }

    /* ── Horizon Selector ──────────────────────────────── */
    .horizon-row {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 20px;
        animation: fadeUp 0.5s 0.35s cubic-bezier(.22,.68,0,1.2) both;
    }

    .horizon-label {
        font-size: 15px;
        font-weight: 600;
        color: var(--ink);
        margin-right: 4px;
    }

    .horizon-btn {
        padding: 7px 16px;
        border-radius: 100px;
        font-size: 13px;
        font-weight: 500;
        cursor: pointer;
        border: none;
        transition: background 0.18s ease, color 0.18s ease;
        background: var(--surface);
        color: var(--ink-2);
        box-shadow: var(--shadow-sm);
    }

    .horizon-btn.active {
        background: var(--blue);
        color: #fff;
        box-shadow: 0 2px 8px rgba(0,113,227,0.3);
    }

    /* ── Streamlit selectbox override ─────────────────── */
    [data-testid="stSelectbox"] label {
        font-size: 11px !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
        color: var(--ink-3) !important;
    }

    [data-testid="stSelectbox"] > div > div {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--r-md) !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        color: var(--ink) !important;
        box-shadow: var(--shadow-sm) !important;
        transition: box-shadow 0.18s ease !important;
    }

    [data-testid="stSelectbox"] > div > div:focus-within {
        box-shadow: 0 0 0 3px rgba(0,113,227,0.18), var(--shadow-sm) !important;
        border-color: var(--blue) !important;
    }

    /* ── Chart card ────────────────────────────────────── */
    .chart-card {
        background: var(--surface);
        border-radius: var(--r-xl);
        box-shadow: var(--shadow-md);
        padding: 24px 20px 12px;
        margin-bottom: 16px;
        border: 1px solid var(--border);
        animation: fadeUp 0.5s 0.38s cubic-bezier(.22,.68,0,1.2) both;
    }

    .chart-card-header {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        margin-bottom: 4px;
        padding: 0 4px;
    }

    .chart-card-title {
        font-size: 17px;
        font-weight: 600;
        letter-spacing: -0.3px;
        color: var(--ink);
    }

    .chart-card-subtitle {
        font-size: 13px;
        font-weight: 400;
        color: var(--ink-3);
    }

    /* ── Stats strip ───────────────────────────────────── */
    .stats-strip {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 40px;
        animation: fadeUp 0.5s 0.44s cubic-bezier(.22,.68,0,1.2) both;
    }

    .stat-cell {
        background: var(--surface);
        border-radius: var(--r-lg);
        padding: 18px 18px 16px;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .stat-cell:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }

    .stat-cell-label {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        color: var(--ink-3);
        margin-bottom: 8px;
    }

    .stat-cell-value {
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.8px;
        color: var(--ink);
        line-height: 1;
        margin-bottom: 6px;
        font-variant-numeric: tabular-nums;
    }

    .stat-cell-sub {
        font-size: 11.5px;
        font-weight: 400;
        color: var(--ink-3);
        line-height: 1.4;
    }

    .conf-track {
        height: 3px;
        background: rgba(0,0,0,0.06);
        border-radius: 2px;
        margin-top: 10px;
        overflow: hidden;
    }

    .conf-fill {
        height: 100%;
        background: var(--blue);
        border-radius: 2px;
        transition: width 0.6s cubic-bezier(.22,.68,0,1.2);
    }

    .val-green  { color: var(--green) !important; }
    .val-red    { color: #c0392b !important; }
    .val-muted  { color: var(--ink-3) !important; }

    /* ── News section ──────────────────────────────────── */
    .news-wrap {
        animation: fadeUp 0.5s 0.5s cubic-bezier(.22,.68,0,1.2) both;
    }

    .news-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-bottom: 32px;
    }

    .news-card {
        background: var(--surface);
        border-radius: var(--r-xl);
        padding: 22px 22px 20px;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border);
        display: flex;
        flex-direction: column;
        gap: 8px;
        transition: transform 0.22s cubic-bezier(.34,1.56,.64,1), box-shadow 0.22s ease;
        cursor: default;
    }

    .news-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }

    .news-tag {
        display: inline-block;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        color: var(--blue);
        background: var(--blue-light);
        padding: 3px 9px;
        border-radius: 100px;
        width: fit-content;
    }

    .news-title {
        font-size: 15px;
        font-weight: 600;
        letter-spacing: -0.2px;
        color: var(--ink);
        line-height: 1.4;
    }

    .news-body {
        font-size: 13px;
        font-weight: 400;
        color: var(--ink-2);
        line-height: 1.6;
        flex: 1;
    }

    .news-link {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 13px;
        font-weight: 500;
        color: var(--blue);
        text-decoration: none;
        margin-top: 4px;
        transition: gap 0.15s ease;
    }

    .news-link:hover { gap: 7px; }

    /* ── Info cards (expanders) ────────────────────────── */
    .info-wrap {
        animation: fadeUp 0.5s 0.56s cubic-bezier(.22,.68,0,1.2) both;
        margin-bottom: 16px;
    }

    [data-testid="stExpander"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--r-lg) !important;
        box-shadow: var(--shadow-sm) !important;
        margin-bottom: 8px;
        overflow: hidden;
    }

    [data-testid="stExpander"] summary {
        font-size: 15px !important;
        font-weight: 600 !important;
        letter-spacing: -0.2px !important;
        color: var(--ink) !important;
        padding: 16px 20px !important;
    }

    [data-testid="stExpanderDetails"] {
        font-size: 14px !important;
        font-weight: 400 !important;
        color: var(--ink-2) !important;
        line-height: 1.7 !important;
        padding: 0 20px 18px !important;
    }

    /* ── Dataframe ─────────────────────────────────────── */
    .table-wrap {
        background: var(--surface);
        border-radius: var(--r-xl);
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border);
        overflow: hidden;
        margin-bottom: 40px;
        animation: fadeUp 0.5s 0.42s cubic-bezier(.22,.68,0,1.2) both;
    }

    .table-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 20px 14px;
        border-bottom: 1px solid var(--border);
    }

    .table-title {
        font-size: 15px;
        font-weight: 600;
        letter-spacing: -0.2px;
        color: var(--ink);
    }

    .table-meta {
        font-size: 12px;
        font-weight: 400;
        color: var(--ink-3);
    }

    [data-testid="stDataFrame"] {
        border: none !important;
        border-radius: 0 !important;
    }

    /* ── Footer ────────────────────────────────────────── */
    .app-footer {
        text-align: center;
        padding-top: 24px;
        border-top: 1px solid var(--border);
        font-size: 12px;
        font-weight: 400;
        color: var(--ink-3);
        line-height: 1.8;
        animation: fadeIn 0.5s 0.6s both;
    }

    /* ── Responsive ────────────────────────────────────── */
    @media (max-width: 860px) {
        .block-container { padding: 32px 1.2rem 64px !important; }
        .app-title { font-size: 34px; letter-spacing: -1.2px; }
        .price-grid { grid-template-columns: repeat(2, 1fr); }
        .stats-strip { grid-template-columns: repeat(2, 1fr); }
        .news-grid { grid-template-columns: 1fr; }
    }
    </style>
    """, unsafe_allow_html=True)


# ─── Model ────────────────────────────────────────────────────────────────────
HIST = np.array([[1,74.2,55.8],[1,78.5,56.1],[1,80.2,56.5],[1,82.5,57.0]])
INV  = np.linalg.inv(HIST.T @ HIST) @ HIST.T
W91  = INV @ np.array([50.50,52.10,57.30,59.10])
W95  = INV @ np.array([54.20,56.90,62.10,63.90])
W97  = INV @ np.array([58.10,60.40,65.60,67.40])
WDSL = INV @ np.array([58.00,60.50,72.10,75.90])

FUEL_LABELS = {
    "91":  "91 RON (Xtra Advance / FuelSave / Silver)",
    "95":  "95 RON (XCS / V-Power / Platinum)",
    "97":  "97+ RON (Blaze 100 / Racing)",
    "dsl": "Diesel (Turbo / Max / Power)"
}

def init_state():
    if "market" not in st.session_state:
        st.session_state.market = {
            "fx":56.10,"p91":72.35,"p95":74.50,"p97":82.30,"dsl":75.10
        }

def regress(brent, fx):
    v = np.array([1, brent, fx])
    return {"p91":v@W91,"p95":v@W95,"p97":v@W97,"dsl":v@WDSL}

@st.cache_data(ttl=300, show_spinner=False)
def fetch_market():
    try:
        key = st.secrets.get("FRED_API_KEY", None)
        if not key: return st.session_state.market
        p = {"api_key":key,"file_type":"json","sort_order":"desc","limit":1}
        rb = requests.get("https://api.stlouisfed.org/api/fred/series/observations?series_id=DCOILBRENTEU",params=p,timeout=4)
        rf = requests.get("https://api.stlouisfed.org/api/fred/series/observations?series_id=DEXPHUS",params=p,timeout=4)
        if rb.status_code==200 and rf.status_code==200:
            brent = float(rb.json()['observations'][0]['value'])
            fx    = float(rf.json()['observations'][0]['value'])
            cp    = regress(brent, fx)
            data  = {"fx":fx,"p91":cp["p91"],"p95":cp["p95"],"p97":cp["p97"],"dsl":cp["dsl"]}
            st.session_state.market = data
            return data
        return st.session_state.market
    except:
        return st.session_state.market

@st.cache_data(ttl=300, show_spinner=False)
def fetch_news():
    fallback = [
        {"title":"Legislative Review of Fuel Excise Tax Initiated",
         "description":"National legislators are evaluating structural modifications to fuel taxation to alleviate domestic price pressures.",
         "url":"#","source":"Market Desk"},
        {"title":"Global Brent Crude Trends Impact Local Markets",
         "description":"Recent shifts in global Brent crude valuations continue to influence local retail pump prices within the Philippine archipelago.",
         "url":"#","source":"Market Desk"},
    ]
    try:
        key = st.secrets.get("NEWSDATA_API_KEY", None)
        if not key: return fallback
        r = requests.get(
            f"https://newsdata.io/api/1/news?apikey={key}&country=ph&q=fuel%20OR%20oil%20OR%20gasoline%20OR%20diesel&language=en",
            timeout=5)
        if r.status_code==200:
            results = r.json().get("results",[])
            if len(results)>=2:
                return [{"title":a.get("title","Update"),
                         "description":(str(a.get("description",""))[:155]+"..."),
                         "url":a.get("link","#"),
                         "source":a.get("source_id","News")} for a in results[:2]]
        return fallback
    except:
        return fallback

def sentiment(articles):
    up   = ['hike','increase','surge','conflict','war','shortage','upward','soar','unrest','tighten']
    down = ['rollback','decrease','drop','slump','surplus','ease','plunge','cheaper','suspend']
    s = 0
    for a in articles:
        t = f"{a['title']} {a['description']}".lower()
        for w in up:   s += 0.003 if w in t else 0
        for w in down: s -= 0.003 if w in t else 0
    return max(min(s,0.015),-0.015)

@st.cache_data(ttl=300, show_spinner=False)
def forecast(base, days, bias):
    np.random.seed(42)
    now   = datetime.now()
    dates = [(now+timedelta(days=i)).strftime('%b %d') for i in range(days)]
    drift = 0.002+bias
    data  = {"Date": dates}
    for grade,price in base.items():
        shocks = np.random.normal(drift, 0.012, days)
        data[FUEL_LABELS[grade]] = np.round(price * np.cumprod(1+shocks), 2)
    conf = round(100*math.exp(-0.01*days), 1)
    return pd.DataFrame(data), conf


# ─── App ──────────────────────────────────────────────────────────────────────
inject_css()
init_state()

market  = fetch_market()
news    = fetch_news()
bias    = sentiment(news)
base    = {"91":market["p91"],"95":market["p95"],"97":market["p97"],"dsl":market["dsl"]}

# ── Horizon selector ──────────────────────────────────────────────────────────
period = st.selectbox("Horizon", ["7 Days","14 Days","30 Days"], label_visibility="collapsed")
days   = int(period.split()[0])

df, conf = forecast(base, days, bias)

p91  = df[FUEL_LABELS["91"]].iloc[0]
p95  = df[FUEL_LABELS["95"]].iloc[0]
p97  = df[FUEL_LABELS["97"]].iloc[0]
pdsl = df[FUEL_LABELS["dsl"]].iloc[0]

ts = datetime.now().strftime("%B %d, %Y · %I:%M %p")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="app-header">
    <div class="header-eyebrow">
        <div class="live-dot-wrap">
            <div class="live-dot"></div>
            <span class="live-label">Live</span>
        </div>
        <span class="header-timestamp">{ts}</span>
    </div>
    <div class="app-title">Fuel Prices</div>
    <div class="app-description">Estimated Philippine pump prices, updated every 5 minutes using live Brent Crude and USD/PHP data.</div>
</div>
""", unsafe_allow_html=True)

# ── Alert ─────────────────────────────────────────────────────────────────────
if bias > 0.005:
    a_cls, a_icon, a_txt = "alert-up", "↑", "Price increase likely this cycle based on current supply signals."
elif bias < -0.005:
    a_cls, a_icon, a_txt = "alert-down", "↓", "Rollback possible — demand softness detected in market data."
else:
    a_cls, a_icon, a_txt = "alert-neutral", "◎", "Stable outlook. Indices are within normal variance."

st.markdown(f"""
<div class="alert-row">
    <div class="alert-pill {a_cls}">
        <span class="alert-icon">{a_icon}</span>
        {a_txt}
    </div>
</div>
""", unsafe_allow_html=True)

# ── Price cards ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Today\'s Estimate</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="price-grid">
    <div class="price-card">
        <div class="price-card-icon icon-green">⛽</div>
        <div class="price-card-grade">RON 91</div>
        <div class="price-card-name">Regular</div>
        <div class="price-card-value"><span class="price-peso">₱</span>{p91:.2f}</div>
        <div class="price-card-brands">Xtra Advance · FuelSave · Silver</div>
    </div>
    <div class="price-card">
        <div class="price-card-icon icon-blue">⛽</div>
        <div class="price-card-grade">RON 95</div>
        <div class="price-card-name">Premium</div>
        <div class="price-card-value"><span class="price-peso">₱</span>{p95:.2f}</div>
        <div class="price-card-brands">XCS · V-Power · Platinum</div>
    </div>
    <div class="price-card">
        <div class="price-card-icon icon-purple">⛽</div>
        <div class="price-card-grade">RON 97+</div>
        <div class="price-card-name">Ultra</div>
        <div class="price-card-value"><span class="price-peso">₱</span>{p97:.2f}</div>
        <div class="price-card-brands">Blaze 100 · Extreme 97</div>
    </div>
    <div class="price-card">
        <div class="price-card-icon icon-orange">🛢️</div>
        <div class="price-card-grade">Diesel</div>
        <div class="price-card-name">Standard</div>
        <div class="price-card-value"><span class="price-peso">₱</span>{pdsl:.2f}</div>
        <div class="price-card-brands">Turbo · Max · Power Diesel</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Horizon selector label ────────────────────────────────────────────────────
st.markdown(f'<div class="section-label" style="margin-top:8px;">{days}-Day Price Forecast</div>', unsafe_allow_html=True)

col_sel, _ = st.columns([1, 3])
with col_sel:
    period2 = st.selectbox(
        "Forecast window",
        ["7 Days","14 Days","30 Days"],
        index=["7 Days","14 Days","30 Days"].index(period),
        label_visibility="visible"
    )
    if period2 != period:
        st.rerun()

# ── Chart ─────────────────────────────────────────────────────────────────────
all_fuels = list(FUEL_LABELS.values())
melted = df[["Date"]+all_fuels].melt("Date", var_name="Fuel", value_name="Price")

color_scale = alt.Scale(
    domain=all_fuels,
    range=["#1d9d4e","#0071e3","#5856d6","#bf5200"]
)

base_chart = alt.Chart(melted)

lines = base_chart.mark_line(strokeWidth=2).encode(
    x=alt.X("Date:N", sort=None, title=None,
             axis=alt.Axis(
                 grid=False,
                 labelColor="#aeaeb2",
                 labelFont="Inter",
                 labelFontSize=11,
                 labelFontWeight=400,
                 tickColor="rgba(0,0,0,0.06)",
                 domainColor="rgba(0,0,0,0.06)"
             )),
    y=alt.Y("Price:Q", scale=alt.Scale(zero=False), title="₱ per litre",
             axis=alt.Axis(
                 grid=True,
                 gridColor="rgba(0,0,0,0.04)",
                 labelColor="#aeaeb2",
                 titleColor="#aeaeb2",
                 labelFont="Inter",
                 titleFont="Inter",
                 labelFontSize=11,
                 titleFontSize=11,
                 domainOpacity=0,
                 tickCount=5
             )),
    color=alt.Color("Fuel:N", scale=color_scale,
                     legend=alt.Legend(
                         orient="bottom",
                         title=None,
                         labelColor="#6e6e73",
                         labelFont="Inter",
                         labelFontSize=12,
                         labelFontWeight=500,
                         symbolSize=90,
                         symbolStrokeWidth=2.5,
                         padding=16,
                         columnPadding=24
                     )),
    tooltip=[
        alt.Tooltip("Date:N", title="Date"),
        alt.Tooltip("Fuel:N", title="Grade"),
        alt.Tooltip("Price:Q", title="Price (₱)", format=".2f")
    ]
)

points = base_chart.mark_point(size=55, filled=True, opacity=0).encode(
    x=alt.X("Date:N", sort=None),
    y=alt.Y("Price:Q", scale=alt.Scale(zero=False)),
    color=alt.Color("Fuel:N", scale=color_scale, legend=None),
    tooltip=[
        alt.Tooltip("Date:N", title="Date"),
        alt.Tooltip("Fuel:N", title="Grade"),
        alt.Tooltip("Price:Q", title="Price (₱)", format=".2f")
    ]
).properties(width="container")

chart = (
    (lines + points)
    .properties(height=340, background="#ffffff",
                padding={"left":14,"right":14,"top":16,"bottom":10})
    .configure_view(strokeWidth=0, cornerRadius=18)
    .configure_axis(domain=False)
)

st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.markdown(f"""
<div class="chart-card-header">
    <span class="chart-card-title">Price Trajectory</span>
    <span class="chart-card-subtitle">All grades · {days}-day stochastic model</span>
</div>
""", unsafe_allow_html=True)
st.altair_chart(chart, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Stats strip ───────────────────────────────────────────────────────────────
if bias > 0.003:   sig_val, sig_cls = "Bullish", "val-green"
elif bias < -0.003: sig_val, sig_cls = "Bearish", "val-red"
else:               sig_val, sig_cls = "Neutral",  "val-muted"

bar_w = min(conf, 100)

st.markdown(f"""
<div class="stats-strip">
    <div class="stat-cell">
        <div class="stat-cell-label">Confidence</div>
        <div class="stat-cell-value">{conf}%</div>
        <div class="conf-track"><div class="conf-fill" style="width:{bar_w}%"></div></div>
        <div class="stat-cell-sub">{days}-day horizon</div>
    </div>
    <div class="stat-cell">
        <div class="stat-cell-label">Market Signal</div>
        <div class="stat-cell-value {sig_cls}">{sig_val}</div>
        <div class="stat-cell-sub">NLP sentiment · news data</div>
    </div>
    <div class="stat-cell">
        <div class="stat-cell-label">Algorithm</div>
        <div class="stat-cell-value" style="font-size:18px; letter-spacing:-0.3px;">MLR + RW</div>
        <div class="stat-cell-sub">Multi-var regression · random walk</div>
    </div>
    <div class="stat-cell">
        <div class="stat-cell-label">Data Sources</div>
        <div class="stat-cell-value" style="font-size:18px; letter-spacing:-0.3px;">FRED</div>
        <div class="stat-cell-sub">Brent Crude · USD/PHP · every 5 min</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Forecast table ────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="table-wrap">
    <div class="table-header">
        <span class="table-title">Forecast Table</span>
        <span class="table-meta">{days} days · all grades · ₱/L</span>
    </div>
""", unsafe_allow_html=True)

st.dataframe(
    df[["Date"] + all_fuels].rename(columns={
        FUEL_LABELS["91"]:  "91 RON",
        FUEL_LABELS["95"]:  "95 RON",
        FUEL_LABELS["97"]:  "97+ RON",
        FUEL_LABELS["dsl"]: "Diesel"
    }),
    hide_index=True,
    use_container_width=True,
    height=230
)

st.markdown('</div>', unsafe_allow_html=True)

# ── News ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="news-wrap">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Market News</div>', unsafe_allow_html=True)

news_html = '<div class="news-grid">'
for a in news:
    news_html += f"""
    <div class="news-card">
        <span class="news-tag">{a['source']}</span>
        <div class="news-title">{a['title']}</div>
        <div class="news-body">{a['description']}</div>
        <a href="{a['url']}" target="_blank" class="news-link">Read more →</a>
    </div>"""
news_html += '</div>'
st.markdown(news_html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Info expanders ────────────────────────────────────────────────────────────
st.markdown('<div class="info-wrap">', unsafe_allow_html=True)

with st.expander("How prices are calculated"):
    st.markdown("""
**Data.** Brent Crude spot prices and the USD/PHP exchange rate are fetched from the FRED API (Federal Reserve Economic Data) every 5 minutes.

**Estimation.** A Multiple Linear Regression model maps those indices to domestic pump prices using historical calibration data from prior price adjustments.

**Forecast.** A Stochastic Random Walk simulation — adjusted by an NLP-derived sentiment bias from Philippine fuel news — projects the forward price path over the selected horizon.
    """)

with st.expander("Fuel grade guide"):
    st.markdown("""
- **91 RON — Regular.** Standard unleaded. Petron Xtra Advance, Shell FuelSave, Caltex Silver.
- **95 RON — Premium.** Higher-octane, better knock resistance. Petron XCS, Shell V-Power, Caltex Platinum.
- **97+ RON — Ultra.** Maximum performance for high-compression engines. Petron Blaze 100, Seaoil Extreme 97.
- **Diesel — Standard.** Automotive gas oil for diesel engines. Petron Turbo, Shell V-Power Diesel, Caltex Power Diesel.
    """)

st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="app-footer">
    Developed by Ignacio L. and Andrei B. &nbsp;·&nbsp; © {datetime.now().year}<br>
    Data: FRED API · NewsData.io &nbsp;·&nbsp; Estimates only — not financial advice
</div>
""", unsafe_allow_html=True)
