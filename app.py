import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(page_title="CZ-NoN Engagement Matrix", layout="wide")

# 2026 Industry Benchmarks
BENCHMARKS = {
    'substack_open_rate': 44.0,  # 44%
    'bs_growth_target': 75,       # 75 followers/mo
    'ctr_target': 3.2,            # 3.2%
}

# 2. Custom Styling
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.8rem; color: #1E3A8A; }
    .stMetric { background-color: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; }
    .benchmark-text { font-size: 0.8rem; color: #64748b; margin-top: -10px; }
    .comparison-box { background-color: #eff6ff; padding: 15px; border-radius: 8px; border-left: 5px solid #3b82f6; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Processing
@st.cache_data
def load_and_clean_data():
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

# 4. Header & Primary KPIs
st.title("🛰️ CZ-NoN engagement matrix")
st.markdown(f"[🦋 Bluesky](https://bsky.app/profile/cznews.bsky.social)  •  [✉️ Substack](https://criticalzonenews.substack.com/)")

k1, k2, k3, k4 = st.columns(4)

# Calculations for metrics and comparisons
# Bluesky
bs_f = df_f[df_f['Metric'] == 'followers']
curr_bs = bs_f['Value'].iloc[-1]
prev_bs = bs_f['Value'].iloc[-2] if len(bs_f) > 1 else curr_bs
actual_bs_growth = curr_bs - prev_bs

# Substack Open Rate Proxy (Reads / Followers)
ss_followers = df_f[df_f['Metric'] == 'total followers']['Value'].iloc[-1]
ss_reads_latest = df_f[df_f['Metric'] == 'monthly reads']['Value'].iloc[-1]
actual_open_rate = (ss_reads_latest / ss_followers * 100) if ss_followers > 0 else 0

# CTR
total_clicks = df_f[df_f['Metric'] == 'total clicks']['Value'].sum()
total_views = df_f[df_f['Metric'] == 'total views']['Value'].sum()
actual_ctr = (total_clicks / total_views * 100) if total_views > 0 else 0

# Display KPIs
k1.metric("Bluesky Followers", f"{curr_bs:,.0f}", f"{actual_bs_growth:+.0f} last mo")
k2.metric("Substack Total Reads", f"{df_f[df_f['Metric'] == 'monthly reads']['Value'].sum():,.0f}")
k3.metric("Bitly Clicks", f"{total_clicks:,.0f}", f"{actual_ctr:.1f}% CTR")
k4.metric("Avg Monthly Engagement Points", f"{df_f.groupby('Date')['Points'].sum().mean():.1f}")

# 5. NEW: Comparison Dropdown (Right below data cards)
with st.expander("📊 How do we compare? (Benchmark Analysis)", expanded=True):
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown(f"**Substack Engagement**")
        st.write(f"Actual: **{actual_open_rate:.1f}%** (Latest)")
        st.write(f"Benchmark: **{BENCHMARKS['substack_open_rate']}%**")
        status = "✅ Above" if actual_open_rate > BENCHMARKS['substack_open_rate'] else "⚠️ Below"
        st.caption(f"{status} Industry Average")

    with c2:
        st.markdown(f"**Bluesky Growth**")
        st.write(f"Actual: **+{actual_bs_growth}** followers/mo")
        st.write(f"Target: **+{BENCHMARKS['bs_growth_target']}** followers/mo")
        status = "✅ On Track" if actual_bs_growth >= BENCHMARKS['bs_growth_target'] else "📉 Under Target"
        st.caption(f"{status} for Niche SciComm")

    with c3:
        st.markdown(f"**Click-Through Rate (CTR)**")
        st.write(f"Actual: **{actual_ctr:.1f}%**")
        st.write(f"Target: **{BENCHMARKS['ctr_target']}%**")
        status = "✅ High Intent" if actual_ctr > BENCHMARKS['ctr_target'] else "ℹ️ Standard"
        st.caption(f"{status} Audience Action")

st.markdown("---")

# 6. Main Trend Graph
st.header("📈 Weighted Engagement Trend")
agg_trend = df_f.groupby('Date')['Points'].sum().reset_index()

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=agg_trend['Date'], y=agg_trend['Points'],
    mode='lines+markers',
    line=dict(color='#1E3A8A', width=4),
    marker=dict(size=12, color='#1E3A8A', line=dict(color='white', width=2)),
    name='Engagement Points',
    hovertemplate="<b>%{x|%B %Y}</b><br>Score: %{y:.1f} pts<extra></extra>"
))

# 2025 Baseline
baseline = agg_trend[agg_trend['Date'].dt.year == 2025]['Points'].mean()
if pd.notna(baseline):
    fig_trend.add_hline(y=baseline, line_dash="dot", line_color="#94a3b8", 
                        annotation_text="2025 Average Baseline", annotation_position="bottom right")

fig_trend.update_layout(plot_bgcolor='white', hovermode="x unified", height=400, margin=dict(t=20))
st.plotly_chart(fig_trend, use_container_width=True)

# 7. Restored Side-by-Side Charts
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🦋 Bluesky Follower Growth")
    bs_data = df_f[df_f['Platform'] == 'Bluesky']
    fig_bs = px.area(bs_data, x='Date', y='Value', 
                    color_discrete_sequence=['#8B5CF6'],
                    labels={'Value': 'Follower Count'})
    fig_bs.update_layout(plot_bgcolor='white', height=350)
    st.plotly_chart(fig_bs, use_container_width=True)

with col_right:
    st.subheader("✉️ Substack: Views vs. Actual Reads")
    ss_data = df_f[df_f['Platform'] == 'Substack']
    ss_pivot = ss_data.pivot(index='Date', columns='Metric', values='Value').reset_index()
    
    fig_ss = go.Figure()
    fig_ss.add_trace(go.Bar(x=ss_pivot['Date'], y=ss_pivot['total views'], name='Total Views', marker_color='#3B82F6'))
    fig_ss.add_trace(go.Bar(x=ss_pivot['Date'], y=ss_pivot['monthly reads'], name='Actual Reads', marker_color='#FF6719'))
    fig_ss.update_layout(barmode='group', plot_bgcolor='white', height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_ss, use_container_width=True)
