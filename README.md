# Central-bank gold buying explorer

Session 3 · Part A — adapted from the course gold stock-transfer monitor.

**Question:** Which central banks are buying gold, how concentrated is that
buying, and does a country's buying follow the price?

All data in `data/` is the **synthetic sample data** shipped with the course
template, and the app labels it as sample data.

## What changed from the template
- New question and title; a sample-data banner at the top.
- Time-window control (12 / 24 / 36 months / whole record) that drives every
  KPI and the Who-is-buying charts.
- New KPI strip: net official buying, buyers vs sellers, top-3 share, price
  change in window, unreported gap.
- **Who is buying** tab: ranking bar chart, cumulative-change lines with a
  country multiselect, and a yearly concentration chart (top-3 share).
- **Country focus** tab (the extension exercise): `st.selectbox` for one
  central bank, monthly purchases (grey = selling) against the gold price,
  with summary stats, price correlation and a monthly table.
- **Reported vs estimated** tab: the IMF vs WGC gap chart kept from the original.
- Removed the ETF and Swiss-export panels and the `ingest.py` live-data code.

## Run locally
    pip install -r requirements.txt
    streamlit run app.py

## Deploy
1. Push `app.py`, `design.py`, `requirements.txt` and `data/` to the top
   level of a public GitHub repo.
2. share.streamlit.io → Create app → pick the repo/branch → main file `app.py` → Deploy.
3. Open the link in a private window to check it works without signing in.
4. Paste the URL into `P01_gold_streamlit.txt` and submit it on Canvas.
