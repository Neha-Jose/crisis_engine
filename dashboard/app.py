import streamlit as st
import pandas as pd
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
import folium
from streamlit_folium import st_folium

SUPABASE_URL = "https://ocmblkbinzezlpksnezj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9jbWJsa2Jpbnplemxwa3NuZXpqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA0MzAwMTEsImV4cCI6MjA4NjAwNjAxMX0.d43E0wvcIda-vrzr5r7ZoI-AN4Zr5J6EBzMC9nTjaFg"

# -------------------------
# Create supabase client once
# -------------------------
@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# -------------------------
# Page config + controls
# -------------------------
st.set_page_config(layout="wide")
st.title("🚨 Crisis Priority Dashboard (Optimized)")

refresh_rate = st.sidebar.slider("Auto refresh (seconds)", min_value=2, max_value=15, value=5, step=1)
max_display = st.sidebar.slider("Max alerts to display", 5, 200, 50, step=5)
manual_refresh = st.sidebar.button("🔄 Refresh Now")

# Trigger an auto-refresh (non-blocking)
# st_autorefresh returns the number of times it has run; we don't use the value.
st_autorefresh(interval=refresh_rate * 1000, key="auto_refresh")

# -------------------------
# Helper: fetch only new rows
# -------------------------
def fetch_new_rows(last_id):

    if last_id is None:
        response = (
            supabase
            .table("alerts")
            .select(
                "id,sms,urgency,severity,vulnerability,trend,reasoning,latitude,longitude,created_at"
            )
            .order("id", desc=False)
            .limit(200)
            .execute()
        )
    else:
        response = (
            supabase
            .table("alerts")
            .select(
                "id,sms,urgency,severity,vulnerability,trend,reasoning,latitude,longitude,created_at"
            )
            .gt("id", last_id)
            .order("id", desc=False)
            .execute()
        )

    # VERY IMPORTANT LINE
    if response and hasattr(response, "data"):
        return response.data
    return []


# -------------------------
# Keep state for incremental updates
# -------------------------
if "alerts_df" not in st.session_state:
    st.session_state["alerts_df"] = pd.DataFrame(columns=["id","sms","urgency","severity","vulnerability","trend","reasoning","created_at"])
    st.session_state["last_id"] = None

# Manual refresh triggers same update path
if manual_refresh:
    pass  # nothing extra needed; st_autorefresh will have re-run script

# Fetch only new rows and append
new_rows = fetch_new_rows(st.session_state["last_id"])

if new_rows:
    new_df = pd.DataFrame(new_rows)
    # ensure correct dtypes
    if "urgency" in new_df.columns:
        new_df["urgency"] = pd.to_numeric(new_df["urgency"], errors="coerce").fillna(0.0)
    st.session_state["alerts_df"] = pd.concat([st.session_state["alerts_df"], new_df], ignore_index=True)
    st.session_state["alerts_df"].drop_duplicates(subset=["id"], inplace=True)
    st.session_state["alerts_df"].sort_values("id", inplace=True)
    st.session_state["last_id"] = int(st.session_state["alerts_df"]["id"].max())

# Prepare DF to display: sort by urgency desc and limit
display_df = st.session_state["alerts_df"].copy()
if not display_df.empty:
    display_df["urgency"] = pd.to_numeric(display_df["urgency"], errors="coerce").fillna(0.0)
    display_df = display_df.sort_values("urgency", ascending=False).head(max_display)

# -------------------------
# Render UI
# -------------------------
placeholder = st.container()

with placeholder:
    if display_df.empty:
        st.info("Waiting for messages (simulator or incoming messages).")
    else:
        # Render each alert as a compact card
        for _, row in display_df.iterrows():
            urgency = float(row.get("urgency", 0.0))
            color = "#2ecc71"  # green
            if urgency > 0.75:
                color = "#e74c3c"  # red
            elif urgency > 0.5:
                color = "#f39c12"  # orange

            st.markdown(
                f"""
                <div style="border-left:6px solid {color}; padding:12px; margin-bottom:10px; background:#ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.06); border-radius:6px;">
                  <div style="display:flex; justify-content:space-between; align-items:center">
                    <div style="font-size:12px;color:#666;">
                    📍 Lat: {row.get('latitude','')} | Lng: {row.get('longitude','')}
                    </div>
                    <div style="font-size:14px; font-weight:700; color:{color};">Urgency: {urgency:.2f}</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.progress(min(urgency, 1.0))

            with st.expander("🧠 Explainable AI"):
                metrics = {
                    "Severity": float(row.get("severity", 0.0) or 0.0),
                    "Vulnerability": float(row.get("vulnerability", 0.0) or 0.0),
                    "Trend": float(row.get("trend", 0.0) or 0.0),
                }
                st.bar_chart(metrics)
                st.write(row.get("reasoning", ""))
# ---------------- MAP VIEW ----------------

geo_df = display_df.dropna(subset=["latitude", "longitude"])

if not geo_df.empty:
    st.subheader("📍 Crisis Locations")

    m = folium.Map(
        location=[geo_df.iloc[0]["latitude"], geo_df.iloc[0]["longitude"]],
        zoom_start=13
    )

    for _, r in geo_df.iterrows():
        folium.Marker(
            [r["latitude"], r["longitude"]],
            popup=f"Urgency: {round(r['urgency'],2)}<br>{r['sms']}"
        ).add_to(m)

    st_folium(m, height=400)
st.caption("Auto-refreshing. Showing most urgent alerts first.")
