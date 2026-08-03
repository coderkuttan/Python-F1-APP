"""
app.py
──────
F1 Race Analytics Explorer — Streamlit Web Application
BCA306-5 Advanced Python | Lab Exercise P6

An interactive dashboard for exploring Formula 1 race telemetry data:
lap times, tyre strategy, sector splits, and driver comparisons.

Run locally:
    streamlit run app.py

Deploy:
    Push to GitHub → deploy via share.streamlit.io (Streamlit Community Cloud)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from auth import (
    validate_registration, validate_login,
    register_user, login_user, seed_demo_user,
)

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="F1 Race Analytics Explorer",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background-color: #0e0e14; }
h1, h2, h3 { color: #e8e8f0; }
.metric-box {
    background: #15151f; border: 1px solid #24243a; border-radius: 10px;
    padding: 14px 18px; text-align: center;
}
.metric-box .val { font-size: 1.8rem; font-weight: 700; color: #ffffff; }
.metric-box .lbl { font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }
.auth-box {
    max-width: 420px; margin: 3rem auto; background: #15151f;
    border: 1px solid #24243a; border-radius: 14px; padding: 2rem;
}
</style>
""", unsafe_allow_html=True)

seed_demo_user()

# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = {}

# ─────────────────────────────────────────────────────────────
# LOGIN / REGISTER GATE
# ─────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown("""
    <div style="text-align:center;margin-top:1rem">
        <h1 style="color:#e8002d;margin-bottom:0;">🏁 F1 Race Analytics Explorer</h1>
        <p style="color:#888;letter-spacing:1px;font-size:0.85rem;text-transform:uppercase;">
            BCA306-5 Advanced Python · Lab P6
        </p>
    </div>
    """, unsafe_allow_html=True)

    auth_choice = st.radio(
        "Choose action", ["🔑 Login", "📝 Register"],
        horizontal=True, label_visibility="collapsed"
    )

    if auth_choice == "🔑 Login":
        st.markdown('<div class="auth-box">', unsafe_allow_html=True)
        st.subheader("Welcome back")
        with st.form("login_form"):
            credential = st.text_input("Username or Email", placeholder="e.g. demo")
            password   = st.text_input("Password", type="password")
            submitted  = st.form_submit_button("Login", use_container_width=True)
        if submitted:
            result = validate_login(credential, password)
            if not result["valid"]:
                for field, msg in result["errors"].items():
                    st.error(f"**{field.replace('_',' ').title()}:** {msg}")
            else:
                ok, msg, user_data = login_user(credential, password)
                if ok:
                    st.session_state.logged_in    = True
                    st.session_state.current_user = user_data
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        st.markdown("</div>", unsafe_allow_html=True)
        st.info("💡 Demo credentials: **demo** / **Demo@1234**")

    else:  # Register
        st.markdown('<div class="auth-box">', unsafe_allow_html=True)
        st.subheader("Create an account")
        with st.form("register_form"):
            full_name = st.text_input("Full Name", placeholder="e.g. Lewis Hamilton")
            username  = st.text_input("Username", placeholder="3–20 chars, start with a letter")
            email     = st.text_input("Email", placeholder="e.g. you@example.com")
            password  = st.text_input("Password", type="password")
            confirm   = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Create Account", use_container_width=True)
        if submitted:
            result = validate_registration(username, full_name, email, password, confirm)
            if not result["valid"]:
                for field, msg in result["errors"].items():
                    st.error(f"**{field.replace('_',' ').title()}:** {msg}")
            else:
                ok, msg = register_user(username, full_name, email, password)
                if ok:
                    st.success(f"🎉 {msg} Switch to Login to continue.")
                else:
                    st.error(msg)
        st.markdown("</div>", unsafe_allow_html=True)
        with st.expander("📋 Password rules"):
            st.markdown("""
            - Minimum 8 characters
            - At least one uppercase letter
            - At least one digit
            - At least one special character (`!@#$%^&*` etc.)
            """)

    st.stop()

# ─────────────────────────────────────────────────────────────
# LOGGED-IN HEADER
# ─────────────────────────────────────────────────────────────
_user = st.session_state.current_user


TEAM_COLORS = {
    "Red Bull Racing": "#3671C6", "Scuderia Ferrari": "#E8002D",
    "McLaren": "#FF8000", "Mercedes-AMG": "#27F4D2",
    "Aston Martin": "#229971", "RB": "#6692FF",
    "Williams": "#64C4FF", "Kick Sauber": "#52E252",
}

# ─────────────────────────────────────────────────────────────
# DATA LOADING  (cached — Streamlit widget: file_uploader)
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_default_data():
    return pd.read_csv("f1_race_data.csv")

@st.cache_data
def load_uploaded(file):
    return pd.read_csv(file)

st.sidebar.title("🏎️ F1 Analytics")
st.sidebar.markdown(f"**{_user.get('full_name','User')}**  \n<small>{_user.get('email','')}</small>", unsafe_allow_html=True)
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.current_user = {}
    st.rerun()
st.sidebar.markdown("---")

# Widget 1: File uploader
uploaded_file = st.sidebar.file_uploader(
    "Upload your own race CSV", type=["csv"],
    help="Must contain columns: race, driver, team, lap, lap_time_sec, tyre_compound, pit_stop, position"
)

if uploaded_file is not None:
    df = load_uploaded(uploaded_file)
    st.sidebar.success(f"✓ Loaded {len(df):,} rows from your file")
else:
    df = load_default_data()
    st.sidebar.info(f"Using sample dataset ({len(df):,} rows)")

st.sidebar.markdown("---")

# ─────────────────────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────────────────────
st.sidebar.subheader("Filters")

# Widget 2: Selectbox — race selection
race_list = sorted(df["race"].unique())
selected_race = st.sidebar.selectbox("Select Race", race_list, index=0)

race_df = df[df["race"] == selected_race]

# Widget 3: Multiselect — driver comparison
driver_list = sorted(race_df["driver"].unique())
default_drivers = driver_list[:3] if len(driver_list) >= 3 else driver_list
selected_drivers = st.sidebar.multiselect(
    "Compare Drivers", driver_list, default=default_drivers
)

# Widget 4: Slider — lap range
min_lap, max_lap = int(race_df["lap"].min()), int(race_df["lap"].max())
lap_range = st.sidebar.slider(
    "Lap Range", min_lap, max_lap, (min_lap, max_lap)
)

# Widget 5: Radio — chart style
chart_style = st.sidebar.radio(
    "Chart Style", ["Line", "Scatter", "Area"], horizontal=True
)

# Widget 6: Checkbox — show raw data
show_raw = st.sidebar.checkbox("Show raw data table", value=False)

# Widget 7: Selectbox — tyre filter
tyre_options = ["All"] + sorted(race_df["tyre_compound"].unique().tolist())
tyre_filter = st.sidebar.selectbox("Filter by Tyre Compound", tyre_options)

st.sidebar.markdown("---")
st.sidebar.caption("BCA306-5 Advanced Python · Lab P6")

# ─────────────────────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────────────────────
filtered = race_df[
    (race_df["driver"].isin(selected_drivers)) &
    (race_df["lap"].between(lap_range[0], lap_range[1]))
]
if tyre_filter != "All":
    filtered = filtered[filtered["tyre_compound"] == tyre_filter]

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
st.title("🏁 F1 Race Analytics Explorer")
st.markdown(f"**{selected_race}** · Lap {lap_range[0]}–{lap_range[1]} · {len(selected_drivers)} driver(s) selected")

if not selected_drivers:
    st.warning("👈 Select at least one driver from the sidebar to see analytics.")
    st.stop()

if filtered.empty:
    st.error("No data matches the current filter combination. Try widening the lap range or tyre filter.")
    st.stop()

# ─────────────────────────────────────────────────────────────
# TOP METRICS
# ─────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

fastest_row = filtered.loc[filtered["lap_time_sec"].idxmin()]
avg_speed   = filtered["top_speed_kmh"].mean()
total_pits  = int(filtered["pit_stop"].sum())
avg_lap     = filtered["lap_time_sec"].mean()

with col1:
    st.markdown(f"""<div class="metric-box"><div class="val">{fastest_row['lap_time_sec']:.3f}s</div>
    <div class="lbl">Fastest Lap ({fastest_row['driver'].split()[-1]})</div></div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="metric-box"><div class="val">{avg_lap:.3f}s</div>
    <div class="lbl">Average Lap Time</div></div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="metric-box"><div class="val">{avg_speed:.1f}</div>
    <div class="lbl">Avg Top Speed (km/h)</div></div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class="metric-box"><div class="val">{total_pits}</div>
    <div class="lbl">Total Pit Stops</div></div>""", unsafe_allow_html=True)

st.markdown("")

# ─────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Lap Time Trace", "🏆 Standings & Pace", "🛞 Tyre Strategy", "📊 Sector Analysis"]
)

# ═══ TAB 1: LAP TIME TRACE ═══════════════════════════════════
with tab1:
    st.subheader("Lap Time Comparison")

    color_map = {
        d: TEAM_COLORS.get(filtered[filtered["driver"]==d]["team"].iloc[0], "#e8002d")
        for d in selected_drivers
    }
    chart_kwargs = dict(
        data_frame=filtered, x="lap", y="lap_time_sec", color="driver",
        color_discrete_map=color_map,
        labels={"lap": "Lap Number", "lap_time_sec": "Lap Time (s)", "driver": "Driver"},
        title=f"Lap Time Trace — {selected_race}",
    )
    if chart_style == "Line":
        fig = px.line(markers=True, **chart_kwargs)
    elif chart_style == "Scatter":
        fig = px.scatter(**chart_kwargs)
    else:  # Area
        fig = px.area(**chart_kwargs)
    fig.update_layout(
        plot_bgcolor="#15151f", paper_bgcolor="#0e0e14",
        font_color="#e8e8f0", legend_title_text="Driver",
        height=450,
    )
    fig.update_xaxes(gridcolor="#24243a")
    fig.update_yaxes(gridcolor="#24243a")
    st.plotly_chart(fig, use_container_width=True)

    # Widget 8: Slider for rolling average smoothing
    smooth_window = st.slider("Smoothing window (rolling avg laps)", 1, 10, 1)
    if smooth_window > 1:
        smoothed = filtered.copy()
        smoothed["lap_time_sec"] = smoothed.groupby("driver")["lap_time_sec"] \
            .transform(lambda s: s.rolling(smooth_window, min_periods=1).mean())
        fig2 = px.line(
            smoothed, x="lap", y="lap_time_sec", color="driver",
            title=f"Smoothed Lap Trend (window={smooth_window})",
        )
        fig2.update_layout(plot_bgcolor="#15151f", paper_bgcolor="#0e0e14", font_color="#e8e8f0", height=350)
        st.plotly_chart(fig2, use_container_width=True)

# ═══ TAB 2: STANDINGS & PACE ═════════════════════════════════
with tab2:
    st.subheader("Driver Pace Comparison")

    summary = filtered.groupby("driver").agg(
        best_lap=("lap_time_sec", "min"),
        avg_lap=("lap_time_sec", "mean"),
        worst_lap=("lap_time_sec", "max"),
        avg_position=("position", "mean"),
        pit_stops=("pit_stop", "sum"),
        top_speed=("top_speed_kmh", "max"),
    ).reset_index().sort_values("best_lap")

    c1, c2 = st.columns([1, 1])

    with c1:
        fig_bar = px.bar(
            summary, x="driver", y="best_lap", color="driver",
            title="Best Lap Time by Driver",
            labels={"best_lap": "Best Lap (s)", "driver": "Driver"},
        )
        fig_bar.update_layout(plot_bgcolor="#15151f", paper_bgcolor="#0e0e14",
                               font_color="#e8e8f0", showlegend=False, height=380)
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        fig_box = px.box(
            filtered, x="driver", y="lap_time_sec", color="driver",
            title="Lap Time Consistency (spread)",
            labels={"lap_time_sec": "Lap Time (s)", "driver": "Driver"},
        )
        fig_box.update_layout(plot_bgcolor="#15151f", paper_bgcolor="#0e0e14",
                               font_color="#e8e8f0", showlegend=False, height=380)
        st.plotly_chart(fig_box, use_container_width=True)

    st.subheader("Summary Table")
    st.dataframe(
        summary.style.format({
            "best_lap": "{:.3f}", "avg_lap": "{:.3f}", "worst_lap": "{:.3f}",
            "avg_position": "{:.1f}", "top_speed": "{:.1f}",
        }),
        use_container_width=True,
    )

# ═══ TAB 3: TYRE STRATEGY ════════════════════════════════════
with tab3:
    st.subheader("Tyre Compound Usage")

    tyre_counts = filtered.groupby(["driver", "tyre_compound"]).size().reset_index(name="laps")
    fig_tyre = px.bar(
        tyre_counts, x="driver", y="laps", color="tyre_compound",
        title="Laps on Each Tyre Compound",
        labels={"laps": "Number of Laps", "driver": "Driver", "tyre_compound": "Tyre"},
        color_discrete_map={
            "Soft": "#E8002D", "Medium": "#F5A623", "Hard": "#C8C8C8",
            "Intermediate": "#22CC6A", "Wet": "#3399FF",
        },
    )
    fig_tyre.update_layout(plot_bgcolor="#15151f", paper_bgcolor="#0e0e14",
                            font_color="#e8e8f0", height=420, barmode="stack")
    st.plotly_chart(fig_tyre, use_container_width=True)

    # Widget 9: Number input — pit stop threshold alert
    threshold = st.number_input("Highlight drivers with pit stops ≥", min_value=0, max_value=10, value=2)
    pit_summary = filtered.groupby("driver")["pit_stop"].sum().reset_index()
    flagged = pit_summary[pit_summary["pit_stop"] >= threshold]
    if not flagged.empty:
        st.warning(f"⚠ {len(flagged)} driver(s) with {threshold}+ pit stops: " +
                   ", ".join(flagged["driver"].tolist()))
    else:
        st.success(f"✓ No drivers with {threshold}+ pit stops in this selection.")

# ═══ TAB 4: SECTOR ANALYSIS ══════════════════════════════════
with tab4:
    st.subheader("Sector Time Breakdown")

    sector_avg = filtered.groupby("driver")[["sector1_sec", "sector2_sec", "sector3_sec"]].mean().reset_index()
    sector_melt = sector_avg.melt(id_vars="driver", var_name="sector", value_name="time")
    sector_melt["sector"] = sector_melt["sector"].map({
        "sector1_sec": "Sector 1", "sector2_sec": "Sector 2", "sector3_sec": "Sector 3"
    })

    fig_sector = px.bar(
        sector_melt, x="driver", y="time", color="sector", barmode="group",
        title="Average Sector Times by Driver",
        labels={"time": "Time (s)", "driver": "Driver", "sector": "Sector"},
    )
    fig_sector.update_layout(plot_bgcolor="#15151f", paper_bgcolor="#0e0e14",
                              font_color="#e8e8f0", height=420)
    st.plotly_chart(fig_sector, use_container_width=True)

    # Correlation heatmap
    st.subheader("Correlation: Lap Time vs Speed vs Position")
    corr_cols = ["lap_time_sec", "top_speed_kmh", "position", "sector1_sec", "sector2_sec", "sector3_sec"]
    corr = filtered[corr_cols].corr()
    fig_heat = px.imshow(
        corr, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r",
        title="Feature Correlation Heatmap",
    )
    fig_heat.update_layout(plot_bgcolor="#15151f", paper_bgcolor="#0e0e14", font_color="#e8e8f0", height=400)
    st.plotly_chart(fig_heat, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# RAW DATA TABLE (toggle)
# ─────────────────────────────────────────────────────────────
if show_raw:
    st.markdown("---")
    st.subheader("Raw Filtered Data")
    st.dataframe(filtered, use_container_width=True)
    csv = filtered.to_csv(index=False).encode("utf-8")
    # Widget 10: Download button
    st.download_button(
        "⬇ Download filtered data as CSV", csv,
        file_name=f"{selected_race.replace(' ','_')}_filtered.csv", mime="text/csv"
    )

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("F1 Race Analytics Explorer · Built with Streamlit · BCA306-5 Advanced Python · Lab Exercise P6")