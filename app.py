import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(page_title="CZ-NoN Engagement Matrix", layout="wide")

# 2026 Industry Benchmarks
BENCHMARKS = {
    'substack_open_rate': 0.44,
    'bs_growth_target': 75,
    'ctr_target': 0.032,
}

# 2. Custom Styling
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.8rem; color: #1E3A8A; }
    .stMetric { background-color: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; }
    .benchmark-text { font-size: 0.8rem; color: #64748b; margin-top: -10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Processing
@st.cache_data
def load_and_clean_data():
    # Make sure your CSV filename matches exactly!
    df_raw = pd.read_csv('CZ NoN Metrics - Sheet1.csv')
    results = []
    
    # Block 1: 2025 Data
    cols_25 = [c for c in df_raw.columns if '2025' in str(c)]
    current_platform = None
    for idx in range(1, 9):
        row = df_raw.iloc[idx]
        label = str(row.iloc[0]).strip()
        if label in ['Bluesky', 'Substack', 'Bitly']: current_platform = label; continue
        if label == 'nan' or not label: continue
        for col in cols_25:
            val = row[col]
            if pd.notna(val):
                results.append({'Date': col, 'Platform': current_platform, 'Metric': label, 'Value': float(str(val).replace(',', ''))})
    
    # Block 2: 2026 Data
    cols_26 = [str(c) for c in df_raw.iloc[9].values[1:] if str(c) != 'nan']
    for idx in range(11, len(df_raw)):
        row = df_raw.iloc[idx]
        label = str(row.iloc[0]).strip()
        if label in ['Bluesky', 'Substack', 'Bitly']: current_platform = label; continue
        if label == 'nan' or not label: continue
        for i, date_label in enumerate(cols_26):
            val = row.iloc[i+1]
            if pd.notna(val):
                results.append({'Date': date_label, 'Platform': current_platform, 'Metric': label, 'Value': float(str(val).replace(',', ''))})
    
    df = pd.DataFrame(results)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y %m')
    return df

# Initialize Data
try:
    df_f = load_and_clean_data()
    WEIGHTS = {'monthly reads': 1, 'total clicks': 2, 'total views': 0.1}
    df_f['Points'] = df_f.apply(lambda r: r['Value'] * WEIGHTS.get(r['Metric'], 0), axis=1)
except Exception as e:
    st.error(f"Data Loading Error: {e}")
    st.stop()

# 4. KPI Header
st.title("🛰️ CZ-NoN engagement matrix")
st.caption("Performance vs. 2026 SciComm Industry Benchmarks")

k1, k2, k3, k4 = st.columns(4)

# Bluesky KPI
bs_f = df_f[df_f['Metric'] == 'followers']
if not bs_f.empty:
    curr_bs = bs_f['Value'].iloc[-1]
    prev_bs = bs_f['Value'].iloc[-2] if len(bs_f) > 1 else curr_bs
    k1.metric("Bluesky Followers", f"{curr_bs:,.0f}", f"{curr_bs - prev_bs:+.0f} mo/mo")
else:
    k1.metric("Bluesky Followers", "N/A")
st.markdown("<p class='benchmark-text'>Target: +50-100/mo</p>", unsafe_allow_html=True)

# Substack KPI
total_reads = df_f[df_f['Metric'] == 'monthly reads']['Value'].sum()
k2.metric("Substack Total Reads", f"{total_reads:,.0f}")
st.markdown("<p class='benchmark-text'>Avg Open Rate Benchmark: 44%</p>", unsafe_allow_html=True)

# Clicks/CTR KPI
total_clicks = df_f[df_f['Metric'] == 'total clicks']['Value'].sum()
total_views = df_f[df_f['Metric'] == 'total views']['Value'].sum()
ctr = (total_clicks / total_views) * 100 if total_views > 0 else 0
k3.metric("Bitly Clicks", f"{total_clicks:,.0f}", f"{ctr:.1f}% CTR")
st.markdown("<p class='benchmark-text'>SciComm CTR Target: 3.2%</p>", unsafe_allow_html=True)

# Avg Engagement KPI
avg_pts = df_f.groupby('Date')['Points'].sum().mean()
k4.metric("Avg Monthly Engagement", f"{avg_pts:.1f} pts")
st.markdown("<p class='benchmark-text'>Weighted by Reach & Action</p>", unsafe_allow_html=True)

st.markdown("---")

# 5. Trend Graph
st.header("📈 Weighted Engagement Trend")
agg_trend = df_f.groupby('Date')['Points'].sum().reset_index()

if not agg_trend.empty:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=agg_trend['Date'], 
        y=agg_trend['Points'],
        mode='lines+markers',
        name='Engagement Points',
        line=dict(color='#1E3A8A', width=4),
        marker=dict(
            size=12, 
            color='#1E3A8A',
            line=dict(color='white', width=2)
        ),
        hovertemplate="<b>%{x|%B %Y}</b><br>Score: %{y:.1f} pts<extra></extra>"
    ))

    # Baseline Logic
    baseline_df = agg_trend[agg_trend['Date'].dt.year == 2025]
    if not baseline_df.empty:
        baseline = baseline_df['Points'].mean()
        fig.add_hline(y=baseline, line_dash="dot", line_color="#94a3b8", 
                      annotation_text="2025 Average Baseline", annotation_position="bottom right")

    fig.update_layout(
        plot_bgcolor='white',
        hovermode="x unified",
        xaxis=dict(showgrid=False),
        yaxis=dict(title="Engagement Points", gridcolor='#f1f5f9'),
        margin=dict(l=20, r=20, t=40, b=20),
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data available to display the trend.")

# 6. Comparative Context
with st.expander("ℹ️ How do these metrics compare to other outlets?"):
    st.write("""
    **2026 SciComm Benchmarks:**
    - **Substack:** A 44% open rate is the standard for high-intent research audiences.
    - **Bluesky:** Organic growth of +75/mo is top-tier for niche scientific accounts.
    - **CTR:** Anything above 3% indicates your audience is moving from "reading" to "acting."
    """)
