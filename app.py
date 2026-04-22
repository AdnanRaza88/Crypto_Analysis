import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import anthropic
import time
from datetime import datetime, timedelta

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Crypto Analyzer Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700;800&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'Exo 2', sans-serif !important;
    background-color: #050d1a !important;
    color: #c8dff0 !important;
}

/* Main background */
.stApp { background: linear-gradient(135deg, #050d1a 0%, #081626 50%, #050d1a 100%); }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060f20 0%, #081828 100%) !important;
    border-right: 1px solid rgba(0,150,200,.2) !important;
}
[data-testid="stSidebar"] * { color: #a0c0d8 !important; }

/* Metric cards */
[data-testid="stMetric"] {
    background: rgba(0,20,45,.7) !important;
    border: 1px solid rgba(0,120,180,.25) !important;
    border-radius: 10px !important;
    padding: 14px 18px !important;
}
[data-testid="stMetricLabel"] { font-size: 10px !important; letter-spacing: 2px !important; color: #3a7a9a !important; text-transform: uppercase !important; }
[data-testid="stMetricValue"] { font-family: 'Share Tech Mono', monospace !important; font-size: 22px !important; color: #fff !important; }
[data-testid="stMetricDelta"] { font-size: 12px !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, rgba(0,160,220,.25), rgba(0,100,160,.25)) !important;
    border: 1.5px solid #00c8ff !important;
    color: #00c8ff !important;
    border-radius: 8px !important;
    font-family: 'Exo 2', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    transition: all .2s !important;
    padding: 10px 24px !important;
}
.stButton > button:hover {
    background: rgba(0,200,255,.2) !important;
    box-shadow: 0 0 20px rgba(0,200,255,.3) !important;
    transform: translateY(-1px) !important;
}

/* Select boxes */
.stSelectbox > div > div {
    background: rgba(0,15,35,.9) !important;
    border: 1px solid rgba(0,120,180,.35) !important;
    border-radius: 7px !important;
    color: #c8dff0 !important;
}

/* Text input */
.stTextInput > div > div > input {
    background: rgba(0,15,35,.9) !important;
    border: 1px solid rgba(0,120,180,.35) !important;
    border-radius: 7px !important;
    color: #c8dff0 !important;
    font-family: 'Share Tech Mono', monospace !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(0,100,160,.3) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    color: #3a6a8a !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    font-size: 12px !important;
    padding: 10px 20px !important;
}
.stTabs [aria-selected="true"] {
    border-bottom-color: #00c8ff !important;
    color: #00c8ff !important;
}

/* Info/success/error boxes */
.stAlert { border-radius: 8px !important; border-left: 3px solid !important; }

/* Header cards */
.header-card {
    background: linear-gradient(135deg, rgba(0,25,50,.9), rgba(0,15,35,.9));
    border: 1px solid rgba(0,120,180,.3);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
.section-title {
    font-size: 9px;
    color: #1a5a7a;
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-bottom: 12px;
    font-family: 'Share Tech Mono', monospace;
}
.price-big {
    font-family: 'Share Tech Mono', monospace;
    font-size: 36px;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.1;
}
.coin-name {
    font-family: 'Share Tech Mono', monospace;
    font-size: 14px;
    color: #3a7a9a;
    margin-top: 4px;
}

/* Indicator badge */
.ind-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    margin: 2px;
}
.bull { background: rgba(0,220,100,.12); border: 1px solid rgba(0,220,100,.4); color: #00dc64; }
.bear { background: rgba(255,60,80,.12); border: 1px solid rgba(255,60,80,.4); color: #ff3c50; }
.neutral { background: rgba(255,180,0,.12); border: 1px solid rgba(255,180,0,.4); color: #ffb400; }

/* Signal box */
.signal-box {
    border-radius: 10px;
    padding: 16px 20px;
    margin: 10px 0;
    font-weight: 700;
    font-size: 16px;
    text-align: center;
    letter-spacing: 2px;
}
.signal-bull { background: rgba(0,220,100,.1); border: 2px solid rgba(0,220,100,.4); color: #00dc64; }
.signal-bear { background: rgba(255,60,80,.1); border: 2px solid rgba(255,60,80,.4); color: #ff3c50; }
.signal-neutral { background: rgba(255,180,0,.1); border: 2px solid rgba(255,180,0,.4); color: #ffb400; }

/* Analysis output */
.analysis-box {
    background: rgba(3,10,22,.98);
    border: 1px solid rgba(0,180,220,.2);
    border-radius: 12px;
    padding: 24px;
    font-family: 'Exo 2', sans-serif;
    line-height: 1.8;
    font-size: 14px;
    color: #b0c8dc;
}
.analysis-section {
    color: #00c8ff;
    font-weight: 800;
    font-size: 12px;
    letter-spacing: 3px;
    border-bottom: 1px solid rgba(0,200,255,.15);
    padding-bottom: 5px;
    margin: 18px 0 10px;
    text-transform: uppercase;
}
.analysis-action-buy {
    background: rgba(0,220,100,.1);
    border: 1px solid rgba(0,220,100,.35);
    border-radius: 8px;
    padding: 12px 16px;
    color: #00dc64;
    font-weight: 800;
    font-size: 16px;
    margin: 8px 0;
}
.analysis-action-sell {
    background: rgba(255,60,80,.1);
    border: 1px solid rgba(255,60,80,.35);
    border-radius: 8px;
    padding: 12px 16px;
    color: #ff3c50;
    font-weight: 800;
    font-size: 16px;
    margin: 8px 0;
}
.disclaimer-box {
    background: rgba(180,130,0,.06);
    border: 1px solid rgba(180,130,0,.2);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 11px;
    color: #6a5520;
    margin-top: 16px;
    line-height: 1.6;
}

/* Divider */
hr { border-color: rgba(0,80,130,.3) !important; }

/* Expander */
[data-testid="stExpander"] {
    background: rgba(0,15,35,.7) !important;
    border: 1px solid rgba(0,80,130,.25) !important;
    border-radius: 8px !important;
}

/* Progress bar */
.stProgress > div > div > div { background: linear-gradient(90deg, #00c8ff, #00ff88) !important; border-radius: 4px !important; }
</style>
""", unsafe_allow_html=True)


# ─── CONSTANTS ───────────────────────────────────────────────────────────────
POPULAR_COINS = {
    "BTC — Bitcoin": "bitcoin",
    "ETH — Ethereum": "ethereum",
    "BNB — BNB": "binancecoin",
    "SOL — Solana": "solana",
    "XRP — Ripple": "ripple",
    "DOGE — Dogecoin": "dogecoin",
    "ADA — Cardano": "cardano",
    "AVAX — Avalanche": "avalanche-2",
    "LINK — Chainlink": "chainlink",
    "SUI — Sui": "sui",
    "PEPE — Pepe": "pepe",
    "SHIB — Shiba Inu": "shiba-inu",
    "TRX — Tron": "tron",
    "DOT — Polkadot": "polkadot",
    "MATIC — Polygon": "matic-network",
}

# ─── COINGECKO API ───────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def fetch_coin_info(coin_id: str):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=60)
def fetch_ohlc(coin_id: str, days: int = 30):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    r = requests.get(url, timeout=15)
    if not r.ok:
        return pd.DataFrame()
    data = r.json()
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

@st.cache_data(ttl=60)
def fetch_market_chart(coin_id: str, days: int = 30):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}&interval=daily"
    r = requests.get(url, timeout=15)
    if not r.ok:
        return pd.DataFrame()
    data = r.json()
    prices = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    volumes = pd.DataFrame(data["total_volumes"], columns=["timestamp", "volume"])
    df = prices.merge(volumes, on="timestamp")
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

# ─── TECHNICAL INDICATORS ────────────────────────────────────────────────────
def calc_rsi(closes: pd.Series, period: int = 14) -> float:
    if len(closes) < period + 2:
        return None
    delta = closes.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean().iloc[-1]
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean().iloc[-1]
    if avg_loss == 0:
        return 100.0
    return round(100 - 100 / (1 + avg_gain / avg_loss), 2)

def calc_rsi_series(closes: pd.Series, period: int = 14) -> pd.Series:
    delta = closes.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - 100 / (1 + rs)

def calc_macd(closes: pd.Series):
    if len(closes) < 26:
        return None, None, None
    ema12 = closes.ewm(span=12, adjust=False).mean()
    ema26 = closes.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal = macd_line.ewm(span=9, adjust=False).mean()
    hist = macd_line - signal
    return macd_line, signal, hist

def calc_bollinger(closes: pd.Series, period: int = 20):
    mid = closes.rolling(period).mean()
    std = closes.rolling(period).std()
    upper = mid + 2 * std
    lower = mid - 2 * std
    return upper, mid, lower

def calc_stochastic(df: pd.DataFrame, period: int = 14):
    low_min = df["low"].rolling(period).min()
    high_max = df["high"].rolling(period).max()
    k = 100 * (df["close"] - low_min) / (high_max - low_min + 1e-10)
    d = k.rolling(3).mean()
    return k, d

def calc_atr(df: pd.DataFrame, period: int = 14) -> float:
    tr = pd.concat([
        df["high"] - df["low"],
        (df["high"] - df["close"].shift()).abs(),
        (df["low"] - df["close"].shift()).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(span=period, adjust=False).mean().iloc[-1]

def calc_vwap(df: pd.DataFrame) -> float:
    typical = (df["high"] + df["low"] + df["close"]) / 3
    return (typical * (df.get("volume", pd.Series(np.ones(len(df)))))).sum() / max(df.get("volume", pd.Series(np.ones(len(df)))).sum(), 1e-10)

def detect_price_action(df: pd.DataFrame):
    """Detect candlestick patterns"""
    patterns = []
    if len(df) < 3:
        return patterns
    last = df.iloc[-1]
    prev = df.iloc[-2]
    body = abs(last["close"] - last["open"])
    rng = last["high"] - last["low"]
    upper_wick = last["high"] - max(last["close"], last["open"])
    lower_wick = min(last["close"], last["open"]) - last["low"]

    # Doji
    if rng > 0 and body / rng < 0.1:
        patterns.append(("Doji ⚖️", "neutral", "Indecision — reversal possible"))
    # Hammer
    if lower_wick > 2 * body and upper_wick < body:
        patterns.append(("Hammer 🔨", "bullish", "Bullish reversal signal"))
    # Shooting Star
    if upper_wick > 2 * body and lower_wick < body:
        patterns.append(("Shooting Star 🌟", "bearish", "Bearish reversal signal"))
    # Bullish engulfing
    if (last["close"] > last["open"] and prev["close"] < prev["open"] and
            last["close"] > prev["open"] and last["open"] < prev["close"]):
        patterns.append(("Bullish Engulfing 🟢", "bullish", "Strong buy signal"))
    # Bearish engulfing
    if (last["close"] < last["open"] and prev["close"] > prev["open"] and
            last["open"] > prev["close"] and last["close"] < prev["open"]):
        patterns.append(("Bearish Engulfing 🔴", "bearish", "Strong sell signal"))
    # Marubozu
    if rng > 0 and body / rng > 0.9:
        if last["close"] > last["open"]:
            patterns.append(("Bullish Marubozu 💪", "bullish", "Very strong buying pressure"))
        else:
            patterns.append(("Bearish Marubozu 😱", "bearish", "Very strong selling pressure"))
    return patterns

def calc_volatility(closes: pd.Series, period: int = 14) -> dict:
    returns = closes.pct_change().dropna()
    daily_vol = returns.tail(period).std()
    annual_vol = daily_vol * np.sqrt(365) * 100
    return {
        "daily_pct": round(daily_vol * 100, 2),
        "annual_pct": round(annual_vol, 2),
        "level": "HIGH 🔴" if annual_vol > 100 else "MEDIUM 🟡" if annual_vol > 50 else "LOW 🟢",
    }

def calc_volume_analysis(df_chart: pd.DataFrame, df_ohlc: pd.DataFrame) -> dict:
    if df_chart.empty or len(df_chart) < 6:
        return {}
    recent_vol = df_chart["volume"].tail(3).mean()
    older_vol = df_chart["volume"].iloc[-7:-3].mean()
    vol_ratio = recent_vol / max(older_vol, 1)
    trend = "Rising 📈" if vol_ratio > 1.1 else "Falling 📉" if vol_ratio < 0.9 else "Stable ➡️"
    avg_vol = df_chart["volume"].mean()
    today_vol = df_chart["volume"].iloc[-1]
    return {
        "trend": trend,
        "ratio": round(vol_ratio, 2),
        "vs_avg": round((today_vol / max(avg_vol, 1)) * 100, 1),
        "signal": "High Volume 🔥" if vol_ratio > 1.2 else "Low Volume ⚠️" if vol_ratio < 0.8 else "Normal Volume",
    }

def calc_support_resistance(df: pd.DataFrame):
    if len(df) < 10:
        return None, None
    recent = df.tail(20)
    support = recent["low"].min()
    resistance = recent["high"].max()
    return support, resistance

def calc_fibonacci(high: float, low: float) -> dict:
    diff = high - low
    return {
        "0.236": round(high - 0.236 * diff, 6),
        "0.382": round(high - 0.382 * diff, 6),
        "0.500": round(high - 0.500 * diff, 6),
        "0.618": round(high - 0.618 * diff, 6),
        "0.786": round(high - 0.786 * diff, 6),
    }

def calc_probability(indicators: dict) -> dict:
    """Calculate bull/bear probability from all signals"""
    bull_score = 0
    bear_score = 0
    signals = []

    rsi = indicators.get("rsi")
    if rsi:
        if rsi < 30:
            bull_score += 3
            signals.append(("RSI Oversold", "bull", f"RSI={rsi} — strong buy zone"))
        elif rsi > 70:
            bear_score += 3
            signals.append(("RSI Overbought", "bear", f"RSI={rsi} — strong sell zone"))
        elif rsi < 45:
            bear_score += 1
            signals.append(("RSI Weak", "bear", f"RSI={rsi} — below midline"))
        elif rsi > 55:
            bull_score += 1
            signals.append(("RSI Strong", "bull", f"RSI={rsi} — above midline"))

    stoch_k = indicators.get("stoch_k")
    if stoch_k is not None:
        if stoch_k < 20:
            bull_score += 2
            signals.append(("Stoch Oversold", "bull", f"Stoch={stoch_k:.0f} — oversold"))
        elif stoch_k > 80:
            bear_score += 2
            signals.append(("Stoch Overbought", "bear", f"Stoch={stoch_k:.0f} — overbought"))

    macd_bull = indicators.get("macd_bullish")
    if macd_bull is True:
        bull_score += 2
        signals.append(("MACD Bullish", "bull", "MACD above signal line"))
    elif macd_bull is False:
        bear_score += 2
        signals.append(("MACD Bearish", "bear", "MACD below signal line"))

    trend = indicators.get("trend")
    if trend == "up":
        bull_score += 2
        signals.append(("Uptrend", "bull", "Price in uptrend"))
    elif trend == "down":
        bear_score += 2
        signals.append(("Downtrend", "bear", "Price in downtrend"))

    price = indicators.get("price")
    ma50 = indicators.get("ma50")
    ma200 = indicators.get("ma200")
    if price and ma50:
        if price > ma50:
            bull_score += 1
            signals.append(("Above MA50", "bull", f"Price > MA50 ({fmt_price(ma50)})"))
        else:
            bear_score += 1
            signals.append(("Below MA50", "bear", f"Price < MA50 ({fmt_price(ma50)})"))
    if price and ma200:
        if price > ma200:
            bull_score += 2
            signals.append(("Above MA200", "bull", f"Price > MA200 ({fmt_price(ma200)})"))
        else:
            bear_score += 2
            signals.append(("Below MA200", "bear", f"Price < MA200 ({fmt_price(ma200)})"))

    bb_sig = indicators.get("bb_signal")
    if bb_sig == "oversold":
        bull_score += 2
        signals.append(("BB Oversold", "bull", "Price below lower Bollinger Band"))
    elif bb_sig == "overbought":
        bear_score += 2
        signals.append(("BB Overbought", "bear", "Price above upper Bollinger Band"))

    vol = indicators.get("volume_ratio")
    ch24 = indicators.get("change_24h")
    if vol and ch24:
        if vol > 1.2 and ch24 > 0:
            bull_score += 1
            signals.append(("High Vol + Up", "bull", "Strong buying with volume"))
        elif vol > 1.2 and ch24 < 0:
            bear_score += 1
            signals.append(("High Vol + Down", "bear", "Strong selling with volume"))

    total = bull_score + bear_score
    bull_pct = round((bull_score / max(total, 1)) * 100)
    bear_pct = 100 - bull_pct

    overall = "BULLISH" if bull_pct >= 62 else "BEARISH" if bull_pct <= 38 else "NEUTRAL"
    return {
        "bull_pct": bull_pct,
        "bear_pct": bear_pct,
        "overall": overall,
        "signals": signals,
        "bull_score": bull_score,
        "bear_score": bear_score,
    }

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def fmt_price(n):
    if n is None:
        return "—"
    if n >= 1000:
        return f"${n:,.2f}"
    if n >= 1:
        return f"${n:.4f}"
    if n >= 0.0001:
        return f"${n:.6f}"
    return f"${n:.2e}"

def fmt_pct(n):
    if n is None:
        return "—"
    return f"+{n:.2f}%" if n >= 0 else f"{n:.2f}%"

def fmt_large(n):
    if n is None:
        return "—"
    if n >= 1e9:
        return f"${n/1e9:.2f}B"
    if n >= 1e6:
        return f"${n/1e6:.1f}M"
    if n >= 1e3:
        return f"${n/1e3:.1f}K"
    return f"${n:.0f}"

def pct_color(v):
    if v is None:
        return "gray"
    return "#00dc64" if v >= 0 else "#ff3c50"

# ─── CHARTS ──────────────────────────────────────────────────────────────────
def build_main_chart(df: pd.DataFrame, df_chart: pd.DataFrame, sym: str):
    if df.empty:
        return None

    closes = df["close"]
    bb_upper, bb_mid, bb_lower = calc_bollinger(closes)
    macd_line, macd_sig, macd_hist = calc_macd(closes)
    rsi_series = calc_rsi_series(closes)
    stoch_k, stoch_d = calc_stochastic(df)

    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        row_heights=[0.5, 0.18, 0.16, 0.16],
        vertical_spacing=0.02,
        subplot_titles=["", "Volume", "RSI (14)", "MACD"],
    )

    # ── Candlestick ──
    fig.add_trace(go.Candlestick(
        x=df["timestamp"], open=df["open"], high=df["high"],
        low=df["low"], close=df["close"],
        name="Price",
        increasing=dict(fillcolor="#00dc64", line=dict(color="#00dc64", width=1)),
        decreasing=dict(fillcolor="#ff3c50", line=dict(color="#ff3c50", width=1)),
    ), row=1, col=1)

    # BB
    fig.add_trace(go.Scatter(x=df["timestamp"], y=bb_upper, name="BB Upper",
        line=dict(color="rgba(0,200,255,.35)", width=1, dash="dot"), showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["timestamp"], y=bb_lower, name="BB Lower",
        line=dict(color="rgba(0,200,255,.35)", width=1, dash="dot"),
        fill="tonexty", fillcolor="rgba(0,150,200,.04)", showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["timestamp"], y=bb_mid, name="BB Mid",
        line=dict(color="rgba(0,200,255,.5)", width=1), showlegend=False), row=1, col=1)

    # MA50 & MA200
    ma50_s = closes.rolling(50).mean()
    ma200_s = closes.rolling(200).mean()
    fig.add_trace(go.Scatter(x=df["timestamp"], y=ma50_s, name="MA50",
        line=dict(color="#ffa500", width=1.5)), row=1, col=1)
    if ma200_s.notna().sum() > 5:
        fig.add_trace(go.Scatter(x=df["timestamp"], y=ma200_s, name="MA200",
            line=dict(color="#ff6b6b", width=1.5)), row=1, col=1)

    # ── Volume ──
    colors = ["#00dc64" if c >= o else "#ff3c50" for c, o in zip(df["close"], df["open"])]
    if not df_chart.empty:
        fig.add_trace(go.Bar(x=df_chart["timestamp"], y=df_chart["volume"], name="Volume",
            marker_color=colors[:len(df_chart)], opacity=0.7, showlegend=False), row=2, col=1)

    # ── RSI ──
    fig.add_trace(go.Scatter(x=df["timestamp"], y=rsi_series, name="RSI",
        line=dict(color="#00c8ff", width=1.5), showlegend=False), row=3, col=1)
    fig.add_hline(y=70, line=dict(color="rgba(255,60,80,.4)", dash="dash", width=1), row=3, col=1)
    fig.add_hline(y=30, line=dict(color="rgba(0,220,100,.4)", dash="dash", width=1), row=3, col=1)
    fig.add_hline(y=50, line=dict(color="rgba(255,255,255,.1)", dash="dot", width=1), row=3, col=1)

    # ── MACD ──
    if macd_line is not None:
        hist_colors = ["#00dc64" if v >= 0 else "#ff3c50" for v in macd_hist.fillna(0)]
        fig.add_trace(go.Bar(x=df["timestamp"], y=macd_hist, name="MACD Hist",
            marker_color=hist_colors, opacity=0.7, showlegend=False), row=4, col=1)
        fig.add_trace(go.Scatter(x=df["timestamp"], y=macd_line, name="MACD",
            line=dict(color="#00c8ff", width=1.5), showlegend=False), row=4, col=1)
        fig.add_trace(go.Scatter(x=df["timestamp"], y=macd_sig, name="Signal",
            line=dict(color="#ffa500", width=1.5), showlegend=False), row=4, col=1)

    fig.update_layout(
        height=700,
        template="plotly_dark",
        paper_bgcolor="rgba(5,13,26,0)",
        plot_bgcolor="rgba(0,15,35,.5)",
        font=dict(family="Exo 2, sans-serif", color="#7a9ab8", size=10),
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis_rangeslider_visible=False,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
        title=dict(text=f"{sym} — Technical Chart", font=dict(color="#00c8ff", size=14)),
    )
    for i in range(1, 5):
        fig.update_xaxes(
            gridcolor="rgba(0,80,130,.15)", row=i, col=1,
            showgrid=True, zeroline=False,
        )
        fig.update_yaxes(
            gridcolor="rgba(0,80,130,.15)", row=i, col=1,
            showgrid=True, zeroline=False,
        )
    return fig

def build_probability_gauge(bull_pct: int):
    color = "#00dc64" if bull_pct >= 60 else "#ff3c50" if bull_pct <= 40 else "#ffb400"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=bull_pct,
        title=dict(text="BULL PROBABILITY %", font=dict(color="#3a7a9a", size=11, family="Exo 2")),
        number=dict(font=dict(color=color, size=36, family="Share Tech Mono"), suffix="%"),
        gauge=dict(
            axis=dict(range=[0, 100], tickwidth=0, tickcolor="transparent",
                      tickfont=dict(color="#2a5a7a", size=9)),
            bar=dict(color=color, thickness=0.25),
            bgcolor="rgba(0,20,45,.6)",
            borderwidth=0,
            steps=[
                dict(range=[0, 38], color="rgba(255,60,80,.08)"),
                dict(range=[38, 62], color="rgba(255,180,0,.08)"),
                dict(range=[62, 100], color="rgba(0,220,100,.08)"),
            ],
            threshold=dict(line=dict(color=color, width=3), thickness=0.8, value=bull_pct),
        ),
    ))
    fig.update_layout(
        height=200, margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Exo 2"),
    )
    return fig

def build_volatility_chart(closes: pd.Series):
    returns = closes.pct_change().dropna() * 100
    fig = go.Figure()
    colors = ["#00dc64" if v >= 0 else "#ff3c50" for v in returns]
    fig.add_trace(go.Bar(y=returns, marker_color=colors, opacity=0.8, name="Daily Return %"))
    fig.update_layout(
        height=180, template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,15,35,.5)",
        margin=dict(l=0, r=0, t=10, b=0),
        font=dict(family="Exo 2", color="#7a9ab8", size=9),
        showlegend=False,
        xaxis=dict(gridcolor="rgba(0,80,130,.1)"),
        yaxis=dict(gridcolor="rgba(0,80,130,.1)", ticksuffix="%"),
    )
    return fig

# ─── AI ANALYSIS ─────────────────────────────────────────────────────────────
def get_ai_analysis(coin_info: dict, indicators: dict, prob: dict, mtype: str, api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    sym = coin_info.get("symbol", "").upper()
    name = coin_info.get("name", "")
    md = coin_info.get("market_data", {})
    price = md.get("current_price", {}).get("usd")

    prompt = f"""Tum ek expert crypto trading analyst ho. Neeche diye gaye complete data ko analyze karke {mtype.upper()} trading ke liye detailed analysis do. Response Hinglish mein likho (Roman script, Hindi+English mix). Specific prices dena zaroori hai.

=== COIN INFORMATION ===
Coin: {name} ({sym})
Current Price: {fmt_price(price)}
24h Change: {fmt_pct(md.get('price_change_percentage_24h'))}
7d Change: {fmt_pct(md.get('price_change_percentage_7d'))}
30d Change: {fmt_pct(md.get('price_change_percentage_30d'))}
Market Cap: {fmt_large(md.get('market_cap', {}).get('usd'))}
Volume 24h: {fmt_large(md.get('total_volume', {}).get('usd'))}
ATH: {fmt_price(md.get('ath', {}).get('usd'))} ({fmt_pct(md.get('ath_change_percentage', {}).get('usd'))} from ATH)
Circulating Supply: {md.get('circulating_supply', 0)/1e6:.1f}M

=== TECHNICAL INDICATORS ===
RSI (14): {indicators.get('rsi', 'N/A')}
Stochastic K: {indicators.get('stoch_k', 'N/A'):.1f if indicators.get('stoch_k') else 'N/A'}
Stochastic D: {indicators.get('stoch_d', 'N/A'):.1f if indicators.get('stoch_d') else 'N/A'}
MACD Signal: {'Bullish ✅' if indicators.get('macd_bullish') else 'Bearish ❌'}
Trend (7d): {indicators.get('trend_label', 'N/A')}
MA50: {fmt_price(indicators.get('ma50'))}
MA200: {fmt_price(indicators.get('ma200'))}
Bollinger Upper: {fmt_price(indicators.get('bb_upper'))}
Bollinger Mid: {fmt_price(indicators.get('bb_mid'))}
Bollinger Lower: {fmt_price(indicators.get('bb_lower'))}
BB Signal: {indicators.get('bb_signal', 'N/A')}
Support (20d): {fmt_price(indicators.get('support'))}
Resistance (20d): {fmt_price(indicators.get('resistance'))}
ATR (Volatility): {fmt_price(indicators.get('atr'))}
Daily Volatility: {indicators.get('volatility', {}).get('daily_pct', 'N/A')}%
Annual Volatility: {indicators.get('volatility', {}).get('annual_pct', 'N/A')}%
Volume Trend: {indicators.get('volume', {}).get('trend', 'N/A')}
Volume vs Avg: {indicators.get('volume', {}).get('vs_avg', 'N/A')}%
Price Action Patterns: {', '.join([p[0] for p in indicators.get('patterns', [])]) or 'No clear pattern'}

=== PROBABILITY ANALYSIS ===
Bull Probability: {prob.get('bull_pct')}%
Bear Probability: {prob.get('bear_pct')}%
Overall Signal: {prob.get('overall')}
Active Bull Signals: {prob.get('bull_score')}
Active Bear Signals: {prob.get('bear_score')}

=== MARKET TYPE: {mtype.upper()} ===

Yeh EXACT format mein jawab do — koi extra text nahi:

## MARKET OVERVIEW
[2-3 lines mein current market situation aur kya ho raha hai]

## TECHNICAL ANALYSIS
**RSI ({indicators.get('rsi')}):** [detailed explanation]
**MACD:** [bullish/bearish aur kya matlab hai]
**Bollinger Bands:** [price kahan hai aur kya signal hai]
**Stochastic:** [overbought/oversold analysis]
**Moving Averages:** [MA50/MA200 ke relative position ka matlab]
**Volume Analysis:** [volume trend ka trading par kya asar]
**Volatility:** [ATR aur volatility ka kya matlab hai]
**Price Action:** [candle patterns jo dikh rahe hain]

## PROBABILITY ASSESSMENT
**Bull Probability: {prob.get('bull_pct')}%**
[kyon bull ya bear probability zyada hai — top 3 reasons]

## {mtype.upper()} TRADING PLAN
**Action:** [{'BUY / SELL / HOLD / WAIT' if mtype == 'spot' else 'LONG / SHORT / WAIT'}]
**Entry Zone:** ${price * 0.98:.4f} – ${price * 1.01:.4f} (ya specific levels suggest karo)
**Target 1:** $[specific price] ([X]% gain)
**Target 2:** $[specific price] ([X]% gain)
**Stop Loss:** $[specific price] ([X]% loss)
**Risk:Reward Ratio:** 1:[number]
{f'**Max Safe Leverage:** [X]x' + chr(10) + f'**Liquidation at Leverage:** $[price]' if mtype == 'futures' else '**Recommended Hold:** [timeframe]'}
**Position Size:** Capital ka [X]% is trade mein lagao
**Risk Level:** [LOW / MEDIUM / HIGH]

## KEY SIGNALS SUMMARY
- [Most important bull/bear signal]
- [Second signal]
- [Third signal]
- [Fourth signal]
- [Fifth signal]

## FINAL VERDICT
[3-4 lines mein honest Hinglish advice — kya karna chahiye aur kyun]"""

    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text

# ─── RENDER ANALYSIS ─────────────────────────────────────────────────────────
def render_analysis(text: str, mtype: str):
    lines = text.split("\n")
    html_parts = ['<div class="analysis-box">']
    for line in lines:
        line = line.strip()
        if not line:
            html_parts.append("<br>")
            continue
        if line.startswith("## "):
            html_parts.append(f'<div class="analysis-section">{line[3:]}</div>')
        elif "**Action:**" in line or "**Direction:**" in line:
            is_buy = any(w in line.upper() for w in ["BUY", "LONG"])
            is_sell = any(w in line.upper() for w in ["SELL", "SHORT"])
            css = "analysis-action-buy" if is_buy else "analysis-action-sell" if is_sell else ""
            clean = line.replace("**", "")
            if css:
                html_parts.append(f'<div class="{css}">{clean}</div>')
            else:
                html_parts.append(f'<div style="color:#ffb400;font-weight:700;font-size:15px;margin:6px 0">{clean}</div>')
        elif line.startswith("**") and ":**" in line:
            idx = line.index(":**")
            key = line[2:idx]
            val = line[idx + 3:].strip().replace("**", "")
            html_parts.append(f'<div style="margin:4px 0"><span style="color:#00c8ff;font-weight:700">{key}:</span> <span style="color:#c0d8ec">{val}</span></div>')
        elif line.startswith("- "):
            html_parts.append(f'<div style="margin:3px 0;padding-left:12px;color:#9ab8cc">› {line[2:]}</div>')
        elif line.startswith("**Bull Probability"):
            html_parts.append(f'<div style="color:#00dc64;font-weight:800;font-size:15px;margin:8px 0">{line.replace("**","")}</div>')
        else:
            html_parts.append(f'<div style="margin:2px 0;color:#a8c0d4">{line}</div>')

    html_parts.append('<div class="disclaimer-box">⚠️ Yeh sirf AI-generated analysis hai — financial advice nahi hai. DYOR (Do Your Own Research) zaroor karo. Crypto trading mein aapka poora capital risk par hota hai. Sirf wo paisa lagao jo dub jaye toh zindagi na rukay.</div>')
    html_parts.append("</div>")
    st.markdown("\n".join(html_parts), unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-title">◆ CRYPTO ANALYZER PRO</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<div class="section-title">◆ API KEY</div>', unsafe_allow_html=True)
    api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...",
                            help="claude.ai se API key lo")

    st.markdown("---")
    st.markdown('<div class="section-title">◆ COIN SELECT</div>', unsafe_allow_html=True)

    selected_label = st.selectbox("Popular Coins", options=list(POPULAR_COINS.keys()), index=0)
    selected_id = POPULAR_COINS[selected_label]

    custom_id = st.text_input("Ya Custom CoinGecko ID", placeholder="e.g. notcoin, floki, wen",
                              help="CoinGecko pe jaake coin ka ID dhundho")
    coin_id = custom_id.strip().lower() if custom_id.strip() else selected_id

    st.markdown("---")
    st.markdown('<div class="section-title">◆ MARKET TYPE</div>', unsafe_allow_html=True)
    mtype = st.radio("", ["spot", "futures"], format_func=lambda x: "💚 SPOT TRADING" if x == "spot" else "🔮 FUTURES TRADING")

    if mtype == "futures":
        st.warning("⚠️ Futures mein high risk hota hai. Beginners max 3–5x leverage use karein.")

    st.markdown("---")
    st.markdown('<div class="section-title">◆ CHART SETTINGS</div>', unsafe_allow_html=True)
    chart_days = st.slider("Chart Days", min_value=7, max_value=90, value=30, step=7)

    st.markdown("---")
    load_btn = st.button("◆ LOAD & ANALYZE", use_container_width=True)
    analyze_btn = st.button("🤖 GET AI ANALYSIS", use_container_width=True)

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:10px 0 20px">
  <div style="font-family:'Share Tech Mono',monospace; font-size:28px; font-weight:700;
       background:linear-gradient(135deg,#00c8ff,#00ff88); -webkit-background-clip:text;
       -webkit-text-fill-color:transparent; letter-spacing:4px">
    CRYPTO ANALYZER PRO
  </div>
  <div style="font-size:10px; color:#1a5a7a; letter-spacing:5px; margin-top:4px">
    TECHNICAL • FUNDAMENTAL • AI ANALYSIS • PROBABILITY
  </div>
</div>
""", unsafe_allow_html=True)

# Load data on button or on start
if "coin_data" not in st.session_state:
    st.session_state.coin_data = None
    st.session_state.df_ohlc = pd.DataFrame()
    st.session_state.df_chart = pd.DataFrame()
    st.session_state.indicators = {}
    st.session_state.probability = {}
    st.session_state.analysis_text = ""
    st.session_state.loaded_coin = ""

if load_btn or (st.session_state.loaded_coin != coin_id and st.session_state.coin_data is None):
    with st.spinner(f"◆ {coin_id.upper()} ka data load ho raha hai..."):
        try:
            st.cache_data.clear()
            coin_info = fetch_coin_info(coin_id)
            df_ohlc = fetch_ohlc(coin_id, chart_days)
            df_chart = fetch_market_chart(coin_id, chart_days)

            closes = df_ohlc["close"] if not df_ohlc.empty else pd.Series([])
            rsi_val = calc_rsi(closes) if len(closes) > 16 else None
            macd_line, macd_sig, macd_hist = calc_macd(closes) if len(closes) > 26 else (None, None, None)
            bb_u, bb_m, bb_l = calc_bollinger(closes) if len(closes) > 20 else (pd.Series([]), pd.Series([]), pd.Series([]))
            stoch_k_s, stoch_d_s = calc_stochastic(df_ohlc) if not df_ohlc.empty else (pd.Series([]), pd.Series([]))
            ma50 = closes.rolling(50).mean().iloc[-1] if len(closes) >= 50 else None
            ma200 = closes.rolling(200).mean().iloc[-1] if len(closes) >= 200 else None
            support, resistance = calc_support_resistance(df_ohlc)
            atr_val = calc_atr(df_ohlc) if not df_ohlc.empty else None
            vol_data = calc_volatility(closes) if len(closes) > 5 else {}
            vol_analysis = calc_volume_analysis(df_chart, df_ohlc)
            patterns = detect_price_action(df_ohlc) if len(df_ohlc) >= 3 else []

            price = coin_info.get("market_data", {}).get("current_price", {}).get("usd", 0)
            bb_signal = ("overbought" if price > bb_u.iloc[-1] else "oversold" if price < bb_l.iloc[-1] else "normal") if len(bb_u) > 0 and not pd.isna(bb_u.iloc[-1]) else "normal"

            # trend
            if len(closes) >= 10:
                r = closes.tail(5).mean()
                o = closes.iloc[-10:-5].mean()
                pct = (r - o) / o * 100
                trend = "up" if pct > 2 else "down" if pct < -2 else "sideways"
                trend_label = "Uptrend 📈" if trend == "up" else "Downtrend 📉" if trend == "down" else "Sideways ↔️"
            else:
                trend = "sideways"; trend_label = "Unknown"

            indicators = {
                "rsi": rsi_val,
                "macd_bullish": (macd_line.iloc[-1] > macd_sig.iloc[-1]) if macd_line is not None and len(macd_line) > 0 else None,
                "macd_line": macd_line.iloc[-1] if macd_line is not None and len(macd_line) > 0 else None,
                "stoch_k": stoch_k_s.iloc[-1] if len(stoch_k_s) > 0 else None,
                "stoch_d": stoch_d_s.iloc[-1] if len(stoch_d_s) > 0 else None,
                "ma50": ma50, "ma200": ma200,
                "bb_upper": bb_u.iloc[-1] if len(bb_u) > 0 and not pd.isna(bb_u.iloc[-1]) else None,
                "bb_mid": bb_m.iloc[-1] if len(bb_m) > 0 and not pd.isna(bb_m.iloc[-1]) else None,
                "bb_lower": bb_l.iloc[-1] if len(bb_l) > 0 and not pd.isna(bb_l.iloc[-1]) else None,
                "bb_signal": bb_signal,
                "support": support, "resistance": resistance,
                "atr": atr_val,
                "volatility": vol_data, "volume": vol_analysis, "patterns": patterns,
                "trend": trend, "trend_label": trend_label,
                "price": price,
                "change_24h": coin_info.get("market_data", {}).get("price_change_percentage_24h"),
                "volume_ratio": vol_analysis.get("ratio"),
            }

            fib_levels = calc_fibonacci(resistance or price * 1.1, support or price * 0.9) if resistance and support else {}
            prob = calc_probability(indicators)

            st.session_state.coin_data = coin_info
            st.session_state.df_ohlc = df_ohlc
            st.session_state.df_chart = df_chart
            st.session_state.indicators = indicators
            st.session_state.fib_levels = fib_levels
            st.session_state.probability = prob
            st.session_state.loaded_coin = coin_id
            st.session_state.analysis_text = ""
            st.success(f"✅ {coin_info.get('name')} data loaded!")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ─── DISPLAY DATA ─────────────────────────────────────────────────────────────
if st.session_state.coin_data:
    cd = st.session_state.coin_data
    ind = st.session_state.indicators
    prob = st.session_state.probability
    df_ohlc = st.session_state.df_ohlc
    df_chart = st.session_state.df_chart
    md = cd.get("market_data", {})
    sym = cd.get("symbol", "").upper()
    name = cd.get("name", "")
    price = md.get("current_price", {}).get("usd", 0)
    ch24 = md.get("price_change_percentage_24h")
    isup = (ch24 or 0) >= 0

    # ── PRICE HEADER ──
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric(sym, fmt_price(price), fmt_pct(ch24))
    with col2:
        st.metric("7d Change", fmt_pct(md.get("price_change_percentage_7d")))
    with col3:
        st.metric("30d Change", fmt_pct(md.get("price_change_percentage_30d")))
    with col4:
        st.metric("Market Cap", fmt_large(md.get("market_cap", {}).get("usd")))
    with col5:
        st.metric("Volume 24h", fmt_large(md.get("total_volume", {}).get("usd")))
    with col6:
        st.metric("From ATH", fmt_pct(md.get("ath_change_percentage", {}).get("usd")))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── MAIN TABS ──
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊  CHART", "🎯  INDICATORS", "📈  PROBABILITY", "🔍  PRICE ACTION", "🤖  AI ANALYSIS"
    ])

    # ── TAB 1: CHART ──
    with tab1:
        fig = build_main_chart(df_ohlc, df_chart, sym)
        if fig:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.warning("Chart data available nahi hai.")

    # ── TAB 2: INDICATORS ──
    with tab2:
        st.markdown('<div class="section-title">◆ MOMENTUM INDICATORS</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        rsi = ind.get("rsi")
        with c1:
            rsi_status = "🔴 OVERBOUGHT" if rsi and rsi > 70 else "🟢 OVERSOLD" if rsi and rsi < 30 else "🟡 NEUTRAL"
            st.metric("RSI (14)", f"{rsi:.1f}" if rsi else "—", rsi_status)
        sk = ind.get("stoch_k")
        with c2:
            sk_status = "🔴 OVERBOUGHT" if sk and sk > 80 else "🟢 OVERSOLD" if sk and sk < 20 else "🟡 NEUTRAL"
            st.metric("Stochastic %K", f"{sk:.1f}" if sk else "—", sk_status)
        with c3:
            macd_s = "🟢 BULLISH" if ind.get("macd_bullish") else "🔴 BEARISH"
            st.metric("MACD Signal", macd_s, "Above signal" if ind.get("macd_bullish") else "Below signal")
        with c4:
            atr = ind.get("atr")
            st.metric("ATR (Volatility)", fmt_price(atr), ind.get("volatility", {}).get("level", "—"))

        st.markdown("---")
        st.markdown('<div class="section-title">◆ MOVING AVERAGES & BOLLINGER</div>', unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            ma50 = ind.get("ma50")
            diff = ((price - ma50) / ma50 * 100) if ma50 else None
            st.metric("MA 50", fmt_price(ma50), f"{'▲' if diff and diff > 0 else '▼'} {abs(diff):.1f}%" if diff else "—")
        with c2:
            ma200 = ind.get("ma200")
            diff200 = ((price - ma200) / ma200 * 100) if ma200 else None
            st.metric("MA 200", fmt_price(ma200), f"{'▲' if diff200 and diff200 > 0 else '▼'} {abs(diff200):.1f}%" if diff200 else "—")
        with c3:
            st.metric("BB Upper", fmt_price(ind.get("bb_upper")), "Resistance zone")
        with c4:
            st.metric("BB Middle", fmt_price(ind.get("bb_mid")), "Fair value")
        with c5:
            st.metric("BB Lower", fmt_price(ind.get("bb_lower")), "Support zone")

        st.markdown("---")
        st.markdown('<div class="section-title">◆ SUPPORT, RESISTANCE & FIBONACCI</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Support (20d Low)", fmt_price(ind.get("support")), "Strong buy zone 🟢")
        with c2:
            st.metric("Resistance (20d High)", fmt_price(ind.get("resistance")), "Strong sell zone 🔴")

        fib = st.session_state.get("fib_levels", {})
        if fib:
            st.markdown('<div class="section-title" style="margin-top:14px">◆ FIBONACCI RETRACEMENT LEVELS</div>', unsafe_allow_html=True)
            fc = st.columns(5)
            for i, (level, val) in enumerate(fib.items()):
                with fc[i]:
                    diff_fib = ((price - val) / val * 100) if val else None
                    st.metric(f"Fib {level}", fmt_price(val), f"{'+' if diff_fib and diff_fib > 0 else ''}{diff_fib:.1f}%" if diff_fib else "—")

        st.markdown("---")
        st.markdown('<div class="section-title">◆ VOLUME ANALYSIS</div>', unsafe_allow_html=True)
        vol = ind.get("volume", {})
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Volume Trend", vol.get("trend", "—"))
        with c2:
            st.metric("vs 3d Avg", f"×{vol.get('ratio', '—')}", "Recent vs older")
        with c3:
            st.metric("vs All-time Avg", f"{vol.get('vs_avg', '—')}%")
        with c4:
            st.metric("Volume Signal", vol.get("signal", "—"))

        st.markdown("---")
        st.markdown('<div class="section-title">◆ VOLATILITY (DAILY RETURNS)</div>', unsafe_allow_html=True)
        if not df_ohlc.empty:
            st.plotly_chart(build_volatility_chart(df_ohlc["close"]), use_container_width=True,
                           config={"displayModeBar": False})
        v = ind.get("volatility", {})
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Daily Volatility", f"{v.get('daily_pct', '—')}%")
        with c2:
            st.metric("Annual Volatility", f"{v.get('annual_pct', '—')}%")
        with c3:
            st.metric("Volatility Level", v.get("level", "—"))

    # ── TAB 3: PROBABILITY ──
    with tab3:
        st.markdown('<div class="section-title">◆ BULL / BEAR PROBABILITY</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 2])
        with c1:
            st.plotly_chart(build_probability_gauge(prob.get("bull_pct", 50)),
                           use_container_width=True, config={"displayModeBar": False})

            bull_pct = prob.get("bull_pct", 50)
            if bull_pct >= 62:
                sig_html = f'<div class="signal-box signal-bull">🟢 BULLISH SIGNAL<br><span style="font-size:13px;opacity:.8">{bull_pct}% Bull Probability</span></div>'
            elif bull_pct <= 38:
                sig_html = f'<div class="signal-box signal-bear">🔴 BEARISH SIGNAL<br><span style="font-size:13px;opacity:.8">{100 - bull_pct}% Bear Probability</span></div>'
            else:
                sig_html = f'<div class="signal-box signal-neutral">🟡 NEUTRAL SIGNAL<br><span style="font-size:13px;opacity:.8">{bull_pct}% Bull / {100 - bull_pct}% Bear</span></div>'
            st.markdown(sig_html, unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="section-title">◆ ACTIVE SIGNALS</div>', unsafe_allow_html=True)
            signals = prob.get("signals", [])
            bull_sigs = [(n, d) for n, t, d in signals if t == "bull"]
            bear_sigs = [(n, d) for n, t, d in signals if t == "bear"]

            sc1, sc2 = st.columns(2)
            with sc1:
                st.markdown(f'<div style="color:#00dc64;font-weight:700;font-size:11px;letter-spacing:2px;margin-bottom:8px">🟢 BULL SIGNALS ({len(bull_sigs)})</div>', unsafe_allow_html=True)
                for name_s, desc in bull_sigs:
                    st.markdown(f'<div style="background:rgba(0,220,100,.08);border:1px solid rgba(0,220,100,.2);border-radius:6px;padding:6px 10px;margin:4px 0;font-size:12px"><span style="color:#00dc64;font-weight:600">{name_s}</span><br><span style="color:#3a7a5a;font-size:10px">{desc}</span></div>', unsafe_allow_html=True)
            with sc2:
                st.markdown(f'<div style="color:#ff3c50;font-weight:700;font-size:11px;letter-spacing:2px;margin-bottom:8px">🔴 BEAR SIGNALS ({len(bear_sigs)})</div>', unsafe_allow_html=True)
                for name_s, desc in bear_sigs:
                    st.markdown(f'<div style="background:rgba(255,60,80,.08);border:1px solid rgba(255,60,80,.2);border-radius:6px;padding:6px 10px;margin:4px 0;font-size:12px"><span style="color:#ff3c50;font-weight:600">{name_s}</span><br><span style="color:#7a3a3a;font-size:10px">{desc}</span></div>', unsafe_allow_html=True)

        # Progress bars
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">◆ SIGNAL STRENGTH</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:#00dc64;font-size:12px;margin-bottom:4px">BULL {prob.get("bull_pct")}%</div>', unsafe_allow_html=True)
        st.progress(prob.get("bull_pct", 50) / 100)
        st.markdown(f'<div style="color:#ff3c50;font-size:12px;margin-bottom:4px">BEAR {prob.get("bear_pct")}%</div>', unsafe_allow_html=True)
        st.progress(prob.get("bear_pct", 50) / 100)

    # ── TAB 4: PRICE ACTION ──
    with tab4:
        st.markdown('<div class="section-title">◆ CANDLESTICK PATTERN DETECTION</div>', unsafe_allow_html=True)
        patterns = ind.get("patterns", [])
        if patterns:
            for pname, ptype, pdesc in patterns:
                color = "#00dc64" if ptype == "bullish" else "#ff3c50" if ptype == "bearish" else "#ffb400"
                badge = "bull" if ptype == "bullish" else "bear" if ptype == "bearish" else "neutral"
                st.markdown(f"""
                <div style="background:rgba(0,20,45,.7);border:1px solid {color}33;border-radius:8px;padding:12px 16px;margin:6px 0;display:flex;align-items:center;gap:12px">
                  <span class="ind-badge {badge}">{pname}</span>
                  <span style="color:#8ab0c8;font-size:12px">{pdesc}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("Abhi koi clear candlestick pattern detect nahi hua.")

        st.markdown("---")
        st.markdown('<div class="section-title">◆ TREND ANALYSIS</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            trend_color = "#00dc64" if ind.get("trend") == "up" else "#ff3c50" if ind.get("trend") == "down" else "#ffb400"
            st.markdown(f'<div style="background:rgba(0,20,45,.7);border:1px solid {trend_color}33;border-radius:8px;padding:14px;text-align:center"><div style="font-size:9px;color:#1a5a7a;letter-spacing:2px;margin-bottom:6px">SHORT-TERM TREND</div><div style="font-size:18px;font-weight:700;color:{trend_color}">{ind.get("trend_label", "—")}</div></div>', unsafe_allow_html=True)
        with c2:
            ma_sig = "🟢 BULLISH" if (ind.get("ma50") and price > ind.get("ma50", 0)) else "🔴 BEARISH"
            st.markdown(f'<div style="background:rgba(0,20,45,.7);border:1px solid rgba(0,120,180,.25);border-radius:8px;padding:14px;text-align:center"><div style="font-size:9px;color:#1a5a7a;letter-spacing:2px;margin-bottom:6px">MA50 SIGNAL</div><div style="font-size:18px;font-weight:700;color:{"#00dc64" if "BULL" in ma_sig else "#ff3c50"}">{ma_sig}</div></div>', unsafe_allow_html=True)
        with c3:
            ma200_sig = "🟢 BULL MARKET" if (ind.get("ma200") and price > ind.get("ma200", 0)) else "🔴 BEAR MARKET"
            st.markdown(f'<div style="background:rgba(0,20,45,.7);border:1px solid rgba(0,120,180,.25);border-radius:8px;padding:14px;text-align:center"><div style="font-size:9px;color:#1a5a7a;letter-spacing:2px;margin-bottom:6px">MA200 SIGNAL</div><div style="font-size:18px;font-weight:700;color:{"#00dc64" if "BULL" in ma200_sig else "#ff3c50"}">{ma200_sig}</div></div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div class="section-title">◆ PRICE LEVELS AT A GLANCE</div>', unsafe_allow_html=True)
        levels = []
        if ind.get("resistance"):
            levels.append(("Resistance (20d)", ind["resistance"], "#ff3c50", "Sell/Short zone"))
        if ind.get("bb_upper"):
            levels.append(("BB Upper", ind["bb_upper"], "#ff8c42", "Overbought zone"))
        if ind.get("ma200"):
            levels.append(("MA200", ind["ma200"], "#ff6b6b", "Major trend line"))
        if ind.get("ma50"):
            levels.append(("MA50", ind["ma50"], "#ffa500", "Medium trend line"))
        levels.append(("CURRENT PRICE", price, "#ffffff", "Now"))
        if ind.get("bb_mid"):
            levels.append(("BB Middle", ind["bb_mid"], "#00c8ff", "Fair value"))
        if ind.get("bb_lower"):
            levels.append(("BB Lower", ind["bb_lower"], "#00a8cc", "Oversold zone"))
        if ind.get("support"):
            levels.append(("Support (20d)", ind["support"], "#00dc64", "Buy/Long zone"))

        for lname, lval, lcolor, ldesc in sorted(levels, key=lambda x: x[1], reverse=True):
            is_current = lname == "CURRENT PRICE"
            border = "2px solid" if is_current else "1px solid"
            bg = "rgba(255,255,255,.07)" if is_current else "rgba(0,20,45,.7)"
            st.markdown(f"""
            <div style="background:{bg};border:{border} {lcolor}55;border-radius:7px;padding:8px 14px;margin:3px 0;display:flex;justify-content:space-between;align-items:center">
              <span style="color:{lcolor};font-size:12px;font-weight:{'800' if is_current else '500'}">{lname}</span>
              <span style="color:{lcolor};font-family:'Share Tech Mono',monospace;font-size:13px;font-weight:700">{fmt_price(lval)}</span>
              <span style="color:#2a5a7a;font-size:10px">{ldesc}</span>
            </div>""", unsafe_allow_html=True)

    # ── TAB 5: AI ANALYSIS ──
    with tab5:
        if analyze_btn or (st.session_state.analysis_text == "" and analyze_btn):
            if not api_key:
                st.error("⚠️ Sidebar mein Anthropic API key daalo pehle.")
            else:
                with st.spinner("🤖 Claude AI analysis kar raha hai — sab indicators dekh raha hai..."):
                    try:
                        text = get_ai_analysis(
                            st.session_state.coin_data,
                            st.session_state.indicators,
                            st.session_state.probability,
                            mtype, api_key
                        )
                        st.session_state.analysis_text = text
                    except Exception as e:
                        st.error(f"❌ AI Analysis error: {e}")

        if st.session_state.analysis_text:
            render_analysis(st.session_state.analysis_text, mtype)
        else:
            st.markdown("""
            <div style="text-align:center;padding:60px 20px;color:#1a4a6a">
              <div style="font-size:50px;margin-bottom:16px">🤖</div>
              <div style="font-size:14px;letter-spacing:2px;color:#2a6a8a">SIDEBAR MEIN API KEY DAALO</div>
              <div style="font-size:11px;margin-top:8px;color:#0a2a4a">Phir "🤖 GET AI ANALYSIS" button dabao</div>
              <div style="font-size:10px;margin-top:16px;color:#0a2a3a;line-height:1.7">
                App complete analysis dega:<br>
                RSI • MACD • Bollinger • Stochastic • Volume • Volatility<br>
                Price Action • Support/Resistance • Fibonacci • Probability<br>
                Entry/Exit Zones • Stop Loss • Take Profit • Risk:Reward
              </div>
            </div>
            """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center;padding:80px 20px">
      <div style="font-size:48px;margin-bottom:16px">📊</div>
      <div style="font-family:'Share Tech Mono',monospace;font-size:16px;color:#00c8ff;letter-spacing:3px">READY TO ANALYZE</div>
      <div style="font-size:12px;color:#1a5a7a;margin-top:10px">Sidebar mein coin select karo aur "LOAD & ANALYZE" dabao</div>
    </div>
    """, unsafe_allow_html=True)
