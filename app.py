"""Central-bank gold buying explorer.

Adapted from the Session 3 Part A gold stock-transfer monitor.

Question this version answers:
    Which central banks are buying gold, how concentrated is that buying,
    and does a country's buying follow the price?

Run:  streamlit run app.py

Design contract (kept from the original):
  - solid = reported, dashed = estimated; one colour per country everywhere
  - the same event rules on every time axis
  - one bordered region (the KPI strip); whitespace does the other grouping
  - every chart caption states the question the chart answers

All data in data/ is SAMPLE (synthetic) data shipped with the course
template, and the page labels it as such.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

import design as dz

DATA = Path(__file__).parent / "data"

st.set_page_config(page_title="Central-bank gold buying explorer",
                   page_icon="🪙", layout="wide",
                   initial_sidebar_state="collapsed")

# ---------------------------------------------------------------- chrome/css --
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400;1,6..72,500&family=Archivo:wght@400;500;600&display=swap');

html, body, [class*="css"], .stMarkdown, p, li {
  font-family: 'Archivo', system-ui, sans-serif;
  font-variant-numeric: tabular-nums;
}
.stApp { background: #fbfbf8; color: #1c1c18; }
.block-container { max-width: 1180px; padding-top: 2.2rem; padding-bottom: 3rem; }
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; }

h1 { font-family: 'Newsreader', serif; font-weight: 500; letter-spacing: -.01em;
     font-size: 2.4rem; margin-bottom: 0; }
h3 { font-family: 'Newsreader', serif; font-style: italic; font-weight: 500;
     font-size: 1.35rem; margin-bottom: 0; }
.stCaption, [data-testid="stCaptionContainer"] { color: #8c8c84; }

.stTabs [data-baseweb="tab-list"] { gap: 30px; border-bottom: 1px solid #ecece5; }
.stTabs [data-baseweb="tab"] { font-size: 15px; font-weight: 500; color: #8c8c84;
  padding: 6px 0 10px; background: none; }
.stTabs [aria-selected="true"] { color: #1c1c18; }
.stTabs [data-baseweb="tab-highlight"] { background-color: #a3780a; height: 2px; }
.stTabs [data-baseweb="tab-border"] { background-color: transparent; }

.sample { background: #f4efe0; border-left: 3px solid #a3780a; color: #5a4a1a;
  font-size: 13px; padding: 8px 12px; margin: 10px 0 14px; border-radius: 2px; }

.kpis { border: 1.5px solid #1c1c18; border-radius: 3px;
  display: grid; grid-template-columns: repeat(5, 1fr); gap: 0 26px;
  padding: 14px 18px 10px; margin: 6px 0 4px; }
@media (max-width: 760px) { .kpis { grid-template-columns: repeat(2, 1fr); gap: 12px 18px; } }
.kpi .l { font-size: 11px; color: #8c8c84; line-height: 1.25; }
.kpi .v { font-size: 20px; font-weight: 600; margin-top: 1px; }
.kpi .v small { font-size: 11.5px; font-weight: 500; color: #8c8c84; margin-left: 4px; }
.kpi svg { display: block; margin-top: 4px; }

.grammar { font-size: 12.5px; color: #8c8c84; margin: 2px 0 10px; }
.grammar b { color: #1c1c18; font-weight: 500; }
.masthead { display: flex; justify-content: space-between; align-items: baseline;
  flex-wrap: wrap; gap: 6px; }
.masthead .d { color: #8c8c84; font-size: 13px; }
.stat { font-size: 13px; color: #8c8c84; }
.stat b { color: #1c1c18; font-size: 18px; font-weight: 600; display: block; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------- plotly theme --
pio.templates["ledger"] = go.layout.Template(layout=dict(
    paper_bgcolor=dz.PAPER, plot_bgcolor=dz.PAPER,
    font=dict(family="Archivo, system-ui, sans-serif", color=dz.INK, size=13),
    margin=dict(l=10, r=64, t=34, b=10), showlegend=False,
    xaxis=dict(showgrid=False, ticks="outside", tickcolor=dz.GHOST,
               linecolor=dz.GHOST),
    yaxis=dict(gridcolor="#efefe8", zeroline=False, side="right",
               tickformat=","),
    hoverlabel=dict(bgcolor=dz.PAPER, bordercolor=dz.GHOST,
                    font=dict(family="Archivo, system-ui, sans-serif",
                              color=dz.INK, size=12)),
))
pio.templates.default = "ledger"


# ------------------------------------------------------------------ loading --
@st.cache_data(ttl=3600)
def load(name: str, dates=("date",)) -> pd.DataFrame:
    return pd.read_csv(DATA / f"{name}.csv", parse_dates=list(dates))


try:
    price = load("price")
    declared = load("declared")
    gap = load("gap", dates=("quarter_end",))
except FileNotFoundError:
    st.error("No data found. Make sure the data/ folder sits next to app.py.")
    st.stop()

fmt = lambda t: pd.Timestamp(t).strftime("%b %Y")
last = declared.date.max()


# --------------------------------------------------------------- helpers -----
def events(fig, label: bool, start=None):
    for i, (d, t) in enumerate(dz.EVENTS):
        if start is not None and pd.Timestamp(d) < start:
            continue
        fig.add_vline(x=d, line_color=dz.GHOST, line_width=1)
        if label:
            fig.add_annotation(x=d, y=1.03 + 0.075 * (i % 2), yref="paper",
                               text=t, showarrow=False,
                               font=dict(size=11, color=dz.FAINT))


def endlabel(fig, x, y, text, color=dz.FAINT):
    fig.add_annotation(x=x, y=y, text=text, showarrow=False, xanchor="left",
                       xshift=8, font=dict(size=12, color=color))


def chart(fig, h):
    fig.update_layout(template="ledger", height=h,
                      paper_bgcolor=dz.PAPER, plot_bgcolor=dz.PAPER)
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    st.plotly_chart(fig, width="stretch", theme=None,
                    config={"displayModeBar": False})


def spark(vals, color, w=76, h=20):
    vals = list(vals)
    if len(vals) < 2:
        return ""
    lo, hi = min(vals), max(vals) + 1e-9
    pts = " ".join(f"{2 + (w-4)*i/(len(vals)-1):.1f},"
                   f"{h-2 - (h-4)*(v-lo)/(hi-lo):.1f}" for i, v in enumerate(vals))
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<polyline points="{pts}" fill="none" stroke="{color}" '
            f'stroke-width="1.6" stroke-linejoin="round"/></svg>')


# ----------------------------------------------------------------- masthead --
st.markdown(f"""
<div class="masthead"><h1>Central-bank gold buying explorer</h1>
<span class="d">data to {fmt(last)}</span></div>
""", unsafe_allow_html=True)
st.caption("Which central banks are buying gold, how concentrated is that "
           "buying, and does a country's buying follow the price?")
st.markdown('<div class="sample"><b>Sample data.</b> Every number on this page '
            'comes from the synthetic sample dataset supplied with the course '
            'template. It mimics the shape of IMF and World Gold Council '
            'series but is <b>not</b> real reported data.</div>',
            unsafe_allow_html=True)

# ---------------------------------------------------------------- controls --
WINDOWS = {"Last 12 months": 12, "Last 24 months": 24,
           "Last 36 months": 36, "Whole record": None}
win_label = st.radio("Time window", list(WINDOWS), index=0, horizontal=True)
months = WINDOWS[win_label]
start = (last - pd.DateOffset(months=months - 1)) if months else declared.date.min()

dw = declared[declared.date >= start]
pw = price[price.date >= start]
totals = dw.groupby("country").net_purchases_t.sum().sort_values(ascending=False)

# ------------------------------------------------------------- derived nums --
net_total = totals.sum()
buyers = int((totals > 0).sum())
sellers = int((totals < 0).sum())
gross_buy = totals[totals > 0].sum()
top3_share = totals[totals > 0].head(3).sum() / gross_buy if gross_buy else np.nan
p0, p1 = pw.price_usd_oz.iloc[0], pw.price_usd_oz.iloc[-1]
monthly_net = dw.groupby("date").net_purchases_t.sum()
gap_res = gap.wgc_estimate_t - gap.imf_reported_t

KPIS = [
    ("net official buying", f"{net_total:+,.0f} t", win_label.lower(),
     spark(monthly_net.cumsum(), dz.INK)),
    ("buyers / sellers", f"{buyers} / {sellers}", "central banks",
     ""),
    ("top-3 share of buying", f"{top3_share:.0%}",
     " + ".join(totals.head(3).index), ""),
    ("gold price, $/oz", f"{p1:,.0f}", f"{p1/p0-1:+.0%} in window",
     spark(pw.price_usd_oz, dz.GOLD)),
    ("unreported, latest qtr", f"+{gap_res.iloc[-1]:,.0f} t",
     "WGC est. minus IMF", spark(gap_res.tail(8), dz.GOLD)),
]
tiles = "".join(f'<div class="kpi"><div class="l">{l}</div>'
                f'<div class="v">{v}<small>{s}</small></div>{sp}</div>'
                for l, v, s, sp in KPIS)
st.markdown(f'<div class="kpis">{tiles}</div>', unsafe_allow_html=True)
st.markdown('<p class="grammar"><b>Solid</b> marks reported series, '
            '<b>dashed</b> marks estimates. Each country keeps one colour on '
            'every panel; grey bars are months of net selling.</p>',
            unsafe_allow_html=True)

tabW, tabC, tabG = st.tabs(["Who is buying", "Country focus",
                            "Reported vs estimated"])

# ============================================================ WHO IS BUYING ==
with tabW:
    left, right = st.columns([2, 3], gap="large")
    with left:
        st.subheader("Ranking")
        st.caption(f"Who added or removed the most gold? — net tonnes, "
                   f"{fmt(start)} to {fmt(last)}")
        s = totals.sort_values()
        f = go.Figure(go.Bar(x=s.values, y=s.index, orientation="h",
            marker_color=[dz.hue(c) if v > 0 else dz.SELL
                          for c, v in s.items()],
            text=[f"{v:+,.0f}" for v in s.values], textposition="outside",
            textfont=dict(size=11, color=dz.FAINT), cliponaxis=False,
            hovertemplate="%{y}: %{x:+,.1f} t<extra></extra>"))
        span = s.max() - min(s.min(), 0)
        f.update_xaxes(title="tonnes", showgrid=False,
                       range=[min(s.min(), 0) - .18 * span, s.max() + .12 * span])
        f.update_yaxes(side="left", gridcolor=dz.PAPER, ticksuffix="  ")
        f.update_layout(margin=dict(l=10, r=48))
        chart(f, 520)

    with right:
        st.subheader("Cumulative change")
        st.caption("Is the buying steady or does it come in bursts? — running "
                   "total from the start of the window")
        default = [c for c in list(totals.head(4).index) + [totals.index[-1]]]
        picks = st.multiselect("Countries to compare", list(totals.index),
                               default=default)
        f = go.Figure()
        for c in picks:
            d = dw[dw.country == c].sort_values("date")
            cum = d.net_purchases_t.cumsum()
            f.add_trace(go.Scatter(x=d.date, y=cum, name=c, mode="lines",
                line=dict(color=dz.hue(c), width=2.2),
                hovertemplate=f"{c}: %{{y:+,.0f}} t<extra></extra>"))
            if len(d):
                endlabel(f, d.date.iloc[-1], cum.iloc[-1],
                         f"{c} <b>{cum.iloc[-1]:+,.0f}</b>", dz.hue(c))
        f.add_hline(y=0, line_color=dz.GHOST, line_width=1)
        events(f, label=True, start=start)
        f.update_yaxes(title="tonnes")
        f.update_layout(hovermode="x unified", margin=dict(r=120))
        chart(f, 440)

    st.subheader("How concentrated is the buying?")
    st.caption("What share of all gross buying each year came from the three "
               "biggest buyers? Higher means a few banks drive the market.")
    yr = (declared.assign(year=declared.date.dt.year)
          .groupby(["year", "country"]).net_purchases_t.sum().reset_index())
    rows = []
    for y, g in yr.groupby("year"):
        b = g[g.net_purchases_t > 0].sort_values("net_purchases_t",
                                                 ascending=False)
        rows.append(dict(year=y, share=b.net_purchases_t.head(3).sum()
                         / b.net_purchases_t.sum(),
                         who=", ".join(b.country.head(3))))
    conc = pd.DataFrame(rows)
    partial = last.month < 12
    labels = [f"{y}{' (to ' + last.strftime('%b') + ')' if partial and y == last.year else ''}"
              for y in conc.year]
    f = go.Figure(go.Bar(x=labels, y=conc.share, marker_color=dz.INK,
        opacity=.85, text=[f"{v:.0%}" for v in conc.share],
        textposition="outside", textfont=dict(size=12, color=dz.FAINT),
        customdata=conc.who, cliponaxis=False,
        hovertemplate="%{x}: %{y:.0%}<br>top 3: %{customdata}<extra></extra>"))
    f.update_xaxes(type="category")
    f.update_yaxes(tickformat=".0%", range=[0, 1])
    chart(f, 300)

# ============================================================ COUNTRY FOCUS ==
with tabC:
    st.subheader("One central bank, month by month")
    st.caption("Does this bank buy when the price rises, or buy the dips? — "
               "monthly reported purchases against the gold price")
    countries = list(totals.index)
    c = st.selectbox("Choose a central bank", countries,
                     index=countries.index("China") if "China" in countries else 0)
    d = dw[dw.country == c].sort_values("date").merge(
        pw[["date", "price_usd_oz"]], on="date", how="left")
    d["price_chg"] = d.price_usd_oz.pct_change()

    total_c = d.net_purchases_t.sum()
    buy_m = int((d.net_purchases_t > 0).sum())
    corr = d.net_purchases_t.corr(d.price_chg)
    corr_lag = d.net_purchases_t.corr(d.price_chg.shift(1))
    share = total_c / gross_buy if total_c > 0 and gross_buy else np.nan

    a, b, cc, e = st.columns(4)
    a.markdown(f'<div class="stat"><b>{total_c:+,.1f} t</b>net change, '
               f'{win_label.lower()}</div>', unsafe_allow_html=True)
    b.markdown(f'<div class="stat"><b>{buy_m} of {len(d)}</b>months of net '
               f'buying</div>', unsafe_allow_html=True)
    cc.markdown(f'<div class="stat"><b>{share:.0%}</b>of all gross buying'
                f'</div>' if not np.isnan(share) else
                '<div class="stat"><b>—</b>net seller in window</div>',
                unsafe_allow_html=True)
    e.markdown(f'<div class="stat"><b>{corr:+.2f}</b>correlation with same-'
               f'month price change</div>', unsafe_allow_html=True)

    f = go.Figure()
    f.add_trace(go.Bar(x=d.date, y=d.net_purchases_t, name="net purchases",
        marker_color=[dz.hue(c) if v > 0 else dz.SELL
                      for v in d.net_purchases_t],
        hovertemplate="%{x|%b %Y}: %{y:+.1f} t<extra></extra>"))
    f.add_trace(go.Scatter(x=d.date, y=d.price_usd_oz, name="gold price",
        mode="lines", yaxis="y2", line=dict(color=dz.GOLD, width=2.2),
        hovertemplate="%{x|%b %Y}: $%{y:,.0f}/oz<extra></extra>"))
    events(f, label=True, start=start)
    f.update_layout(
        yaxis=dict(title="tonnes / month", side="left"),
        yaxis2=dict(title="$/oz", overlaying="y", side="right",
                    showgrid=False, tickformat=",.0f"),
        margin=dict(l=10, r=10), hovermode="x unified")
    chart(f, 420)

    def describe(r):
        if np.isnan(r):
            return "not enough data to say"
        if abs(r) < 0.2:
            return "little link"
        return "buys more when the price rises" if r > 0 else "buys more when the price falls"

    st.caption(f"Bars: {c}'s monthly net purchases (coloured "
               f"for buying, grey for selling). Gold line: monthly average "
               f"price, right axis. Same-month correlation {corr:+.2f} "
               f"({describe(corr)}); price change one month earlier "
               f"{corr_lag:+.2f} ({describe(corr_lag)}). Correlation on sample "
               f"data says nothing about real policy.")

    with st.expander("Monthly table"):
        st.dataframe(
            d[["date", "net_purchases_t", "price_usd_oz"]]
            .rename(columns={"date": "month", "net_purchases_t": "net t",
                             "price_usd_oz": "price $/oz"})
            .assign(month=lambda x: x.month.dt.strftime("%Y-%m"))
            .iloc[::-1],
            hide_index=True, width="stretch")

# ===================================================== REPORTED VS ESTIMATED ==
with tabG:
    st.subheader("The gap")
    st.caption(f"How much official buying goes unreported each quarter? — "
               f"to {gap.quarter_end.iloc[-1].to_period('Q')}")
    f = go.Figure()
    f.add_trace(go.Scatter(x=gap.quarter_end, y=gap.imf_reported_t,
        mode="lines", line=dict(width=0), hoverinfo="skip"))
    f.add_trace(go.Scatter(x=gap.quarter_end, y=gap.wgc_estimate_t,
        name="WGC estimate", mode="lines",
        line=dict(color=dz.INK, width=1.6, dash=dz.DASH),
        fill="tonexty", fillcolor="rgba(163,120,10,.16)",
        hovertemplate="WGC estimate: %{y:,.0f} t<extra></extra>"))
    f.add_trace(go.Bar(x=gap.quarter_end, y=gap.imf_reported_t,
        name="reported to IMF", marker_color=dz.INK, opacity=.85,
        hovertemplate="reported: %{y:,.0f} t<extra></extra>"))
    events(f, label=True)
    endlabel(f, gap.quarter_end.iloc[-1], gap.wgc_estimate_t.iloc[-1],
             f"WGC <b>{gap.wgc_estimate_t.iloc[-1]:,.0f}</b> t")
    endlabel(f, gap.quarter_end.iloc[-1], gap.imf_reported_t.iloc[-1],
             f"IMF <b>{gap.imf_reported_t.iloc[-1]:,.0f}</b> t")
    f.update_yaxes(title="tonnes / quarter")
    f.update_layout(hovermode="x unified")
    chart(f, 430)
    share_unrep = gap_res.sum() / gap.wgc_estimate_t.sum()
    st.caption(f"Bars: purchases reported to the IMF. Dashed: World Gold "
               f"Council estimate of actual official demand. Shaded: the "
               f"unreported residual — {share_unrep:.0%} of estimated demand "
               f"across the record. The country rankings in the other tabs "
               f"only see the reported part.")

st.caption("Sample data shaped after: IMF International Financial Statistics "
           "(declared reserves), World Gold Council Gold Demand Trends "
           "(estimates), COMEX gold futures (price). Event rules: Feb 22 "
           "reserve freeze, Jun 22 G7 import ban, Jun 25 Iran war, Nov 25 CBR "
           "sales begin, May 26 escalation. Adapted from the DVN 36104 "
           "Session 3 gold dashboard.")
