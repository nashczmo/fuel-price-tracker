import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime, timedelta
import numpy as np
import math

st.set_page_config(page_title="Fuel PH", layout="wide", initial_sidebar_state="collapsed")

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
def css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,500;14..32,600;14..32,700&display=swap');

    :root {
        --white:   #ffffff;
        --bg:      #f5f5f7;
        --ink:     #1d1d1f;
        --ink-2:   #6e6e73;
        --ink-3:   #aeaeb2;
        --sep:     rgba(0,0,0,0.08);
        --blue:    #0071e3;
        --green:   #1a8a3c;
        --red:     #d92b2b;
        --shadow:  0 1px 1px rgba(0,0,0,0.04), 0 2px 8px rgba(0,0,0,0.05);
    }

    *, *::before, *::after {
        font-family: 'Inter', -apple-system, 'SF Pro Text', sans-serif !important;
        box-sizing: border-box;
        -webkit-font-smoothing: antialiased;
    }

    .stApp { background: var(--bg); }
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    #MainMenu, footer { display: none !important; }

    .block-container {
        padding: 64px 0 96px !important;
        max-width: 860px !important;
        margin: 0 auto !important;
    }

    /* ── Animations ─────────────────────────────────── */
    @keyframes up {
        from { opacity:0; transform:translateY(14px); }
        to   { opacity:1; transform:translateY(0); }
    }
    @keyframes in {
        from { opacity:0; }
        to   { opacity:1; }
    }
    @keyframes glow {
        0%,100% { opacity:1; }
        50%     { opacity:.4; }
    }

    .a1 { animation: up .5s cubic-bezier(.22,.68,0,1.2) both; }
    .a2 { animation: up .5s .07s cubic-bezier(.22,.68,0,1.2) both; }
    .a3 { animation: up .5s .14s cubic-bezier(.22,.68,0,1.2) both; }
    .a4 { animation: up .5s .21s cubic-bezier(.22,.68,0,1.2) both; }
    .a5 { animation: up .5s .28s cubic-bezier(.22,.68,0,1.2) both; }
    .a6 { animation: up .5s .35s cubic-bezier(.22,.68,0,1.2) both; }
    .a7 { animation: up .5s .42s cubic-bezier(.22,.68,0,1.2) both; }
    .a8 { animation: in  .6s .5s both; }

    /* ── Header ─────────────────────────────────────── */
    .hdr {
        padding-bottom: 36px;
        border-bottom: 1px solid var(--sep);
        margin-bottom: 44px;
    }

    .hdr-top {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
    }

    .dot {
        width: 7px; height: 7px;
        background: var(--green);
        border-radius: 50%;
        animation: glow 2.4s ease-in-out infinite;
    }

    .ts {
        font-size: 12px;
        font-weight: 400;
        color: var(--ink-3);
        letter-spacing: .01em;
    }

    .hdr-title {
        font-size: 44px;
        font-weight: 700;
        letter-spacing: -1.8px;
        color: var(--ink);
        line-height: 1;
        margin: 0 0 10px;
    }

    .hdr-sub {
        font-size: 16px;
        font-weight: 400;
        color: var(--ink-2);
        max-width: 400px;
        line-height: 1.5;
        margin: 0;
    }

    /* ── Signal banner ──────────────────────────────── */
    .signal {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 14px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 44px;
    }
    .sig-n { background:rgba(0,0,0,.05); color:var(--ink-2); }
    .sig-u { background:rgba(217,43,43,.07); color:var(--red); }
    .sig-d { background:rgba(26,138,60,.08); color:var(--green); }

    /* ── Prices ─────────────────────────────────────── */
    .prices {
        display: grid;
        grid-template-columns: repeat(4,1fr);
        gap: 2px;
        background: var(--sep);
        border-radius: 16px;
        overflow: hidden;
        margin-bottom: 44px;
    }

    .pc {
        background: var(--white);
        padding: 24px 20px 22px;
        transition: background .15s;
        cursor: default;
    }
    .pc:first-child { border-radius: 16px 0 0 16px; }
    .pc:last-child  { border-radius: 0 16px 16px 0; }
    .pc:hover { background: #fafafa; }

    .pc-grade {
        font-size: 10.5px;
        font-weight: 600;
        letter-spacing: .06em;
        text-transform: uppercase;
        color: var(--ink-3);
        margin-bottom: 6px;
    }

    .pc-name {
        font-size: 13px;
        font-weight: 400;
        color: var(--ink-2);
        margin-bottom: 14px;
    }

    .pc-price {
        font-size: 32px;
        font-weight: 700;
        letter-spacing: -1.2px;
        color: var(--ink);
        line-height: 1;
        font-variant-numeric: tabular-nums;
    }

    .pc-sym {
        font-size: 17px;
        font-weight: 300;
        color: var(--ink-3);
        vertical-align: 4px;
        margin-right: 1px;
    }

    .pc-brands {
        font-size: 10.5px;
        font-weight: 400;
        color: var(--ink-3);
        margin-top: 12px;
        line-height: 1.5;
    }

    /* ── Selector ───────────────────────────────────── */
    [data-testid="stSelectbox"] label {
        font-size: 10.5px !important;
        font-weight: 600 !important;
        letter-spacing: .05em !important;
        text-transform: uppercase !important;
        color: var(--ink-3) !important;
    }
    [data-testid="stSelectbox"] > div > div {
        background: var(--white) !important;
        border: 1px solid var(--sep) !important;
        border-radius: 10px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        color: var(--ink) !important;
        box-shadow: var(--shadow) !important;
    }

    /* ── Chart wrap ─────────────────────────────────── */
    .chart-wrap {
        background: var(--white);
        border-radius: 16px;
        box-shadow: var(--shadow);
        padding: 22px 18px 10px;
        margin-bottom: 12px;
    }

    .chart-meta {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 2px;
        padding: 0 4px;
    }

    .chart-title {
        font-size: 15px;
        font-weight: 600;
        letter-spacing: -.2px;
        color: var(--ink);
    }

    .chart-sub {
        font-size: 12px;
        font-weight: 400;
        color: var(--ink-3);
    }

    /* ── Stats ──────────────────────────────────────── */
    .stats {
        display: grid;
        grid-template-columns: repeat(4,1fr);
        gap: 2px;
        background: var(--sep);
        border-radius: 14px;
        overflow: hidden;
        margin-bottom: 44px;
    }

    .sc {
        background: var(--white);
        padding: 18px 18px 16px;
        cursor: default;
        transition: background .15s;
    }
    .sc:first-child { border-radius: 14px 0 0 14px; }
    .sc:last-child  { border-radius: 0 14px 14px 0; }
    .sc:hover { background: #fafafa; }

    .sc-label {
        font-size: 10.5px;
        font-weight: 600;
        letter-spacing: .05em;
        text-transform: uppercase;
        color: var(--ink-3);
        margin-bottom: 8px;
    }

    .sc-value {
        font-size: 22px;
        font-weight: 700;
        letter-spacing: -.6px;
        color: var(--ink);
        line-height: 1;
        font-variant-numeric: tabular-nums;
        margin-bottom: 6px;
    }

    .sc-sub {
        font-size: 11px;
        font-weight: 400;
        color: var(--ink-3);
    }

    .track {
        height: 2px;
        background: rgba(0,0,0,.06);
        border-radius: 1px;
        margin-top: 10px;
        overflow: hidden;
    }
    .fill {
        height: 100%;
        border-radius: 1px;
        background: var(--blue);
    }

    .green { color: var(--green) !important; }
    .red   { color: var(--red)   !important; }
    .muted { color: var(--ink-3) !important; }

    /* ── Table ──────────────────────────────────────── */
    .tbl-wrap {
        background: var(--white);
        border-radius: 16px;
        box-shadow: var(--shadow);
        overflow: hidden;
        margin-bottom: 44px;
    }
    .tbl-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 20px 14px;
        border-bottom: 1px solid var(--sep);
    }
    .tbl-title {
        font-size: 14px;
        font-weight: 600;
        letter-spacing: -.2px;
        color: var(--ink);
    }
    .tbl-meta {
        font-size: 12px;
        font-weight: 400;
        color: var(--ink-3);
    }
    [data-testid="stDataFrame"] { border: none !important; border-radius: 0 !important; }

    /* ── News ───────────────────────────────────────── */
    .news-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2px;
        background: var(--sep);
        border-radius: 16px;
        overflow: hidden;
        margin-bottom: 44px;
    }

    .nc {
        background: var(--white);
        padding: 22px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        transition: background .15s;
        cursor: default;
    }
    .nc:first-child { border-radius: 16px 0 0 16px; }
    .nc:last-child  { border-radius: 0 16px 16px 0; }
    .nc:hover { background: #fafafa; }

    .nc-src {
        font-size: 10.5px;
        font-weight: 600;
        letter-spacing: .05em;
        text-transform: uppercase;
        color: var(--blue);
    }

    .nc-title {
        font-size: 14px;
        font-weight: 600;
        letter-spacing: -.2px;
        color: var(--ink);
        line-height: 1.4;
    }

    .nc-body {
        font-size: 13px;
        font-weight: 400;
        color: var(--ink-2);
        line-height: 1.6;
        flex: 1;
    }

    .nc-link {
        font-size: 13px;
        font-weight: 500;
        color: var(--blue);
        text-decoration: none;
        margin-top: 4px;
    }

    /* ── Expanders ──────────────────────────────────── */
    [data-testid="stExpander"] {
        background: var(--white) !important;
        border: none !important;
        border-radius: 14px !important;
        box-shadow: var(--shadow) !important;
        margin-bottom: 8px;
        overflow: hidden;
    }
    [data-testid="stExpander"] summary {
        font-size: 14px !important;
        font-weight: 600 !important;
        letter-spacing: -.1px !important;
        color: var(--ink) !important;
        padding: 16px 20px !important;
    }
    [data-testid="stExpanderDetails"] {
        font-size: 13.5px !important;
        font-weight: 400 !important;
        color: var(--ink-2) !important;
        line-height: 1.7 !important;
        padding: 0 20px 18px !important;
    }

    /* ── Divider ────────────────────────────────────── */
    .div { border:none; border-top:1px solid var(--sep); margin:0 0 44px; }

    /* ── Footer ─────────────────────────────────────── */
    .ftr {
        text-align: center;
        font-size: 11.5px;
        font-weight: 400;
        color: var(--ink-3);
        line-height: 1.8;
    }

    @media(max-width:720px){
        .block-container { padding: 40px 1rem 80px !important; }
        .hdr-title { font-size:32px; letter-spacing:-1px; }
        .prices, .stats, .news-grid { grid-template-columns:1fr 1fr; }
        .pc:first-child, .pc:nth-child(3) { border-radius: 16px 0 0 0; }
        .pc:nth-child(2), .pc:last-child  { border-radius: 0 16px 0 0; }
        .sc-value { font-size:18px; }
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Model
# ─────────────────────────────────────────────────────────────────────────────
_H   = np.array([[1,74.2,55.8],[1,78.5,56.1],[1,80.2,56.5],[1,82.5,57.0]])
_INV = np.linalg.inv(_H.T @ _H) @ _H.T
W = {
    "91":  _INV @ np.array([50.50,52.10,57.30,59.10]),
    "95":  _INV @ np.array([54.20,56.90,62.10,63.90]),
    "97":  _INV @ np.array([58.10,60.40,65.60,67.40]),
    "dsl": _INV @ np.array([58.00,60.50,72.10,75.90]),
}
LABELS = {
    "91":  "91 RON", "95": "95 RON",
    "97":  "97+ RON", "dsl": "Diesel"
}

def _init():
    if "mkt" not in st.session_state:
        st.session_state.mkt = {"fx":56.10,"p91":72.35,"p95":74.50,"p97":82.30,"dsl":75.10}

@st.cache_data(ttl=300, show_spinner=False)
def _market():
    try:
        k = st.secrets.get("FRED_API_KEY")
        if not k: return st.session_state.mkt
        p = {"api_key":k,"file_type":"json","sort_order":"desc","limit":1}
        rb = requests.get("https://api.stlouisfed.org/api/fred/series/observations?series_id=DCOILBRENTEU",params=p,timeout=4)
        rf = requests.get("https://api.stlouisfed.org/api/fred/series/observations?series_id=DEXPHUS",params=p,timeout=4)
        if rb.ok and rf.ok:
            b = float(rb.json()["observations"][0]["value"])
            f = float(rf.json()["observations"][0]["value"])
            v = np.array([1,b,f])
            d = {"fx":f,"p91":v@W["91"],"p95":v@W["95"],"p97":v@W["97"],"dsl":v@W["dsl"]}
            st.session_state.mkt = d; return d
        return st.session_state.mkt
    except: return st.session_state.mkt

@st.cache_data(ttl=300, show_spinner=False)
def _news():
    fb = [
        {"title":"Legislative Review of Fuel Excise Tax Initiated",
         "description":"National legislators are evaluating modifications to fuel taxation to alleviate domestic price pressures.",
         "url":"#","source":"Market Desk"},
        {"title":"Brent Crude Shifts Impact Philippine Pump Prices",
         "description":"Recent movements in global Brent crude valuations continue to influence retail fuel prices across the Philippine archipelago.",
         "url":"#","source":"Market Desk"},
    ]
    try:
        k = st.secrets.get("NEWSDATA_API_KEY")
        if not k: return fb
        r = requests.get(
            f"https://newsdata.io/api/1/news?apikey={k}&country=ph&q=fuel+OR+oil+OR+gasoline+OR+diesel&language=en",
            timeout=5)
        if r.ok:
            res = r.json().get("results",[])
            if len(res)>=2:
                return [{"title":a.get("title","Update"),
                         "description":(str(a.get("description",""))[:155]+"…"),
                         "url":a.get("link","#"),"source":a.get("source_id","News")} for a in res[:2]]
        return fb
    except: return fb

def _sentiment(articles):
    up   = ["hike","increase","surge","conflict","war","shortage","upward","soar","unrest","tighten"]
    dn   = ["rollback","decrease","drop","slump","surplus","ease","plunge","cheaper","suspend"]
    s = 0
    for a in articles:
        t = f"{a['title']} {a['description']}".lower()
        for w in up: s += .003 if w in t else 0
        for w in dn: s -= .003 if w in t else 0
    return max(min(s,.015),-.015)

@st.cache_data(ttl=300, show_spinner=False)
def _forecast(base, days, bias):
    np.random.seed(42)
    now = datetime.now()
    dates = [(now+timedelta(days=i)).strftime("%b %d") for i in range(days)]
    data = {"Date": dates}
    for g,p in base.items():
        sh = np.random.normal(.002+bias, .012, days)
        data[LABELS[g]] = np.round(p * np.cumprod(1+sh), 2)
    conf = round(100*math.exp(-.01*days), 1)
    return pd.DataFrame(data), conf


# ─────────────────────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────────────────────
css(); _init()

mkt  = _market()
news = _news()
bias = _sentiment(news)
base = {"91":mkt["p91"],"95":mkt["p95"],"97":mkt["p97"],"dsl":mkt["dsl"]}

# horizon selectbox (rendered before layout so cache key is stable)
col_sel, _ = st.columns([1,3])
with col_sel:
    period = st.selectbox("Forecast window", ["7 Days","14 Days","30 Days"])
days = int(period.split()[0])

df, conf = _forecast(base, days, bias)
p91, p95, p97, pdsl = (df[LABELS[g]].iloc[0] for g in ["91","95","97","dsl"])
ts = datetime.now().strftime("%B %d, %Y · %I:%M %p")

# ── Signal ───────────────────────────────────────────────────────────────────
if   bias > .005:  sc, si, sm = "sig-u", "↑", "Price increase likely this cycle."
elif bias < -.005: sc, si, sm = "sig-d", "↓", "Rollback possible — market softening."
else:              sc, si, sm = "sig-n", "—", "Stable outlook. Indices within normal range."

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hdr a1">
  <div class="hdr-top">
    <span class="dot"></span>
    <span class="ts">{ts}</span>
  </div>
  <div class="hdr-title">Fuel Prices</div>
  <div class="hdr-sub">Estimated Philippine pump prices, updated every 5 minutes.</div>
</div>
""", unsafe_allow_html=True)

# ── Signal ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="a2">
  <div class="signal {sc}">{si}&nbsp;&nbsp;{sm}</div>
</div>
""", unsafe_allow_html=True)

# ── Price grid ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="prices a3">
  <div class="pc">
    <div class="pc-grade">RON 91</div>
    <div class="pc-name">Regular</div>
    <div class="pc-price"><span class="pc-sym">₱</span>{p91:.2f}</div>
    <div class="pc-brands">Xtra Advance · FuelSave · Silver</div>
  </div>
  <div class="pc">
    <div class="pc-grade">RON 95</div>
    <div class="pc-name">Premium</div>
    <div class="pc-price"><span class="pc-sym">₱</span>{p95:.2f}</div>
    <div class="pc-brands">XCS · V-Power · Platinum</div>
  </div>
  <div class="pc">
    <div class="pc-grade">RON 97+</div>
    <div class="pc-name">Ultra</div>
    <div class="pc-price"><span class="pc-sym">₱</span>{p97:.2f}</div>
    <div class="pc-brands">Blaze 100 · Extreme 97</div>
  </div>
  <div class="pc">
    <div class="pc-grade">Diesel</div>
    <div class="pc-name">Standard</div>
    <div class="pc-price"><span class="pc-sym">₱</span>{pdsl:.2f}</div>
    <div class="pc-brands">Turbo · Max · Power Diesel</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Chart ────────────────────────────────────────────────────────────────────
all_cols = list(LABELS.values())
melted   = df[["Date"]+all_cols].melt("Date", var_name="Grade", value_name="₱")

chart = (
    alt.Chart(melted)
    .mark_line(strokeWidth=1.8, point=alt.OverlayMarkDef(size=40, filled=True))
    .encode(
        x=alt.X("Date:N", sort=None, title=None,
            axis=alt.Axis(grid=False, labelColor="#aeaeb2", labelFont="Inter",
                          labelFontSize=11, labelFontWeight=400,
                          tickColor="rgba(0,0,0,.06)", domainColor="rgba(0,0,0,.06)")),
        y=alt.Y("₱:Q", scale=alt.Scale(zero=False), title="₱ per litre",
            axis=alt.Axis(grid=True, gridColor="rgba(0,0,0,.04)", gridDash=[3,3],
                          labelColor="#aeaeb2", titleColor="#aeaeb2",
                          labelFont="Inter", titleFont="Inter",
                          labelFontSize=11, titleFontSize=11,
                          domainOpacity=0, tickCount=5)),
        color=alt.Color("Grade:N",
            scale=alt.Scale(
                domain=["91 RON","95 RON","97+ RON","Diesel"],
                range=["#1a8a3c","#0071e3","#5856d6","#bf5200"]
            ),
            legend=alt.Legend(orient="bottom", title=None,
                              labelColor="#6e6e73", labelFont="Inter",
                              labelFontSize=12, labelFontWeight=500,
                              symbolSize=80, symbolStrokeWidth=2.5,
                              padding=14, columnPadding=20)),
        tooltip=[
            alt.Tooltip("Date:N", title="Date"),
            alt.Tooltip("Grade:N", title="Grade"),
            alt.Tooltip("₱:Q", title="Price (₱)", format=".2f"),
        ]
    )
    .properties(height=320, background="#ffffff",
                padding={"left":12,"right":12,"top":12,"bottom":8})
    .configure_view(strokeWidth=0, cornerRadius=16)
    .configure_axis(domain=False)
)

st.markdown(f"""
<div class="chart-wrap a4">
  <div class="chart-meta">
    <span class="chart-title">Price Forecast</span>
    <span class="chart-sub">{days} days · all grades</span>
  </div>
</div>
""", unsafe_allow_html=True)

# Render chart directly (Streamlit renders after the markdown)
with st.container():
    st.markdown('<div class="a4" style="margin-top:-8px; background:#fff; border-radius:0 0 16px 16px; box-shadow:0 1px 1px rgba(0,0,0,.04),0 2px 8px rgba(0,0,0,.05); padding:0 18px 10px; margin-bottom:12px;">', unsafe_allow_html=True)
    st.altair_chart(chart, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Stats ────────────────────────────────────────────────────────────────────
if   bias > .003:  sv, sc2 = "Bullish", "green"
elif bias < -.003: sv, sc2 = "Bearish", "red"
else:              sv, sc2 = "Neutral",  "muted"

st.markdown(f"""
<div class="stats a5">
  <div class="sc">
    <div class="sc-label">Confidence</div>
    <div class="sc-value">{conf}%</div>
    <div class="track"><div class="fill" style="width:{min(conf,100)}%"></div></div>
    <div class="sc-sub">{days}-day horizon</div>
  </div>
  <div class="sc">
    <div class="sc-label">Signal</div>
    <div class="sc-value {sc2}">{sv}</div>
    <div class="sc-sub">NLP · news sentiment</div>
  </div>
  <div class="sc">
    <div class="sc-label">Model</div>
    <div class="sc-value" style="font-size:17px;letter-spacing:-.3px">MLR + RW</div>
    <div class="sc-sub">Regression · random walk</div>
  </div>
  <div class="sc">
    <div class="sc-label">Refresh</div>
    <div class="sc-value" style="font-size:17px;letter-spacing:-.3px">5 min</div>
    <div class="sc-sub">FRED API · Brent · USD/PHP</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Table ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="tbl-wrap a6">
  <div class="tbl-head">
    <span class="tbl-title">Forecast Table</span>
    <span class="tbl-meta">{days} days · ₱ per litre</span>
  </div>
""", unsafe_allow_html=True)
st.dataframe(df[["Date"]+all_cols], hide_index=True,
             use_container_width=True, height=210)
st.markdown('</div>', unsafe_allow_html=True)

# ── News ──────────────────────────────────────────────────────────────────────
nh = '<div class="news-grid a7">'
for a in news:
    nh += f"""
  <div class="nc">
    <div class="nc-src">{a['source']}</div>
    <div class="nc-title">{a['title']}</div>
    <div class="nc-body">{a['description']}</div>
    <a href="{a['url']}" target="_blank" class="nc-link">Read more →</a>
  </div>"""
nh += '</div>'
st.markdown(nh, unsafe_allow_html=True)

# ── Info ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="a7">', unsafe_allow_html=True)
with st.expander("How prices are calculated"):
    st.markdown("""
**Data** — Brent Crude spot prices and the USD/PHP rate are fetched from the FRED API every 5 minutes.

**Estimation** — A Multiple Linear Regression model maps those indices to domestic pump prices using historical price data.

**Forecast** — A Stochastic Random Walk, adjusted by an NLP sentiment score from Philippine fuel news, projects forward prices over the selected horizon.
    """)
with st.expander("Fuel grade guide"):
    st.markdown("""
- **91 RON** — Standard unleaded. Petron Xtra Advance, Shell FuelSave, Caltex Silver.
- **95 RON** — Premium, higher-octane. Petron XCS, Shell V-Power, Caltex Platinum.
- **97+ RON** — Ultra-performance. Petron Blaze 100, Seaoil Extreme 97.
- **Diesel** — Standard gas oil. Petron Turbo, Shell V-Power Diesel, Caltex Power Diesel.
    """)
st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<hr class="div">
<div class="ftr a8">
  Developed by Ignacio L. and Andrei B. · © {datetime.now().year}<br>
  Estimates only — not financial advice · Data: FRED API · NewsData.io
</div>
""", unsafe_allow_html=True)
